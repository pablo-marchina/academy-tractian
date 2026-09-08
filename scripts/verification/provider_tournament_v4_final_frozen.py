#!/usr/bin/env python3
from __future__ import annotations

"""Frozen entry point for the final GPT-OSS provider tournament.

This file deliberately leaves the preregistered V4 scoring/execution core unchanged and applies
only serving-boundary normalizations that are outside candidate quality:

1. Cloudflare's network model id begins with ``@cf/`` while the canonical safe audit identity
   schema deliberately excludes ``@``. The network request keeps the exact model id; only the
   persisted audit identity drops the leading ``@`` exactly as the production release adapter does.
2. Tournament-specific Cloudflare credentials, when configured, are copied into the generic
   Academy variable names consumed by the frozen core. This avoids overwriting production-serving
   credentials and permits an isolated billing/quota account for the experiment.
3. The HTTP client sends an explicit application User-Agent and JSON Accept header. Groq's edge
   rejects Python urllib's default browser signature with Cloudflare error 1010 even though the
   same API key/model are valid. This transport normalization is applied identically to both
   candidates and changes no prompt, schema, model, scoring, retry, or fallback behavior.
4. Groq calls are deterministically paced after each attempt using the live-account 8,000 TPM
   limit observed before the scored run. Pacing happens strictly outside the provider-call timer,
   so latency metrics remain request latency rather than benchmark scheduler delay. A 429 remains
   a scored failure; the cooldown only prevents one throttled attempt from mechanically cascading
   into subsequent attempts. No request is retried.

No retries, fallbacks, JSON repair, rubric changes, dataset changes, or candidate-specific scoring
changes are introduced here.
"""

from dataclasses import replace
import importlib.util
import os
from pathlib import Path
import sys
import time

CORE_PATH = Path(__file__).with_name("provider_tournament_v4_final.py")
SPEC = importlib.util.spec_from_file_location("provider_tournament_v4_final_core", CORE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load frozen V4 tournament core")
core = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = core
SPEC.loader.exec_module(core)

_real_identity = core.ProviderCallIdentity
_real_audit_integrity = core._audit_integrity
_real_build_http_request = core.OpenAICompatTournamentClient.build_http_request
_real_attempt = core._attempt
USER_AGENT = "academy-tractian-provider-tournament/1.0"
GROQ_TPM_LIMIT = 8000.0
GROQ_PACING_MARGIN_SECONDS = 1.0
GROQ_429_COOLDOWN_SECONDS = 60.0


def _audit_model_id(value: str) -> str:
    return value[1:] if value.startswith("@") else value


def _safe_provider_call_identity(**kwargs):
    kwargs["model_id"] = _audit_model_id(str(kwargs["model_id"]))
    return _real_identity(**kwargs)


def _safe_audit_integrity(*, source, candidate):
    return _real_audit_integrity(
        source=source,
        candidate=replace(candidate, model_id=_audit_model_id(candidate.model_id)),
    )


def _build_http_request_with_explicit_user_agent(self, request):
    built = _real_build_http_request(self, request)
    return replace(
        built,
        headers={
            **dict(built.headers),
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )


def _attempt_with_provider_pacing(**kwargs):
    row = _real_attempt(**kwargs)
    if row.get("candidate_id") != "groq-gpt-oss-120b":
        return row

    exception_code = str(row.get("exception_code") or "")
    if exception_code == "HTTP_STATUS:429":
        time.sleep(GROQ_429_COOLDOWN_SECONDS)
        return row

    total_tokens = row.get("total_tokens")
    if isinstance(total_tokens, int) and total_tokens > 0:
        delay = (float(total_tokens) / GROQ_TPM_LIMIT) * 60.0 + GROQ_PACING_MARGIN_SECONDS
        time.sleep(delay)
    return row


def _install_tournament_specific_cloudflare_credentials() -> None:
    account = os.environ.get("TOURNAMENT_CLOUDFLARE_ACCOUNT_ID", "").strip()
    token = os.environ.get("TOURNAMENT_CLOUDFLARE_API_TOKEN", "").strip()
    if bool(account) != bool(token):
        raise RuntimeError(
            "TOURNAMENT_CLOUDFLARE_ACCOUNT_ID and TOURNAMENT_CLOUDFLARE_API_TOKEN must be configured together"
        )
    if account and token:
        os.environ["ACADEMY_PROVIDER_ACCOUNT_ID"] = account
        os.environ["ACADEMY_PROVIDER_API_TOKEN"] = token


def main() -> int:
    _install_tournament_specific_cloudflare_credentials()
    core.ProviderCallIdentity = _safe_provider_call_identity
    core._audit_integrity = _safe_audit_integrity
    core.OpenAICompatTournamentClient.build_http_request = _build_http_request_with_explicit_user_agent
    core._attempt = _attempt_with_provider_pacing
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
