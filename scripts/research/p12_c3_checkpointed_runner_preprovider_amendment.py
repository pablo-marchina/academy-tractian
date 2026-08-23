#!/usr/bin/env python3
from __future__ import annotations

"""Derive the P12-C3 checkpoint runner after the pre-provider pacing-validation amendment.

The first B1 live attempt (run 32671370930) reached the live job but failed before
any provider request because the retained E14l configuration assertion requires
its historical transport values (25s/25s/retries=2), while P12-C3 prospectively
moved transport pacing/retry ownership to the checkpoint controller
(0s/0s/retries=0 at the inherited runner boundary, with controller-owned 30s
spacing and max 3 pre-output attempts).

This amendment changes only the compatibility assertion: it temporarily presents
the historical values to E14l's invariant check, restores the frozen P12-C3
transport overrides immediately, and does not alter prompts, model, candidates,
evaluator, seeds, batch map, checkpoint semantics, or scientific gates.
"""

import argparse
import hashlib
import importlib.util
from pathlib import Path

PRIOR_FIXUP_PATH = Path("scripts/research/p12_c3_checkpointed_runner_fixup.py")
PRIOR_FIXUP_GIT_BLOB_SHA = "edf38534ee6cede336432c644e01fda2b49944c3"
PRIOR_EFFECTIVE_RUNNER_SHA256 = "00cdf340714449bc0424777ec73598f5d8f172436c543918fc9e3ef383fc806e"


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def load_prior_fixup():
    raw = PRIOR_FIXUP_PATH.read_bytes()
    actual = git_blob_sha(raw)
    if actual != PRIOR_FIXUP_GIT_BLOB_SHA:
        raise AssertionError(f"prior P12-C3 fixup blob changed: {actual}")
    spec = importlib.util.spec_from_file_location("p12_c3_prior_fixup", PRIOR_FIXUP_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load prior P12-C3 fixup")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label} anchor count changed: {count}")
    return text.replace(old, new)


def derive(base_text: str) -> str:
    prior = load_prior_fixup()
    text = prior.derive(base_text)
    prior_sha = hashlib.sha256(text.encode()).hexdigest()
    if prior_sha != PRIOR_EFFECTIVE_RUNNER_SHA256:
        raise AssertionError(f"prior effective runner changed: {prior_sha}")

    helper_anchor = '''def persist(cap,cp,raw,public,batch): cp["checkpoint_version"]=int(cp.get("checkpoint_version",0))+1; write(raw,cp); write(public,pub(cap,cp,batch))\n\n\ndef prepare(a):\n'''
    helper_replacement = '''def persist(cap,cp,raw,public,batch): cp["checkpoint_version"]=int(cp.get("checkpoint_version",0))+1; write(raw,cp); write(public,pub(cap,cp,batch))\n\n\ndef assert_parent_config_with_c3_transport_override(runner):\n    keys=("E8_BETWEEN_CALL_DELAY_SECONDS","E14F_REPAIR_DELAY_SECONDS","E14_MAX_RETRIES")\n    saved={k:os.environ.get(k) for k in keys}\n    assert saved["E8_BETWEEN_CALL_DELAY_SECONDS"]=="0"\n    assert saved["E14F_REPAIR_DELAY_SECONDS"]=="0"\n    assert saved["E14_MAX_RETRIES"]=="0"\n    try:\n        os.environ["E8_BETWEEN_CALL_DELAY_SECONDS"]="25"\n        os.environ["E14F_REPAIR_DELAY_SECONDS"]="25"\n        os.environ["E14_MAX_RETRIES"]="2"\n        runner.e14o.e14l.assert_frozen_configuration(dry_run=False)\n    finally:\n        for k,v in saved.items():\n            if v is None: os.environ.pop(k,None)\n            else: os.environ[k]=v\n    assert os.environ.get("E8_BETWEEN_CALL_DELAY_SECONDS")=="0"\n    assert os.environ.get("E14F_REPAIR_DELAY_SECONDS")=="0"\n    assert os.environ.get("E14_MAX_RETRIES")=="0"\n\n\ndef prepare(a):\n'''
    text = replace_once(text, helper_anchor, helper_replacement, "c3_transport_validation_bridge_helper")

    old = '''    if not a.dry_run:\n        runner.e14o.e14l.assert_frozen_configuration(dry_run=False); runner.e14o.e14l.schema.run_self_checks(); runner.base.assert_zero_cost_guard("groq",False); assert os.getenv("GROQ_API_KEY")\n'''
    new = '''    if not a.dry_run:\n        assert_parent_config_with_c3_transport_override(runner); runner.e14o.e14l.schema.run_self_checks(); runner.base.assert_zero_cost_guard("groq",False); assert os.getenv("GROQ_API_KEY")\n'''
    text = replace_once(text, old, new, "e14l_transport_assertion_bridge")

    definition = "def assert_parent_config_with_c3_transport_override(runner):"
    call = "        assert_parent_config_with_c3_transport_override(runner);"
    if text.count(definition) != 1 or text.count(call) != 1:
        raise AssertionError("C3 transport validation bridge definition/call count changed")
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base_text = args.base.read_text(encoding="utf-8")
    derived = derive(base_text)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(derived, encoding="utf-8")
    print(hashlib.sha256(derived.encode()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
