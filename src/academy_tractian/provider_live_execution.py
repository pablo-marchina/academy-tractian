from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any, Literal, Mapping, Type
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from research.e2.controller import ControllerDecisionKind

from .decision_source import (
    ProviderCallIdentity,
    ProviderDecisionSource,
    ProviderModelCallRecord,
)
from .provider_clients import (
    GoogleInteractionsDecisionClient,
    OpenAIResponsesDecisionClient,
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderHttpResponse,
    ProviderJsonTransport,
    UrllibProviderJsonTransport,
)
from .provider_comparison import (
    MAX_LIVE_ATTEMPTS,
    FrozenComparisonBundle,
    ProviderComparisonAttempt,
    ProviderComparisonExecutor,
    ProviderComparisonPlan,
    build_provider_comparison_plan,
    controller_context_for_unit,
    load_frozen_provider_comparison_bundle,
)
from .runtime import canonical_tool_registry


LIVE_PROVIDER_EXECUTION_VERSION = "provider-live-execution-v1"
EXPECTED_PLAN_SHA256 = "69691adff4af5c9d8928bf633089efdf4cd32c9419d10ae64b1a426df62c692f"
OPENAI_CANDIDATE_ID = "openai_gpt_5_6_sol_responses_standard"
GOOGLE_CANDIDATE_ID = "google_gemini_3_7_flash_interactions_stateless"
LEDGER_FILENAME = "attempt-ledger.json"
RESULT_FILENAME = "result.json"


class LiveExecutionError(RuntimeError):
    """Base error for the governed live-comparison execution surface."""


class MissingProviderSecretsError(LiveExecutionError):
    """Required secret values were not provisioned; no provider call is allowed."""


class ExistingLiveRunError(LiveExecutionError):
    """A run directory already exists and may contain consumed-call evidence."""


class LiveExecutionInvariantError(LiveExecutionError):
    """The live wrapper detected a frozen-plan or durable-ledger invariant violation."""


class LiveExecutionStopped(LiveExecutionError):
    """Execution stopped fail-closed after sanitized evidence was persisted."""


@dataclass(frozen=True, repr=False)
class LiveProviderSecrets:
    """Execution-owned secrets that are never serialized by this module."""

    openai_api_key: str
    google_api_key: str

    def __repr__(self) -> str:
        return "LiveProviderSecrets(openai_api_key=<redacted>, google_api_key=<redacted>)"

    def validate_presence(self) -> None:
        missing: list[str] = []
        if not isinstance(self.openai_api_key, str) or not self.openai_api_key.strip():
            missing.append("OPENAI_API_KEY")
        if not isinstance(self.google_api_key, str) or not self.google_api_key.strip():
            missing.append("GOOGLE_API_KEY")
        if missing:
            raise MissingProviderSecretsError(
                "required execution secrets not provisioned: " + ",".join(missing)
            )


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


AttemptState = Literal["pending", "claimed", "completed", "uncertain"]
RunState = Literal["prepared", "running", "stopped", "complete"]


class LiveAttemptLedgerEntry(_FrozenModel):
    attempt_index: int = Field(ge=0, lt=MAX_LIVE_ATTEMPTS)
    candidate_id: str
    unit_id: str
    repeat_index: int = Field(ge=0, lt=2)
    state: AttemptState = "pending"
    attempt: dict[str, Any] | None = None
    stop_code: str | None = None

    @model_validator(mode="after")
    def validate_state_payload(self) -> "LiveAttemptLedgerEntry":
        if self.state == "completed" and self.attempt is None:
            raise ValueError("completed ledger entry requires sanitized attempt evidence")
        if self.state != "completed" and self.attempt is not None:
            raise ValueError("only completed ledger entries may contain attempt evidence")
        if self.state == "uncertain" and not self.stop_code:
            raise ValueError("uncertain ledger entry requires stop_code")
        return self


