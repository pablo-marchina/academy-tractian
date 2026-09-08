#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import replace
import importlib.util
from pathlib import Path
import sys

RUNNER_PATH = Path(__file__).with_name("provider_tournament_v4_final.py")
SPEC = importlib.util.spec_from_file_location("provider_tournament_v4_final_impl", RUNNER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load V4 tournament runner")
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)

_real_identity = module.ProviderCallIdentity
_real_audit_integrity = module._audit_integrity


def _audit_model_id(value: str) -> str:
    # ProviderCallIdentity is a browser-safe provenance identity and deliberately excludes '@'.
    # Network requests continue to use the exact provider model id, including Cloudflare's @cf/ prefix.
    return value[1:] if value.startswith("@") else value


def _safe_provider_call_identity(**kwargs):
    kwargs["model_id"] = _audit_model_id(str(kwargs["model_id"]))
    return _real_identity(**kwargs)


def _safe_audit_integrity(*, source, candidate):
    return _real_audit_integrity(
        source=source,
        candidate=replace(candidate, model_id=_audit_model_id(candidate.model_id)),
    )


module.ProviderCallIdentity = _safe_provider_call_identity
module._audit_integrity = _safe_audit_integrity

if __name__ == "__main__":
    raise SystemExit(module.main())
