from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Literal, Mapping
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .cloudflare_provider_client import (
    CLOUDFLARE_GLM_MODEL_ID,
    CLOUDFLARE_NEMOTRON_MODEL_ID,
    CloudflareWorkersAIChatCompletionsDecisionClient,
)
from .cloudflare_provider_comparison_v2 import (
    ADR_018_GIT_BLOB,
    ADR_019_GIT_BLOB,
    CLOUDFLARE_CLIENT_GIT_BLOB,
    EXPECTED_PLAN_SHA256,
    GLM_CANDIDATE_ID,
    MAX_LIVE_ATTEMPTS_V2,
    MIN_FREE_NEURONS_BEFORE_ATTEMPT_1,
    NEMOTRON_CANDIDATE_ID,
    WORKERS_FREE_DAILY_NEURONS,
    CloudflareComparisonStopped,
    CloudflareProviderComparisonExecutorV2,
    CloudflareProviderComparisonPlan,
    FrozenCloudflareComparisonBundleV2,
    build_cloudflare_provider_comparison_plan_v2,
    load_frozen_cloudflare_comparison_bundle_v2,
)
from .decision_source import ProviderCallIdentity, ProviderDecisionSource, ProviderModelCallRecord
from .provider_clients import (
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderHttpResponse,
    ProviderJsonTransport,
    UrllibProviderJsonTransport,
)
from .provider_comparison import ProviderComparisonAttempt, controller_context_for_unit
from .runtime import canonical_tool_registry


CLOUDFLARE_LIVE_EXECUTION_VERSION = "cloudflare-live-execution-v2"
CLOUDFLARE_LIVE_TASK_VERSION = "cloudflare-live-task-v2"
CLOUDFLARE_CUSTODY_FILENAME = "cloudflare-adr018-live-comparison-custody-v2.json"
CANONICAL_RUN_DIRNAME = "run"
LEDGER_FILENAME = "attempt-ledger-v2.json"
RESULT_FILENAME = "result-v2.json"


class CloudflareLiveExecutionError(RuntimeError):
    """Base error for the v2 governed Cloudflare execution surface."""


class MissingCloudflareSecretsError(CloudflareLiveExecutionError):
    """Required Cloudflare secret values were not provisioned."""


class ExistingCloudflareRunError(CloudflareLiveExecutionError):
    """Durable run/custody evidence already exists."""


class CloudflareLiveExecutionInvariantError(CloudflareLiveExecutionError):
    """A v2 custody or resource invariant was violated."""


class CloudflareLiveExecutionStopped(CloudflareLiveExecutionError):
    """Execution stopped fail-closed after durable evidence was recorded."""


@dataclass(frozen=True, repr=False)
class CloudflareLiveSecrets:
    api_token: str
    account_id: str

    def __repr__(self) -> str:
        return "CloudflareLiveSecrets(api_token=<redacted>, account_id=<redacted>)"

    def validate_presence(self) -> None:
        missing: list[str] = []
        if not isinstance(self.api_token, str) or not self.api_token.strip():
            missing.append("CLOUDFLARE_API_TOKEN")
        if not isinstance(self.account_id, str) or not self.account_id.strip():
            missing.append("CLOUDFLARE_ACCOUNT_ID")
        if missing:
            raise MissingCloudflareSecretsError(
                "required execution values not provisioned: " + ",".join(missing)
            )


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CloudflarePreLiveEvidence(_FrozenModel):
    """Sanitized evidence supplied by a later authorization task; performs no probe."""

    schema_version: Literal["cloudflare-pre-live-evidence-v1"] = "cloudflare-pre-live-evidence-v1"
    workers_plan: Literal["Workers Free"] = "Workers Free"
    workers_paid_enabled: Literal[False] = False
    prepaid_ai_gateway_enabled: Literal[False] = False
    direct_workers_ai_route: Literal[True] = True
    actual_cash_cost_usd: Literal[0.0] = 0.0
    free_neurons_remaining: float = Field(ge=0, le=WORKERS_FREE_DAILY_NEURONS)
    utc_day: str = Field(min_length=10, max_length=10)
    evidence_source: str = Field(min_length=1, max_length=256)
    inference_used_to_obtain_evidence: Literal[False] = False
    credential_account_probe_used: Literal[False] = False

    @model_validator(mode="after")
    def validate_start_gate(self) -> "CloudflarePreLiveEvidence":
        if self.free_neurons_remaining < MIN_FREE_NEURONS_BEFORE_ATTEMPT_1:
            raise ValueError("at least 9000 free neurons are required before attempt 1")
        return self

    @property
    def zero_cash_route_proven(self) -> bool:
        return True

    @property
    def canonical_sha256(self) -> str:
        payload = self.model_dump(mode="json")
        data = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return sha256(data).hexdigest()