class LiveRunLedger(_FrozenModel):
    schema_version: Literal["provider-live-attempt-ledger-v1"] = "provider-live-attempt-ledger-v1"
    wrapper_version: Literal["provider-live-execution-v1"] = LIVE_PROVIDER_EXECUTION_VERSION
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    design_blob: str = Field(pattern=r"^[0-9a-f]{40}$")
    population_blob: str = Field(pattern=r"^[0-9a-f]{40}$")
    authorization_blob: str = Field(pattern=r"^[0-9a-f]{40}$")
    adr_009_blob: str = Field(pattern=r"^[0-9a-f]{40}$")
    provider_clients_blob: str = Field(pattern=r"^[0-9a-f]{40}$")
    state: RunState = "prepared"
    stop_code: str | None = None
    entries: tuple[LiveAttemptLedgerEntry, ...]

    @model_validator(mode="after")
    def validate_geometry(self) -> "LiveRunLedger":
        if len(self.entries) != MAX_LIVE_ATTEMPTS:
            raise ValueError("live ledger must contain exactly 32 canonical attempts")
        if tuple(item.attempt_index for item in self.entries) != tuple(range(MAX_LIVE_ATTEMPTS)):
            raise ValueError("live ledger attempt indexes must be canonical 0..31")
        if self.state == "complete" and any(item.state != "completed" for item in self.entries):
            raise ValueError("complete live ledger requires all 32 completed attempts")
        if self.state == "stopped" and not self.stop_code:
            raise ValueError("stopped live ledger requires stop_code")
        return self


class LiveComparisonExecutionResult(_FrozenModel):
    schema_version: Literal["provider-live-execution-result-v1"] = "provider-live-execution-result-v1"
    wrapper_version: Literal["provider-live-execution-v1"] = LIVE_PROVIDER_EXECUTION_VERSION
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    state: Literal["complete", "stopped"]
    completed_attempts: int = Field(ge=0, le=MAX_LIVE_ATTEMPTS)
    consumed_or_uncertain_attempts: int = Field(ge=0, le=MAX_LIVE_ATTEMPTS)
    stop_code: str | None = None
    selection: str
    provider_result: dict[str, Any] | None = None
    production_selection_claim: Literal[False] = False
    raw_provider_material_recorded: Literal[False] = False


