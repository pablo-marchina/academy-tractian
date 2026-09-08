#!/usr/bin/env python3
from __future__ import annotations

"""Frozen entry point for the final GPT-OSS provider tournament.

This file deliberately leaves the preregistered V4 scoring/execution core unchanged and applies
only two serving-boundary normalizations that are outside candidate quality:

1. Cloudflare's network model id begins with ``@cf/`` while the canonical safe audit identity
   schema deliberately excludes ``@``. The network request keeps the exact model id; only the
   persisted audit identity drops the leading ``@`` exactly as the production release adapter does.
2. Tournament-specific Cloudflare credentials, when configured, are copied into the generic
   Academy variable names consumed by the frozen core. This avoids overwriting production-serving
   credentials and permits an isolated billing/quota account for the experiment.

No retries, fallbacks, JSON repair, rubric changes, dataset changes, or candidate-specific scoring
changes are introduced here.
"""

from dataclasses import replace
import importlib.util
import os
from pathlib import Path
import sys

CORE_PATH = Path(__file__).with_name("provider_tournament_v4_final.py")
SPEC = importlib.util.spec_from_file_location("provider_tournament_v4_final_core", CORE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load frozen V4 tournament core")
core = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = core
SPEC.loader.exec_module(core)

_real_identity = core.ProviderCallIdentity
_real_audit_integrity = core._audit_integrity


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
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