AttemptState = Literal["pending", "claimed", "completed", "uncertain"]
RunState = Literal["prepared", "running", "stopped", "complete"]


class CloudflareLiveAttemptLedgerEntryV2(_FrozenModel):
    attempt_index: int = Field(ge=0, lt=MAX_LIVE_ATTEMPTS_V2)
    candidate_id: str
    unit_id: str
    repeat_index: int = Field(ge=0, lt=2)
    state: AttemptState = "pending"
    attempt: dict[str, Any] | None = None
    stop_code: str | None = None

    @model_validator(mode="after")
    def validate_state_payload(self) -> "CloudflareLiveAttemptLedgerEntryV2":
        if self.state == "completed" and self.attempt is None:
            raise ValueError("completed ledger entry requires sanitized attempt evidence")
        if self.state != "completed" and self.attempt is not None:
            raise ValueError("only completed entries may contain attempt evidence")
        if self.state == "uncertain" and not self.stop_code:
            raise ValueError("uncertain entry requires stop_code")
        return self


class CloudflareLiveRunLedgerV2(_FrozenModel):
    schema_version: Literal["cloudflare-live-attempt-ledger-v2"] = (
        "cloudflare-live-attempt-ledger-v2"
    )
    wrapper_version: Literal["cloudflare-live-execution-v2"] = CLOUDFLARE_LIVE_EXECUTION_VERSION
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    design_blob: str = Field(pattern=r"^[0-9a-f]{40}$")
    population_blob: str = Field(pattern=r"^[0-9a-f]{40}$")
    adr_018_blob: str = Field(pattern=r"^[0-9a-f]{40}$")
    adr_019_blob: str = Field(pattern=r"^[0-9a-f]{40}$")
    cloudflare_client_blob: str = Field(pattern=r"^[0-9a-f]{40}$")
    pre_live_evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    available_free_neurons_at_start: float = Field(ge=MIN_FREE_NEURONS_BEFORE_ATTEMPT_1)
    state: RunState = "prepared"
    stop_code: str | None = None
    entries: tuple[CloudflareLiveAttemptLedgerEntryV2, ...]

    @model_validator(mode="after")
    def validate_geometry(self) -> "CloudflareLiveRunLedgerV2":
        if len(self.entries) != MAX_LIVE_ATTEMPTS_V2:
            raise ValueError("v2 live ledger must contain exactly 32 entries")
        if tuple(item.attempt_index for item in self.entries) != tuple(
            range(MAX_LIVE_ATTEMPTS_V2)
        ):
            raise ValueError("v2 ledger indexes must be canonical 0..31")
        if self.state == "complete" and any(item.state != "completed" for item in self.entries):
            raise ValueError("complete v2 ledger requires all attempts completed")
        if self.state == "stopped" and not self.stop_code:
            raise ValueError("stopped v2 ledger requires stop_code")
        return self


class CloudflareAuthorizationCustodyRecordV2(_FrozenModel):
    schema_version: Literal["cloudflare-live-authorization-custody-v2"] = (
        "cloudflare-live-authorization-custody-v2"
    )
    task_version: Literal["cloudflare-live-task-v2"] = CLOUDFLARE_LIVE_TASK_VERSION
    wrapper_version: Literal["cloudflare-live-execution-v2"] = CLOUDFLARE_LIVE_EXECUTION_VERSION
    adr_018_blob: Literal["e075ab4ff21904b9412769496dd2680c049cdaa8"] = ADR_018_GIT_BLOB
    adr_019_blob: Literal["b8f76831aceb13f5f3ffb5d7da0e12b595d9dd1a"] = ADR_019_GIT_BLOB
    cloudflare_client_blob: Literal["a5c814b519584b6d4346e3b0567bbc3da8ba0bf4"] = (
        CLOUDFLARE_CLIENT_GIT_BLOB
    )
    plan_sha256: Literal[
        "092e1e6070876f63388f4dd3e4bf47205db785f5f54e4676f3307992d81ac9cb"
    ] = EXPECTED_PLAN_SHA256
    pre_live_evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    available_free_neurons_at_reservation: float = Field(
        ge=MIN_FREE_NEURONS_BEFORE_ATTEMPT_1,
        le=WORKERS_FREE_DAILY_NEURONS,
    )
    canonical_run_dirname: Literal["run"] = CANONICAL_RUN_DIRNAME
    state: Literal["reserved"] = "reserved"
    live_calls_consumed_at_reservation: Literal[0] = 0
    credentials_recorded: Literal[False] = False
    raw_provider_material_recorded: Literal[False] = False
    workers_paid_enabled: Literal[False] = False
    prepaid_ai_gateway_enabled: Literal[False] = False
    workers_free_required: Literal[True] = True


