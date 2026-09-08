from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Mapping

from research.e2.controller import ControllerContext

from .decision_source import (
    ProviderCallIdentity,
    ProviderDecisionRequest,
    ProviderDecisionSource,
    ProviderModelCallRecord,
)
from .provider_clients import (
    PROVIDER_DECISION_JSON_SCHEMA,
    PROVIDER_DECISION_SYSTEM_INSTRUCTION,
    ProviderHttpClientError,
    ProviderHttpRequest,
    ProviderHttpResponse,
    ProviderJsonTransport,
    ProviderUsageRecord,
)
from .runtime import canonical_tool_registry


MAX_INPUT_TOKENS = 8000
MAX_OUTPUT_TOKENS = 512


@dataclass(frozen=True)
class HostedRouteCandidateV2:
    candidate_id: str
    provider_id: str
    model_id: str
    route_id: str
    endpoint: str
    max_token_field: str = "max_tokens"
    openrouter_no_fallback: bool = False
    acceptable_response_model_ids: tuple[str, ...] = ()

    def accepts_response_model(self, value: object) -> bool:
        if not isinstance(value, str) or not value:
            return False
        allowed = self.acceptable_response_model_ids or (self.model_id,)
        return value in allowed


def groq_candidate(model_id: str) -> HostedRouteCandidateV2:
    return HostedRouteCandidateV2(
        candidate_id=f"groq:{model_id}",
        provider_id="groq",
        model_id=model_id,
        route_id="groq.openai_compat.chat_completions.v1.json_schema",
        endpoint="https://api.groq.com/openai/v1/chat/completions",
        max_token_field="max_completion_tokens",
    )


NVIDIA_CANDIDATE = HostedRouteCandidateV2(
    candidate_id="nvidia:nvidia/nemotron-3-super-120b-a12b",
    provider_id="nvidia",
    model_id="nvidia/nemotron-3-super-120b-a12b",
    route_id="nvidia.integrate.chat_completions.v1.json_schema",
    endpoint="https://integrate.api.nvidia.com/v1/chat/completions",
)

OPENROUTER_CANDIDATE = HostedRouteCandidateV2(
    candidate_id="openrouter:nvidia/nemotron-3-super-120b-a12b:free",
    provider_id="openrouter",
    model_id="nvidia/nemotron-3-super-120b-a12b:free",
    route_id="openrouter.chat_completions.v1.free.json_schema.no_fallback",
    endpoint="https://openrouter.ai/api/v1/chat/completions",
    openrouter_no_fallback=True,
    acceptable_response_model_ids=(
        "nvidia/nemotron-3-super-120b-a12b:free",
        "nvidia/nemotron-3-super-120b-a12b",
    ),
)