class DurableLiveRunLedger:
    """Atomic, write-ahead ledger for the non-resettable ADR-009 call budget.

    The wrapper intentionally does not support resume. If a process terminates after an attempt is
    durably claimed, a later process must treat the run directory as consumed evidence and stop.
    This prevents a crash from silently replaying a provider invocation or resetting the 32-call
    envelope.
    """

    def __init__(self, *, path: Path, ledger: LiveRunLedger) -> None:
        self.path = path
        self.ledger = ledger

    @classmethod
    def create(
        cls,
        *,
        run_dir: Path,
        bundle: FrozenComparisonBundle,
        plan: ProviderComparisonPlan,
    ) -> "DurableLiveRunLedger":
        parent = run_dir.parent
        parent.mkdir(parents=True, exist_ok=True)
        try:
            run_dir.mkdir()
        except FileExistsError as exc:
            raise ExistingLiveRunError(
                "live run directory already exists; refusing resume or budget reset"
            ) from exc

        entries = tuple(
            LiveAttemptLedgerEntry(
                attempt_index=item.attempt_index,
                candidate_id=item.candidate_id,
                unit_id=item.unit_id,
                repeat_index=item.repeat_index,
            )
            for item in plan.entries
        )
        ledger = LiveRunLedger(
            plan_sha256=plan.plan_sha256,
            design_blob=bundle.design_blob,
            population_blob=bundle.population_blob,
            authorization_blob=bundle.authorization_blob,
            adr_009_blob=bundle.adr_009_blob,
            provider_clients_blob=bundle.provider_clients_blob,
            entries=entries,
        )
        path = run_dir / LEDGER_FILENAME
        _write_json_atomic(path, ledger.model_dump(mode="json"))
        return cls(path=path, ledger=ledger)

    def _replace_entry(self, index: int, replacement: LiveAttemptLedgerEntry) -> None:
        entries = list(self.ledger.entries)
        entries[index] = replacement
        self.ledger = self.ledger.model_copy(update={"entries": tuple(entries)})

    def _persist(self) -> None:
        _write_json_atomic(self.path, self.ledger.model_dump(mode="json"))

    def claim(self, *, attempt_index: int) -> None:
        pending = [item.attempt_index for item in self.ledger.entries if item.state == "pending"]
        if not pending or attempt_index != min(pending):
            raise LiveExecutionInvariantError("attempt claim is not the next canonical pending index")
        if any(item.state in {"claimed", "uncertain"} for item in self.ledger.entries):
            raise LiveExecutionInvariantError("existing claimed/uncertain evidence forbids another attempt")

        current = self.ledger.entries[attempt_index]
        if current.state != "pending":
            raise LiveExecutionInvariantError("attempt is not pending")
        self._replace_entry(
            attempt_index,
            current.model_copy(update={"state": "claimed"}),
        )
        self.ledger = self.ledger.model_copy(update={"state": "running", "stop_code": None})
        self._persist()

    def complete(self, attempt: ProviderComparisonAttempt) -> None:
        index = attempt.attempt_index
        current = self.ledger.entries[index]
        if current.state != "claimed":
            raise LiveExecutionInvariantError("completed attempt was not durably claimed first")
        if (
            attempt.candidate_id != current.candidate_id
            or attempt.unit_id != current.unit_id
            or attempt.repeat_index != current.repeat_index
        ):
            raise LiveExecutionInvariantError("attempt evidence does not match canonical ledger entry")
        self._replace_entry(
            index,
            current.model_copy(
                update={
                    "state": "completed",
                    "attempt": attempt.model_dump(mode="json"),
                    "stop_code": None,
                }
            ),
        )
        self._persist()

    def mark_uncertain(self, *, attempt_index: int, stop_code: str) -> None:
        current = self.ledger.entries[attempt_index]
        if current.state != "claimed":
            raise LiveExecutionInvariantError("only a claimed attempt can become uncertain")
        self._replace_entry(
            attempt_index,
            current.model_copy(update={"state": "uncertain", "stop_code": stop_code}),
        )
        self.ledger = self.ledger.model_copy(update={"state": "stopped", "stop_code": stop_code})
        self._persist()

    def stop_after_completed(self, *, stop_code: str) -> None:
        if any(item.state == "claimed" for item in self.ledger.entries):
            raise LiveExecutionInvariantError("cannot stop cleanly while an attempt remains claimed")
        self.ledger = self.ledger.model_copy(update={"state": "stopped", "stop_code": stop_code})
        self._persist()

    def mark_complete(self) -> None:
        if any(item.state != "completed" for item in self.ledger.entries):
            raise LiveExecutionInvariantError("cannot complete before all 32 attempts are recorded")
        self.ledger = self.ledger.model_copy(update={"state": "complete", "stop_code": None})
        self._persist()

    @property
    def completed_attempts(self) -> int:
        return sum(item.state == "completed" for item in self.ledger.entries)

    @property
    def consumed_or_uncertain_attempts(self) -> int:
        return sum(item.state in {"claimed", "completed", "uncertain"} for item in self.ledger.entries)


class _InjectedFailureTransport(ProviderJsonTransport):
    """Provider-free local failure used only for the frozen M5 client failure probe."""

    def __init__(self) -> None:
        self.calls = 0

    def post_json(self, request: ProviderHttpRequest) -> ProviderHttpResponse:
        self.calls += 1
        raise ProviderHttpClientError("INJECTED_PROVIDER_FREE_FAILURE")