class CloudflareGovernedExecutionResultV2(_FrozenModel):
    schema_version: Literal["cloudflare-governed-live-result-v2"] = (
        "cloudflare-governed-live-result-v2"
    )
    wrapper_version: Literal["cloudflare-live-execution-v2"] = CLOUDFLARE_LIVE_EXECUTION_VERSION
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    state: Literal["complete", "stopped"]
    completed_attempts: int = Field(ge=0, le=MAX_LIVE_ATTEMPTS_V2)
    consumed_or_uncertain_attempts: int = Field(ge=0, le=MAX_LIVE_ATTEMPTS_V2)
    stop_code: str | None = None
    selection: str
    provider_result: dict[str, Any] | None = None
    production_selection_claim: Literal[False] = False
    raw_provider_material_recorded: Literal[False] = False
    actual_cash_cost_usd: Literal[0.0] = 0.0


def build_cloudflare_live_clients_v2(
    *,
    secrets: CloudflareLiveSecrets,
    transport: ProviderJsonTransport,
) -> dict[str, CloudflareWorkersAIChatCompletionsDecisionClient]:
    secrets.validate_presence()
    return {
        GLM_CANDIDATE_ID: CloudflareWorkersAIChatCompletionsDecisionClient(
            api_token=secrets.api_token,
            account_id=secrets.account_id,
            model_id=CLOUDFLARE_GLM_MODEL_ID,
            transport=transport,
        ),
        NEMOTRON_CANDIDATE_ID: CloudflareWorkersAIChatCompletionsDecisionClient(
            api_token=secrets.api_token,
            account_id=secrets.account_id,
            model_id=CLOUDFLARE_NEMOTRON_MODEL_ID,
            transport=transport,
        ),
    }


def build_cloudflare_one_shot_transport_v2() -> UrllibProviderJsonTransport:
    """Construct the generic one-shot transport; construction performs no network I/O."""
    return UrllibProviderJsonTransport()


class _InjectedFailureTransport(ProviderJsonTransport):
    def __init__(self) -> None:
        self.calls = 0

    def post_json(self, request: ProviderHttpRequest) -> ProviderHttpResponse:
        self.calls += 1
        raise ProviderHttpClientError("INJECTED_PROVIDER_FREE_FAILURE")


def _fixed_failure_probe(model_id: str) -> bool:
    transport = _InjectedFailureTransport()
    client = CloudflareWorkersAIChatCompletionsDecisionClient(
        api_token="provider-free-injected-token",
        account_id="0123456789abcdef0123456789abcdef",
        model_id=model_id,
        transport=transport,
    )
    bundle = load_frozen_cloudflare_comparison_bundle_v2()
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


