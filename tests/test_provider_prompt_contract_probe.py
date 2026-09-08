from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "scripts" / "verification" / "provider_prompt_contract_probe.py"


def _load_probe():
    spec = importlib.util.spec_from_file_location("provider_prompt_contract_probe", PROBE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_probe_never_imports_frozen_tournament_or_benchmark_population() -> None:
    source = PROBE_PATH.read_text(encoding="utf-8")

    assert "provider_tournament" not in source
    assert "provider-tournament" not in source
    assert "POPULATION_SHA" not in source
    assert "load_frozen" not in source
    assert "T3-01" not in source
    assert '"benchmark_inputs_loaded": 0' in source


def test_nvidia_probe_uses_current_hosted_v15_contract_without_unadvertised_schema_parameter() -> None:
    probe = _load_probe()
    config = probe.PROVIDERS["nvidia"]

    body = probe.request_body("nvidia", config["model"], "synthetic-request")

    assert config["model"] == "nvidia/llama-3.3-nemotron-super-49b-v1.5"
    assert body["model"] == config["model"]
    assert body["max_tokens"] == 512
    assert "max_completion_tokens" not in body
    assert "response_format" not in body
    assert body["temperature"] == 0
    assert body["stream"] is False
    assert body["messages"][0]["content"].startswith("/no_think\n")


def test_openrouter_probe_requires_exact_capabilities_using_supported_max_tokens_name() -> None:
    probe = _load_probe()
    config = probe.PROVIDERS["openrouter"]

    body = probe.request_body("openrouter", config["model"], "synthetic-request")

    assert body["max_tokens"] == 512
    assert "max_completion_tokens" not in body
    assert body["response_format"]["type"] == "json_schema"
    assert body["response_format"]["json_schema"]["strict"] is False
    assert body["provider"] == {"require_parameters": True, "allow_fallbacks": False}


def test_probe_response_extraction_is_shape_strict_and_sanitized() -> None:
    probe = _load_probe()
    payload = {
        "model": "example/model",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"content": '{"kind":"TOOL"}'},
            }
        ],
        "usage": {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18},
    }

    result = probe.extract_response(payload)

    assert result == {
        "content": '{"kind":"TOOL"}',
        "served_model": "example/model",
        "prompt_tokens": 11,
        "completion_tokens": 7,
        "total_tokens": 18,
        "choices_count": 1,
        "finish_reason": "stop",
        "message_content_present": True,
    }


def test_safe_error_never_copies_unknown_provider_fields() -> None:
    probe = _load_probe()
    payload = {
        "error": {
            "type": "rate_limit",
            "code": "429",
            "message": "sanitized diagnostic",
            "credential": "must-not-be-copied",
            "raw_request": {"secret": "must-not-be-copied"},
        }
    }

    result = probe.safe_error(payload)

    assert result == {
        "type": "rate_limit",
        "code": "429",
        "message": "sanitized diagnostic",
    }