def _fixed_failure_probe_for_client(
    *,
    client_class: Type[OpenAIResponsesDecisionClient] | Type[GoogleInteractionsDecisionClient],
    bundle: FrozenComparisonBundle,
) -> bool:
    transport = _InjectedFailureTransport()
    client = client_class(
        api_key="provider-free-injected-secret",
        transport=transport,
    )
    context = controller_context_for_unit(bundle, bundle.population["units"][0]["unit_id"])
    source = ProviderDecisionSource(
        client=client,
        registry=canonical_tool_registry(),
        call_identity=ProviderCallIdentity(
            provider_id=client.provider_id,
            model_id=client.model_id,
            route_id=client.route_id,
            live_call=False,
        ),
    )
    try:
        source.decide(context)
    except ProviderHttpClientError:
        pass
    except Exception:
        return False
    else:
        return False

    records = source.drain_audit_records()
    if transport.calls != 1 or len(records) != 1:
        return False
    item = records[0]
    try:
        record = ProviderModelCallRecord.model_validate(
            {"call_id": item.call_id, **dict(item.metadata)}
        )
    except Exception:
        return False
    return bool(
        record.outcome == "failure"
        and record.failure_code == "CLIENT_FAILURE"
        and record.live_call is False
        and record.adapter_client_invocations == 1
        and record.adapter_retry_count == 0
        and record.adapter_fallback_used is False
        and record.raw_request_recorded is False
        and record.raw_response_recorded is False
        and record.exception_text_recorded is False
    )


def run_provider_free_fixed_failure_probes(
    bundle: FrozenComparisonBundle,
) -> dict[str, bool]:
    """Run the preregistered M5 fixed client-failure probes with zero network calls."""
    return {
        OPENAI_CANDIDATE_ID: _fixed_failure_probe_for_client(
            client_class=OpenAIResponsesDecisionClient,
            bundle=bundle,
        ),
        GOOGLE_CANDIDATE_ID: _fixed_failure_probe_for_client(
            client_class=GoogleInteractionsDecisionClient,
            bundle=bundle,
        ),
    }


def _build_exact_live_clients(
    secrets: LiveProviderSecrets,
) -> dict[str, OpenAIResponsesDecisionClient | GoogleInteractionsDecisionClient]:
    secrets.validate_presence()
    transport = UrllibProviderJsonTransport()
    return {
        OPENAI_CANDIDATE_ID: OpenAIResponsesDecisionClient(
            api_key=secrets.openai_api_key,
            transport=transport,
        ),
        GOOGLE_CANDIDATE_ID: GoogleInteractionsDecisionClient(
            api_key=secrets.google_api_key,
            transport=transport,
        ),
    }


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _write_result_once(run_dir: Path, result: LiveComparisonExecutionResult) -> None:
    path = run_dir / RESULT_FILENAME
    data = json.dumps(
        result.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ) + "\n"
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ExistingLiveRunError("immutable live result already exists") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def _sanitized_exception_code(exc: Exception) -> str:
    if isinstance(exc, LiveExecutionError):
        return type(exc).__name__.upper()
    return "EXECUTOR_INTERNAL_FAILURE"


