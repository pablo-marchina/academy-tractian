from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Mapping, Protocol
import urllib.error
import urllib.request

from .decision_source import ProviderDecisionRequest


PROVIDER_HTTP_CLIENTS_VERSION = "provider-http-clients-v1"
OPENAI_PROVIDER_ID = "openai"
OPENAI_MODEL_ID = "gpt-5.6-sol"
OPENAI_ROUTE_ID = "openai.responses.v1.standard"
OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"
GOOGLE_PROVIDER_ID = "google"
GOOGLE_MODEL_ID = "gemini-3.7-flash"
GOOGLE_ROUTE_ID = "google.interactions.v1beta.stateless"
GOOGLE_INTERACTIONS_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"

PROVIDER_DECISION_SYSTEM_INSTRUCTION = """
You are the decision source for an application-owned industrial-maintenance agent controller.
Return exactly one JSON object matching the supplied ProviderDecisionPayload schema.
You may propose one canonical public tool by returning kind=TOOL, but you never execute tools.
The application owns the agent loop, runtime binding/control state, tool execution, and evaluation.
Never invent or request access to hidden evaluator truth, credentials, runtime authorization state, or private state.
Choose FINAL, CLARIFY, ESCALATE, or ABSTAIN when a tool proposal is not the correct next controller decision.
Do not wrap the JSON object in Markdown or explanatory text.
""".strip()

# The provider API constrains top-level shape; ADR-006 ProviderDecisionPayload remains the
# authoritative strict relational validator. `arguments` and `final` intentionally remain
# open JSON objects because their canonical semantics are owned downstream by B1 / the
# production response contract rather than duplicated in provider-specific code.
PROVIDER_DECISION_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "schema_version": {
            "type": "string",
            "enum": ["provider-decision-payload-v1"],
        },
        "kind": {
            "type": "string",
            "enum": ["TOOL", "FINAL", "CLARIFY", "ESCALATE", "ABSTAIN"],
        },
        "tool_name": {"type": ["string", "null"]},
        "arguments": {"type": "object"},
        "evidence_id": {"type": ["string", "null"]},
        "final": {"type": ["object", "null"]},
        "message": {"type": ["string", "null"]},
        "reason_code": {"type": ["string", "null"]},
    },
    "required": [
        "schema_version",
        "kind",
        "tool_name",
        "arguments",
        "evidence_id",
        "final",
        "message",
        "reason_code",
    ],
}


class ProviderHttpClientError(RuntimeError):
    """Sanitized provider-client failure safe to cross into the fail-closed adapter path."""

    def __init__(self, code: str, *, status_code: int | None = None) -> None:
        self.code = code
        self.status_code = status_code
        message = code if status_code is None else f"{code}:{status_code}"
        super().__init__(message)


@dataclass(frozen=True)
class ProviderHttpRequest:
    method: str
    url: str
    headers: Mapping[str, str] = field(repr=False)
    body: Mapping[str, Any]
    timeout_seconds: float

    def __repr__(self) -> str:
        return (
            "ProviderHttpRequest("
            f"method={self.method!r}, url={self.url!r}, headers=<redacted>, "
            f"body={self.body!r}, timeout_seconds={self.timeout_seconds!r})"
        )


@dataclass(frozen=True)
class ProviderHttpResponse:
    status_code: int
    body: Mapping[str, Any]


class ProviderJsonTransport(Protocol):
    def post_json(self, request: ProviderHttpRequest) -> ProviderHttpResponse: ...