def run_cloudflare_provider_free_fixed_failure_probes_v2() -> dict[str, bool]:
    return {
        GLM_CANDIDATE_ID: _fixed_failure_probe(CLOUDFLARE_GLM_MODEL_ID),
        NEMOTRON_CANDIDATE_ID: _fixed_failure_probe(CLOUDFLARE_NEMOTRON_MODEL_ID),
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


def _write_result_once(run_dir: Path, result: CloudflareGovernedExecutionResultV2) -> None:
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
        raise ExistingCloudflareRunError("immutable Cloudflare v2 result already exists") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def _fsync_directory(path: Path) -> None:
    if os.name == "nt":
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class DurableCloudflareLiveRunLedgerV2:
    def __init__(self, *, path: Path, ledger: CloudflareLiveRunLedgerV2) -> None:
        self.path = path
        self.ledger = ledger

    @classmethod
    def create(
        cls,
        *,
        run_dir: Path,
        bundle: FrozenCloudflareComparisonBundleV2,
        plan: CloudflareProviderComparisonPlan,
        pre_live_evidence: CloudflarePreLiveEvidence,
    ) -> "DurableCloudflareLiveRunLedgerV2":
        run_dir.parent.mkdir(parents=True, exist_ok=True)
        try:
            run_dir.mkdir()
        except FileExistsError as exc:
            raise ExistingCloudflareRunError(
                "Cloudflare v2 run directory already exists; refusing resume or budget reset"
            ) from exc
        entries = tuple(
            CloudflareLiveAttemptLedgerEntryV2(
                attempt_index=item.attempt_index,
                candidate_id=item.candidate_id,
                unit_id=item.unit_id,
                repeat_index=item.repeat_index,
            )
            for item in plan.entries
        )
        ledger = CloudflareLiveRunLedgerV2(
            plan_sha256=plan.plan_sha256,
            design_blob=bundle.design_blob,
            population_blob=bundle.population_blob,
            adr_018_blob=bundle.adr_018_blob,
            adr_019_blob=bundle.adr_019_blob,
            cloudflare_client_blob=bundle.cloudflare_client_blob,
            pre_live_evidence_sha256=pre_live_evidence.canonical_sha256,
            available_free_neurons_at_start=pre_live_evidence.free_neurons_remaining,
            entries=entries,
        )
        path = run_dir / LEDGER_FILENAME
        _write_json_atomic(path, ledger.model_dump(mode="json"))
        return cls(path=path, ledger=ledger)

    def _replace_entry(
        self,
        index: int,
        replacement: CloudflareLiveAttemptLedgerEntryV2,
    ) -> None:
        entries = list(self.ledger.entries)
        entries[index] = replacement
        self.ledger = self.ledger.model_copy(update={"entries": tuple(entries)})

    def _persist(self) -> None:
        _write_json_atomic(self.path, self.ledger.model_dump(mode="json"))

    def claim(self, *, attempt_index: int) -> None:
        pending = [item.attempt_index for item in self.ledger.entries if item.state == "pending"]
        if not pending or attempt_index != min(pending):
            raise CloudflareLiveExecutionInvariantError(
                "attempt claim is not the next canonical pending index"
            )
        if any(item.state in {"claimed", "uncertain"} for item in self.ledger.entries):
            raise CloudflareLiveExecutionInvariantError(
                "existing claimed/uncertain evidence forbids another attempt"
            )
        current = self.ledger.entries[attempt_index]
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
            raise CloudflareLiveExecutionInvariantError(
                "completed attempt was not durably claimed first"
            )
        if (
            attempt.candidate_id != current.candidate_id
            or attempt.unit_id != current.unit_id
            or attempt.repeat_index != current.repeat_index
        ):
            raise CloudflareLiveExecutionInvariantError(
                "attempt evidence does not match canonical v2 ledger entry"
            )
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
            raise CloudflareLiveExecutionInvariantError(
                "only a claimed attempt can become uncertain"
            )
        self._replace_entry(
            attempt_index,
            current.model_copy(update={"state": "uncertain", "stop_code": stop_code}),
        )
        self.ledger = self.ledger.model_copy(
            update={"state": "stopped", "stop_code": stop_code}
        )
        self._persist()

    def stop_after_completed(self, *, stop_code: str) -> None:
        if any(item.state == "claimed" for item in self.ledger.entries):
            raise CloudflareLiveExecutionInvariantError(
                "cannot stop cleanly while an attempt remains claimed"
            )
        self.ledger = self.ledger.model_copy(
            update={"state": "stopped", "stop_code": stop_code}
        )
        self._persist()

    def mark_complete(self) -> None:
        if any(item.state != "completed" for item in self.ledger.entries):
            raise CloudflareLiveExecutionInvariantError(
                "cannot complete before all 32 attempts are recorded"
            )
        self.ledger = self.ledger.model_copy(update={"state": "complete", "stop_code": None})
        self._persist()

    @property
    def completed_attempts(self) -> int:
        return sum(item.state == "completed" for item in self.ledger.entries)

    @property
    def consumed_or_uncertain_attempts(self) -> int:
        return sum(
            item.state in {"claimed", "completed", "uncertain"}
            for item in self.ledger.entries
        )


def _reserve_authorization_custody_v2(
    *,
    custody_root: Path,
    record: CloudflareAuthorizationCustodyRecordV2,
) -> Path:
    custody_root.mkdir(parents=True, exist_ok=True)
    path = custody_root / CLOUDFLARE_CUSTODY_FILENAME
    data = json.dumps(
        record.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ) + "\n"
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ExistingCloudflareRunError(
            "Cloudflare ADR-018 custody already exists; refusing a second run or budget reset"
        ) from exc
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        _fsync_directory(custody_root)
    except Exception:
        raise
    return path


def _sanitized_exception_code(exc: Exception) -> str:
    if isinstance(exc, CloudflareLiveExecutionError):
        return type(exc).__name__.upper()
    return "EXECUTOR_INTERNAL_FAILURE"


@dataclass
class GovernedCloudflareProviderComparisonV2:
    run_dir: Path
    bundle: FrozenCloudflareComparisonBundleV2
    plan: CloudflareProviderComparisonPlan
    secrets: CloudflareLiveSecrets
    pre_live_evidence: CloudflarePreLiveEvidence
    transport: ProviderJsonTransport
    ledger: DurableCloudflareLiveRunLedgerV2
    fixture_result: bool

    @classmethod
    def prepare(
        cls,
        *,
        run_dir: Path | str,
        secrets: CloudflareLiveSecrets,
        pre_live_evidence: CloudflarePreLiveEvidence,
        transport: ProviderJsonTransport,
        fixture_result: bool,
        repo_root: Path | str = ".",
    ) -> "GovernedCloudflareProviderComparisonV2":
        secrets.validate_presence()
        bundle = load_frozen_cloudflare_comparison_bundle_v2(repo_root)
        plan = build_cloudflare_provider_comparison_plan_v2(bundle)
        if plan.plan_sha256 != EXPECTED_PLAN_SHA256:
            raise CloudflareLiveExecutionInvariantError("Cloudflare v2 plan SHA drift")
        path = Path(run_dir)
        ledger = DurableCloudflareLiveRunLedgerV2.create(
            run_dir=path,
            bundle=bundle,
            plan=plan,
            pre_live_evidence=pre_live_evidence,
        )
        return cls(
            run_dir=path,
            bundle=bundle,
            plan=plan,
            secrets=secrets,
            pre_live_evidence=pre_live_evidence,
            transport=transport,
            ledger=ledger,
            fixture_result=fixture_result,
        )

    def execute_all(self) -> CloudflareGovernedExecutionResultV2:
        fixed_probes = run_cloudflare_provider_free_fixed_failure_probes_v2()
        if not all(fixed_probes.values()):
            self.ledger.stop_after_completed(stop_code="FIXED_FAILURE_PROBE_FAILED")
            result = CloudflareGovernedExecutionResultV2(
                plan_sha256=self.plan.plan_sha256,
                state="stopped",
                completed_attempts=0,
                consumed_or_uncertain_attempts=0,
                stop_code="FIXED_FAILURE_PROBE_FAILED",
                selection="NO_SELECTION",
            )
            _write_result_once(self.run_dir, result)
            return result

        clients = build_cloudflare_live_clients_v2(
            secrets=self.secrets,
            transport=self.transport,
        )
        executor = CloudflareProviderComparisonExecutorV2(
            bundle=self.bundle,
            clients=clients,
            fixture_result=self.fixture_result,
            available_free_neurons=self.pre_live_evidence.free_neurons_remaining,
            zero_cash_cost_route_proven=self.pre_live_evidence.zero_cash_route_proven,
        )

        for entry in self.plan.entries:
            try:
                executor.assert_next_attempt_allowed()
            except CloudflareComparisonStopped:
                stop_code = executor.stop_reason or "RESOURCE_GUARD_STOP"
                self.ledger.stop_after_completed(stop_code=stop_code)
                provider_result = executor.finalize(
                    fixed_failure_probe_passed=fixed_probes
                )
                result = CloudflareGovernedExecutionResultV2(
                    plan_sha256=self.plan.plan_sha256,
                    state="stopped",
                    completed_attempts=self.ledger.completed_attempts,
                    consumed_or_uncertain_attempts=self.ledger.consumed_or_uncertain_attempts,
                    stop_code=stop_code,
                    selection="NO_SELECTION",
                    provider_result=provider_result.model_dump(mode="json"),
                )
                _write_result_once(self.run_dir, result)
                return result

            self.ledger.claim(attempt_index=entry.attempt_index)
            try:
                attempt = executor.execute_next()
            except Exception as exc:
                stop_code = _sanitized_exception_code(exc)
                self.ledger.mark_uncertain(
                    attempt_index=entry.attempt_index,
                    stop_code=stop_code,
                )
                result = CloudflareGovernedExecutionResultV2(
                    plan_sha256=self.plan.plan_sha256,
                    state="stopped",
                    completed_attempts=self.ledger.completed_attempts,
                    consumed_or_uncertain_attempts=self.ledger.consumed_or_uncertain_attempts,
                    stop_code=stop_code,
                    selection="NO_SELECTION",
                )
                _write_result_once(self.run_dir, result)
                raise CloudflareLiveExecutionStopped(stop_code) from None

            self.ledger.complete(attempt)
            if executor.stopped:
                stop_code = executor.stop_reason or "EXECUTOR_HARD_GATE_STOP"
                self.ledger.stop_after_completed(stop_code=stop_code)
                provider_result = executor.finalize(
                    fixed_failure_probe_passed=fixed_probes
                )
                result = CloudflareGovernedExecutionResultV2(
                    plan_sha256=self.plan.plan_sha256,
                    state="stopped",
                    completed_attempts=self.ledger.completed_attempts,
                    consumed_or_uncertain_attempts=self.ledger.consumed_or_uncertain_attempts,
                    stop_code=stop_code,
                    selection="NO_SELECTION",
                    provider_result=provider_result.model_dump(mode="json"),
                )
                _write_result_once(self.run_dir, result)
                return result

        provider_result = executor.finalize(fixed_failure_probe_passed=fixed_probes)
        self.ledger.mark_complete()
        result = CloudflareGovernedExecutionResultV2(
            plan_sha256=self.plan.plan_sha256,
            state="complete",
            completed_attempts=self.ledger.completed_attempts,
            consumed_or_uncertain_attempts=self.ledger.consumed_or_uncertain_attempts,
            selection=provider_result.selection,
            provider_result=provider_result.model_dump(mode="json"),
        )
        _write_result_once(self.run_dir, result)
        return result


@dataclass
class GovernedCloudflareLiveTaskV2:
    custody_root: Path
    custody_path: Path
    execution: GovernedCloudflareProviderComparisonV2

    @classmethod
    def prepare(
        cls,
        *,
        custody_root: Path | str,
        secrets: CloudflareLiveSecrets,
        pre_live_evidence: CloudflarePreLiveEvidence,
        transport: ProviderJsonTransport,
        fixture_result: bool,
        repo_root: Path | str = ".",
    ) -> "GovernedCloudflareLiveTaskV2":
        secrets.validate_presence()
        bundle = load_frozen_cloudflare_comparison_bundle_v2(repo_root)
        plan = build_cloudflare_provider_comparison_plan_v2(bundle)
        root = Path(custody_root)
        record = CloudflareAuthorizationCustodyRecordV2(
            pre_live_evidence_sha256=pre_live_evidence.canonical_sha256,
            available_free_neurons_at_reservation=pre_live_evidence.free_neurons_remaining,
        )
        custody_path = _reserve_authorization_custody_v2(
            custody_root=root,
            record=record,
        )
        execution = GovernedCloudflareProviderComparisonV2.prepare(
            run_dir=root / CANONICAL_RUN_DIRNAME,
            secrets=secrets,
            pre_live_evidence=pre_live_evidence,
            transport=transport,
            fixture_result=fixture_result,
            repo_root=repo_root,
        )
        if execution.plan.plan_sha256 != plan.plan_sha256:
            raise CloudflareLiveExecutionInvariantError(
                "custody and execution plan identities diverged"
            )
        return cls(
            custody_root=root,
            custody_path=custody_path,
            execution=execution,
        )

    def execute_all(self) -> CloudflareGovernedExecutionResultV2:
        return self.execution.execute_all()