@dataclass
class GovernedLiveProviderComparison:
    """Operational wrapper around the exact ADR-010 executor.

    Construction performs only local verification and object creation. `execute_all()` is the
    sole network-capable method and must be invoked only by a separately governed live task with
    explicit secret provisioning.
    """

    run_dir: Path
    bundle: FrozenComparisonBundle
    plan: ProviderComparisonPlan
    secrets: LiveProviderSecrets
    ledger: DurableLiveRunLedger

    @classmethod
    def prepare(
        cls,
        *,
        run_dir: Path | str,
        secrets: LiveProviderSecrets,
        repo_root: Path | str = ".",
    ) -> "GovernedLiveProviderComparison":
        # Secret presence is a local check only. No account/capability request is made.
        secrets.validate_presence()
        bundle = load_frozen_provider_comparison_bundle(repo_root)
        plan = build_provider_comparison_plan(bundle)
        if plan.plan_sha256 != EXPECTED_PLAN_SHA256:
            raise LiveExecutionInvariantError("canonical ADR-010 plan SHA-256 drift")
        path = Path(run_dir)
        ledger = DurableLiveRunLedger.create(run_dir=path, bundle=bundle, plan=plan)
        return cls(
            run_dir=path,
            bundle=bundle,
            plan=plan,
            secrets=secrets,
            ledger=ledger,
        )

    def execute_all(self) -> LiveComparisonExecutionResult:
        """Consume the exact live envelope once; never retry or resume consumed attempts."""
        fixed_failure_probe_passed = run_provider_free_fixed_failure_probes(self.bundle)
        if not all(fixed_failure_probe_passed.values()):
            self.ledger.stop_after_completed(stop_code="FIXED_FAILURE_PROBE_FAILED")
            result = LiveComparisonExecutionResult(
                plan_sha256=self.plan.plan_sha256,
                state="stopped",
                completed_attempts=0,
                consumed_or_uncertain_attempts=0,
                stop_code="FIXED_FAILURE_PROBE_FAILED",
                selection="NO_SELECTION",
            )
            _write_result_once(self.run_dir, result)
            return result

        clients = _build_exact_live_clients(self.secrets)
        executor = ProviderComparisonExecutor(
            bundle=self.bundle,
            clients=clients,
            fixture_result=False,
        )

        for entry in self.plan.entries:
            # The claim is fsync'd before ProviderComparisonExecutor reaches its network-capable
            # client invocation. A crash after this point makes the attempt consumed/uncertain and
            # the existing run directory intentionally cannot be resumed.
            self.ledger.claim(attempt_index=entry.attempt_index)
            try:
                attempt = executor.execute_next()
            except Exception as exc:
                stop_code = _sanitized_exception_code(exc)
                self.ledger.mark_uncertain(
                    attempt_index=entry.attempt_index,
                    stop_code=stop_code,
                )
                result = LiveComparisonExecutionResult(
                    plan_sha256=self.plan.plan_sha256,
                    state="stopped",
                    completed_attempts=self.ledger.completed_attempts,
                    consumed_or_uncertain_attempts=self.ledger.consumed_or_uncertain_attempts,
                    stop_code=stop_code,
                    selection="NO_SELECTION",
                )
                _write_result_once(self.run_dir, result)
                raise LiveExecutionStopped(stop_code) from None

            self.ledger.complete(attempt)
            if executor.stopped:
                stop_code = executor.stop_reason or "EXECUTOR_HARD_GATE_STOP"
                self.ledger.stop_after_completed(stop_code=stop_code)
                provider_result = executor.finalize(
                    fixed_failure_probe_passed=fixed_failure_probe_passed,
                )
                result = LiveComparisonExecutionResult(
                    plan_sha256=self.plan.plan_sha256,
                    state="stopped",
                    completed_attempts=self.ledger.completed_attempts,
                    consumed_or_uncertain_attempts=self.ledger.consumed_or_uncertain_attempts,
                    stop_code=stop_code,
                    selection=provider_result.selection,
                    provider_result=provider_result.model_dump(mode="json"),
                )
                _write_result_once(self.run_dir, result)
                return result

        provider_result = executor.finalize(
            fixed_failure_probe_passed=fixed_failure_probe_passed,
        )
        self.ledger.mark_complete()
        result = LiveComparisonExecutionResult(
            plan_sha256=self.plan.plan_sha256,
            state="complete",
            completed_attempts=self.ledger.completed_attempts,
            consumed_or_uncertain_attempts=self.ledger.consumed_or_uncertain_attempts,
            selection=provider_result.selection,
            provider_result=provider_result.model_dump(mode="json"),
        )
        _write_result_once(self.run_dir, result)
        return result