class UrllibProviderJsonTransport:
    """One-shot stdlib JSON transport. It has no retry, fallback, or credential lookup."""

    def post_json(self, request: ProviderHttpRequest) -> ProviderHttpResponse:
        if request.method != "POST":
            raise ProviderHttpClientError("METHOD_NOT_ALLOWED")
        try:
            encoded = json.dumps(
                request.body,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            raw_request = urllib.request.Request(
                request.url,
                data=encoded,
                headers=dict(request.headers),
                method="POST",
            )
            with urllib.request.urlopen(raw_request, timeout=request.timeout_seconds) as response:
                status_code = int(response.status)
                raw_body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise ProviderHttpClientError("HTTP_STATUS", status_code=int(exc.code)) from None
        except ProviderHttpClientError:
            raise
        except Exception:
            raise ProviderHttpClientError("TRANSPORT_FAILURE") from None

        if status_code < 200 or status_code >= 300:
            raise ProviderHttpClientError("HTTP_STATUS", status_code=status_code)
        try:
            payload = json.loads(raw_body)
        except Exception:
            raise ProviderHttpClientError("HTTP_JSON_INVALID") from None
        if not isinstance(payload, dict):
            raise ProviderHttpClientError("HTTP_JSON_NOT_OBJECT")
        return ProviderHttpResponse(status_code=status_code, body=payload)


@dataclass(frozen=True)
class ProviderUsageRecord:
    provider_id: str
    model_id: str
    route_id: str
    request_sha256: str
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    reasoning_tokens: int | None = None


class _BaseProviderDecisionClient:
    provider_id: str
    model_id: str
    route_id: str

    def __init__(
        self,
        *,
        api_key: str,
        transport: ProviderJsonTransport,
        timeout_seconds: float = 60.0,
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("provider client requires an explicit non-empty api_key")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._api_key = api_key
        self._transport = transport
        self._timeout_seconds = float(timeout_seconds)
        self._usage_records: list[ProviderUsageRecord] = []

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(provider_id={self.provider_id!r}, "
            f"model_id={self.model_id!r}, route_id={self.route_id!r}, api_key=<redacted>)"
        )

    def drain_usage_records(self) -> tuple[ProviderUsageRecord, ...]:
        records = tuple(self._usage_records)
        self._usage_records.clear()
        return records

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

    def _record_usage(
        self,
        *,
        request: ProviderDecisionRequest,
        input_tokens: Any,
        output_tokens: Any,
        total_tokens: Any,
        reasoning_tokens: Any = None,
    ) -> None:
        self._usage_records.append(
            ProviderUsageRecord(
                provider_id=self.provider_id,
                model_id=self.model_id,
                route_id=self.route_id,
                request_sha256=request.request_sha256,
                input_tokens=_nonnegative_int_or_none(input_tokens),
                output_tokens=_nonnegative_int_or_none(output_tokens),
                total_tokens=_nonnegative_int_or_none(total_tokens),
                reasoning_tokens=_nonnegative_int_or_none(reasoning_tokens),
            )
        )


def _nonnegative_int_or_none(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _provider_request_text(request: ProviderDecisionRequest) -> str:
    return json.dumps(
        request.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _schema_copy() -> dict[str, Any]:
    return json.loads(json.dumps(PROVIDER_DECISION_JSON_SCHEMA))


class OpenAIResponsesDecisionClient(_BaseProviderDecisionClient):
    provider_id = OPENAI_PROVIDER_ID
    model_id = OPENAI_MODEL_ID
    route_id = OPENAI_ROUTE_ID

    def build_http_request(self, request: ProviderDecisionRequest) -> ProviderHttpRequest:
        body: dict[str, Any] = {
            "model": self.model_id,
            "store": False,
            "background": False,
            "reasoning": {"effort": "medium"},
            "instructions": PROVIDER_DECISION_SYSTEM_INSTRUCTION,
            "input": _provider_request_text(request),
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "provider_decision_payload",
                    "schema": _schema_copy(),
                    # ADR-006 remains the strict relational validator. The provider schema
                    # intentionally leaves nested argument/final objects open.
                    "strict": False,
                }
            },
        }
        return ProviderHttpRequest(
            method="POST",
            url=OPENAI_RESPONSES_ENDPOINT,
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
        output_details = usage_map.get("output_tokens_details")
        output_details_map = output_details if isinstance(output_details, Mapping) else {}
        self._record_usage(
            request=request,
            input_tokens=usage_map.get("input_tokens"),
            output_tokens=usage_map.get("output_tokens"),
            total_tokens=usage_map.get("total_tokens"),
            reasoning_tokens=output_details_map.get("reasoning_tokens"),
        )
        return _extract_openai_output(response)


class GoogleInteractionsDecisionClient(_BaseProviderDecisionClient):
    provider_id = GOOGLE_PROVIDER_ID
    model_id = GOOGLE_MODEL_ID
    route_id = GOOGLE_ROUTE_ID

    def build_http_request(self, request: ProviderDecisionRequest) -> ProviderHttpRequest:
        body: dict[str, Any] = {
            "model": self.model_id,
            "store": False,
            "background": False,
            "system_instruction": PROVIDER_DECISION_SYSTEM_INSTRUCTION,
            "input": _provider_request_text(request),
            "response_format": {
                "type": "text",
                "mime_type": "application/json",
                "schema": _schema_copy(),
            },
            "generation_config": {
                "thinking_level": "medium",
                "thinking_summaries": "none",
                "tool_choice": "none",
            },
        }
        return ProviderHttpRequest(
            method="POST",
            url=GOOGLE_INTERACTIONS_ENDPOINT,
            headers={
                "x-goog-api-key": self._api_key,
                "Content-Type": "application/json",
            },
            body=body,
            timeout_seconds=self._timeout_seconds,
        )

    def complete(self, request: ProviderDecisionRequest) -> str:
        response = self._invoke_once(self.build_http_request(request))
        usage = response.get("usage")
        usage_map = usage if isinstance(usage, Mapping) else {}
        self._record_usage(
            request=request,
            input_tokens=usage_map.get("total_input_tokens"),
            output_tokens=usage_map.get("total_output_tokens"),
            total_tokens=usage_map.get("total_tokens"),
            reasoning_tokens=usage_map.get("total_thought_tokens"),
        )
        return _extract_google_output(response)


def _extract_openai_output(response: Mapping[str, Any]) -> str:
    if response.get("object") != "response":
        raise ProviderHttpClientError("OPENAI_OBJECT_INVALID")
    if response.get("status") != "completed":
        raise ProviderHttpClientError("OPENAI_STATUS_NOT_COMPLETED")
    if response.get("model") != OPENAI_MODEL_ID:
        raise ProviderHttpClientError("OPENAI_MODEL_MISMATCH")
    output = response.get("output")
    if not isinstance(output, list):
        raise ProviderHttpClientError("OPENAI_OUTPUT_INVALID")

    texts: list[str] = []
    for item in output:
        if not isinstance(item, Mapping):
            raise ProviderHttpClientError("OPENAI_OUTPUT_ITEM_INVALID")
        item_type = item.get("type")
        if item_type == "reasoning":
            continue
        if item_type != "message":
            raise ProviderHttpClientError("OPENAI_UNEXPECTED_OUTPUT_ITEM")
        if item.get("status") not in (None, "completed"):
            raise ProviderHttpClientError("OPENAI_MESSAGE_NOT_COMPLETED")
        content = item.get("content")
        if not isinstance(content, list):
            raise ProviderHttpClientError("OPENAI_CONTENT_INVALID")
        for part in content:
            if not isinstance(part, Mapping) or part.get("type") != "output_text":
                raise ProviderHttpClientError("OPENAI_UNEXPECTED_CONTENT")
            text = part.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ProviderHttpClientError("OPENAI_OUTPUT_TEXT_INVALID")
            texts.append(text)

    if len(texts) != 1:
        raise ProviderHttpClientError("OPENAI_OUTPUT_TEXT_COUNT")
    return texts[0]


def _extract_google_output(response: Mapping[str, Any]) -> str:
    if response.get("object") != "interaction":
        raise ProviderHttpClientError("GOOGLE_OBJECT_INVALID")
    if response.get("status") != "completed":
        raise ProviderHttpClientError("GOOGLE_STATUS_NOT_COMPLETED")
    if response.get("model") != GOOGLE_MODEL_ID:
        raise ProviderHttpClientError("GOOGLE_MODEL_MISMATCH")
    steps = response.get("steps")
    if not isinstance(steps, list):
        raise ProviderHttpClientError("GOOGLE_STEPS_INVALID")

    texts: list[str] = []
    for step in steps:
        if not isinstance(step, Mapping):
            raise ProviderHttpClientError("GOOGLE_STEP_INVALID")
        step_type = step.get("type")
        if step_type == "thought":
            continue
        if step_type != "model_output":
            raise ProviderHttpClientError("GOOGLE_UNEXPECTED_STEP")
        content = step.get("content")
        if not isinstance(content, list):
            raise ProviderHttpClientError("GOOGLE_CONTENT_INVALID")
        for part in content:
            if not isinstance(part, Mapping) or part.get("type") != "text":
                raise ProviderHttpClientError("GOOGLE_UNEXPECTED_CONTENT")
            text = part.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ProviderHttpClientError("GOOGLE_OUTPUT_TEXT_INVALID")
            texts.append(text)

    if len(texts) != 1:
        raise ProviderHttpClientError("GOOGLE_OUTPUT_TEXT_COUNT")
    return texts[0]