def _provider_request_text(request: ProviderDecisionRequest) -> str:
    return json.dumps(
        request.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _schema_envelope() -> dict[str, Any]:
    return {
        "name": "provider_decision_payload",
        "strict": False,
        "schema": json.loads(json.dumps(PROVIDER_DECISION_JSON_SCHEMA)),
    }


def _nonnegative_int_or_none(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


class HostedOpenAICompatibleDecisionClientV2:
    """Provider-neutral one-shot route used by DP-006.

    There is intentionally no retry, model fallback, JSON repair, provider-side state, web
    search or native tool execution. Strict parsing remains owned by ProviderDecisionSource.
    """

    def __init__(
        self,
        *,
        candidate: HostedRouteCandidateV2,
        api_key: str,
        transport: ProviderJsonTransport,
        timeout_seconds: float = 60.0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("DP-006 hosted client requires a non-empty explicit api_key")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.candidate = candidate
        self._api_key = api_key
        self._transport = transport
        self._timeout_seconds = float(timeout_seconds)
        self._usage_records: list[ProviderUsageRecord] = []

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(candidate_id={self.candidate.candidate_id!r}, "
            f"provider_id={self.candidate.provider_id!r}, model_id={self.candidate.model_id!r}, "
            "api_key=<redacted>)"
        )

    def drain_usage_records(self) -> tuple[ProviderUsageRecord, ...]:
        records = tuple(self._usage_records)
        self._usage_records.clear()
        return records

    def build_http_request(self, request: ProviderDecisionRequest) -> ProviderHttpRequest:
        body: dict[str, Any] = {
            "model": self.candidate.model_id,
            "messages": [
                {"role": "system", "content": PROVIDER_DECISION_SYSTEM_INSTRUCTION},
                {"role": "user", "content": _provider_request_text(request)},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": _schema_envelope(),
            },
            "temperature": 0,
            "n": 1,
            "stream": False,
            self.candidate.max_token_field: MAX_OUTPUT_TOKENS,
        }
        if self.candidate.openrouter_no_fallback:
            body["provider"] = {
                "allow_fallbacks": False,
                "require_parameters": True,
            }
        return ProviderHttpRequest(
            method="POST",
            url=self.candidate.endpoint,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            body=body,
            timeout_seconds=self._timeout_seconds,
        )

    def complete(self, request: ProviderDecisionRequest) -> str:
        response = self._invoke_once(self.build_http_request(request))
        usage = response.get("usage")
        usage_map = usage if isinstance(usage, Mapping) else {}
        details = usage_map.get("completion_tokens_details")
        details_map = details if isinstance(details, Mapping) else {}
        input_tokens = usage_map.get("prompt_tokens", usage_map.get("input_tokens"))
        output_tokens = usage_map.get("completion_tokens", usage_map.get("output_tokens"))
        total_tokens = usage_map.get("total_tokens")
        self._usage_records.append(
            ProviderUsageRecord(
                provider_id=self.candidate.provider_id,
                model_id=self.candidate.model_id,
                route_id=self.candidate.route_id,
                request_sha256=request.request_sha256,
                input_tokens=_nonnegative_int_or_none(input_tokens),
                output_tokens=_nonnegative_int_or_none(output_tokens),
                total_tokens=_nonnegative_int_or_none(total_tokens),
                reasoning_tokens=_nonnegative_int_or_none(details_map.get("reasoning_tokens")),
            )
        )
        return self._extract_output(response)

    def _invoke_once(self, request: ProviderHttpRequest) -> Mapping[str, Any]:
        try:
            response = self._transport.post_json(request)
        except ProviderHttpClientError:
            raise
        except Exception:
            raise ProviderHttpClientError("TRANSPORT_FAILURE") from None
        if not isinstance(response, ProviderHttpResponse):
            raise ProviderHttpClientError("TRANSPORT_RESPONSE_INVALID")
        if response.status_code < 200 or response.status_code >= 300:
            raise ProviderHttpClientError("HTTP_STATUS", status_code=response.status_code)
        if not isinstance(response.body, Mapping):
            raise ProviderHttpClientError("HTTP_JSON_NOT_OBJECT")
        return response.body

    def _extract_output(self, response: Mapping[str, Any]) -> str:
        if response.get("object") not in (None, "chat.completion"):
            raise ProviderHttpClientError("CHAT_COMPLETION_OBJECT_INVALID")
        if not self.candidate.accepts_response_model(response.get("model")):
            raise ProviderHttpClientError("MODEL_IDENTITY_MISMATCH")
        choices = response.get("choices")
        if not isinstance(choices, list) or len(choices) != 1:
            raise ProviderHttpClientError("CHAT_COMPLETION_CHOICES_INVALID")
        choice = choices[0]
        if not isinstance(choice, Mapping):
            raise ProviderHttpClientError("CHAT_COMPLETION_CHOICE_INVALID")
        if choice.get("index") not in (None, 0):
            raise ProviderHttpClientError("CHAT_COMPLETION_CHOICE_INDEX_INVALID")
        if choice.get("finish_reason") != "stop":
            raise ProviderHttpClientError("CHAT_COMPLETION_FINISH_REASON_INVALID")
        message = choice.get("message")
        if not isinstance(message, Mapping):
            raise ProviderHttpClientError("CHAT_COMPLETION_MESSAGE_INVALID")
        if message.get("role") not in (None, "assistant"):
            raise ProviderHttpClientError("CHAT_COMPLETION_ROLE_INVALID")
        if message.get("tool_calls") not in (None, []):
            raise ProviderHttpClientError("PROVIDER_NATIVE_TOOL_CALL_REJECTED")
        if message.get("function_call") is not None:
            raise ProviderHttpClientError("PROVIDER_NATIVE_FUNCTION_CALL_REJECTED")
        if message.get("refusal") not in (None, ""):
            raise ProviderHttpClientError("PROVIDER_REFUSAL_REJECTED")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ProviderHttpClientError("CHAT_COMPLETION_OUTPUT_TEXT_INVALID")
        return content


def run_synthetic_eligibility_probe(
    *,
    candidate: HostedRouteCandidateV2,
    api_key: str,
    transport: ProviderJsonTransport,
) -> dict[str, Any]:
    client = HostedOpenAICompatibleDecisionClientV2(
        candidate=candidate,
        api_key=api_key,
        transport=transport,
    )
    source = ProviderDecisionSource(
        client=client,
        registry=canonical_tool_registry(),
        call_identity=ProviderCallIdentity(
            provider_id=candidate.provider_id,
            model_id=candidate.model_id,
            route_id=candidate.route_id,
            live_call=True,
        ),
    )
    context = ControllerContext(
        user_request=(
            "I need maintenance help, but I have not identified the equipment or asset yet. "
            "Choose the correct next controller decision. Do not execute tools."
        ),
        turn_index=0,
        tool_call_count=0,
        observations=(),
    )
    failure_code: str | None = None
    decision_kind: str | None = None
    try:
        decision = source.decide(context)
        decision_kind = decision.kind.value
    except ProviderHttpClientError as exc:
        failure_code = f"{exc.code}:{exc.status_code}" if exc.status_code is not None else exc.code
    except Exception as exc:
        failure_code = type(exc).__name__

    audits = source.drain_audit_records()
    audit_ok = False
    latency_ms: int | None = None
    if len(audits) == 1:
        try:
            record = ProviderModelCallRecord.from_trace_event(
                call_id=audits[0].call_id,
                metadata=dict(audits[0].metadata),
            )
            audit_ok = (
                record.provider_id == candidate.provider_id
                and record.model_id == candidate.model_id
                and record.route_id == candidate.route_id
                and record.live_call is True
                and record.adapter_client_invocations == 1
                and record.adapter_retry_count == 0
                and record.adapter_fallback_used is False
                and record.raw_request_recorded is False
                and record.raw_response_recorded is False
            )
            latency_ms = record.latency_ms
        except Exception:
            audit_ok = False

    usages = client.drain_usage_records()
    usage_ok = (
        len(usages) == 1
        and usages[0].input_tokens is not None
        and usages[0].output_tokens is not None
        and usages[0].input_tokens <= MAX_INPUT_TOKENS
        and usages[0].output_tokens <= MAX_OUTPUT_TOKENS
    )
    passed = failure_code is None and decision_kind is not None and audit_ok and usage_ok
    return {
        "candidate_id": candidate.candidate_id,
        "provider_id": candidate.provider_id,
        "model_id": candidate.model_id,
        "passed": passed,
        "decision_kind": decision_kind,
        "failure_code": failure_code,
        "audit_integrity": audit_ok,
        "usage_accounted_and_within_ceiling": usage_ok,
        "latency_ms": latency_ms,
        "automatic_retry_count": 0,
        "automatic_fallback_count": 0,
        "raw_provider_material_recorded": False,
    }
