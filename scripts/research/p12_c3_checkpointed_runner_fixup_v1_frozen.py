#!/usr/bin/env python3
from __future__ import annotations

"""Derive the effective P12-C3 checkpoint runner from the frozen base source.

This fail-closed infrastructure fixup is frozen before any P12-C3 provider call.
It does not alter candidate definitions, model/prompt config, evaluator, seeds,
batch geometry, or deterministic gates. It ensures capacity pauses survive the
qualified parent runner's exception-to-record boundary, terminal checkpoints are
publicly summarizable but never resumable, and the byte-identical derived parent
runner is imported from `scripts/research/` so all historical path-relative
module and repository-root resolution semantics remain unchanged.
"""
import argparse
import hashlib
from pathlib import Path

BASE_GIT_BLOB_SHA = "2dd70d4b121a4ad98944d50c2e7fc3381f520b41"


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"{label} anchor count changed: {count}")
    return text.replace(old, new)


def derive(text: str) -> str:
    text = replace_once(
        text,
        '''def mod(name:str,p:Path):\n    s=importlib.util.spec_from_file_location(name,p); assert s and s.loader; m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m\n''',
        '''def mod(name:str,p:Path):\n    s=importlib.util.spec_from_file_location(name,p); assert s and s.loader; m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m\n\ndef base_mod(name:str,p:Path):\n    source=Path("scripts/research")\n    assert source.is_dir()\n    if p.parent.resolve()!=source.resolve():\n        runtime=source/"p12_c3_runtime_parent_execution.py"\n        runtime.write_bytes(p.read_bytes())\n        p=runtime\n    return mod(name,p)\n''',
        "derived_runner_repository_topology",
    )
    text = replace_once(
        text,
        '''def valid(cap,cp,bm,execution):\n    assert cp["schema_version"]==SCHEMA and cp["experiment_id"]==EXP and cp["execution_id"]==execution\n    cap.validate_checkpoint(cp,ids(bm)); assert cp.get("terminal_failure") is None\n''',
        '''def valid(cap,cp,bm,execution,allow_terminal=False):\n    assert cp["schema_version"]==SCHEMA and cp["experiment_id"]==EXP and cp["execution_id"]==execution\n    cap.validate_checkpoint(cp,ids(bm))\n    if not allow_terminal: assert cp.get("terminal_failure") is None\n''',
        "terminal_checkpoint_validation",
    )
    text = replace_once(
        text,
        '''class Pause(Exception):\n    def __init__(self,reason,resume=None): self.reason,self.resume=reason,resume\n\nclass C3Post:\n''',
        '''class Pause(Exception):\n    def __init__(self,reason,resume=None):\n        self.reason,self.resume=reason,resume; self.category="c3_pause_pre_output:"+reason\n\nclass C3Fail(RuntimeError):\n    def __init__(self,category):\n        super().__init__(category); self.category=category\n\nclass C3Post:\n''',
        "typed_capacity_exceptions",
    )
    text = replace_once(
        text,
        'self.response_seen=False; self.last=None',
        'self.response_seen=False; self.last=None; self.sent=False',
        "provider_send_tracking",
    )
    terminal_count = text.count('raise RuntimeError("c3_terminal_')
    if terminal_count < 1:
        raise AssertionError("terminal capacity exception anchors missing")
    text = text.replace('raise RuntimeError("c3_terminal_', 'raise C3Fail("c3_terminal_')
    text = replace_once(
        text,
        'req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers=rh,method="POST")',
        'req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers=rh,method="POST"); self.sent=True',
        "provider_request_send_tracking",
    )
    text = text.replace('mod("c3base",a.base_runner)', 'base_mod("c3base",a.base_runner)')
    text = text.replace('mod("c3basefin",a.base_runner)', 'base_mod("c3basefin",a.base_runner)')
    if text.count('base_mod("c3base",a.base_runner)') != 1 or text.count('base_mod("c3basefin",a.base_runner)') != 1:
        raise AssertionError("base runner import anchors changed")
    old = '''    try:\n        rec=runner.generate_one(mapping=cell,visible_case=case,source_split=split,seed=int(cell["seed"]),repeat_index=int(cell["repeat_index"]),timeout=a.timeout_seconds,dry_run=a.dry_run,is_first_call=True)\n    except Pause as e:\n        persist(cap,cp,a.checkpoint_out,a.public_out,a.batch_id); write(a.cell_summary,{"status":"PAUSED_PRE_OUTPUT","continue_with_batch":False,"terminal":False,"cell_id":cid,"reason":e.reason,"resume_at":e.resume,"provider_call_made":not a.dry_run}); return 0\n    except RuntimeError as e:\n        reason=str(e); post=reason.startswith("c3_terminal_post_output:"); cp["terminal_failure"]={"cell_id":cid,"batch_id":a.batch_id,"reason":reason,"post_initial_output":post,"recorded_at":now().isoformat()}; persist(cap,cp,a.checkpoint_out,a.public_out,a.batch_id); write(a.cell_summary,{"status":"TERMINAL_EXPERIMENT_FAILURE","continue_with_batch":False,"terminal":True,"cell_id":cid,"reason":reason,"provider_call_made":not a.dry_run}); return 0\n    finally: runner.transport.post_json=old\n    if rec.get("success") is not True:\n        reason=str(rec.get("error_category") or "UNKNOWN_PARENT_FAILURE"); cp["terminal_failure"]={"cell_id":cid,"batch_id":a.batch_id,"reason":reason,"post_initial_output":not reason.startswith("c3_terminal_pre_output:"),"recorded_at":now().isoformat()}; persist(cap,cp,a.checkpoint_out,a.public_out,a.batch_id); write(a.cell_summary,{"status":"TERMINAL_EXPERIMENT_FAILURE","continue_with_batch":False,"terminal":True,"cell_id":cid,"reason":reason,"provider_call_made":not a.dry_run}); return 0\n'''
    new = '''    try:\n        rec=runner.generate_one(mapping=cell,visible_case=case,source_split=split,seed=int(cell["seed"]),repeat_index=int(cell["repeat_index"]),timeout=a.timeout_seconds,dry_run=a.dry_run,is_first_call=True)\n    finally:\n        runner.transport.post_json=old\n    if rec.get("success") is not True:\n        reason=str(rec.get("error_category") or "UNKNOWN_PARENT_FAILURE")\n        if reason.startswith("c3_pause_pre_output:"):\n            persist(cap,cp,a.checkpoint_out,a.public_out,a.batch_id); write(a.cell_summary,{"status":"PAUSED_PRE_OUTPUT","continue_with_batch":False,"terminal":False,"cell_id":cid,"reason":reason,"resume_at":cp.get("cell_resume_at",{}).get(cid),"provider_call_made":ctl.sent}); return 0\n        post=reason.startswith("c3_terminal_post_output:") or ctl.response_seen\n        cp["terminal_failure"]={"cell_id":cid,"batch_id":a.batch_id,"reason":reason,"post_initial_output":post,"recorded_at":now().isoformat()}; persist(cap,cp,a.checkpoint_out,a.public_out,a.batch_id); write(a.cell_summary,{"status":"TERMINAL_EXPERIMENT_FAILURE","continue_with_batch":False,"terminal":True,"cell_id":cid,"reason":reason,"provider_call_made":ctl.sent}); return 0\n'''
    text = replace_once(text, old, new, "qualified_runner_exception_boundary")
    text = replace_once(
        text,
        'valid(cap,cp,bm,a.execution_id); b=bids(bm)[a.batch_id]; complete=',
        'valid(cap,cp,bm,a.execution_id,allow_terminal=True); b=bids(bm)[a.batch_id]; complete=',
        "terminal_public_summary",
    )
    if 'except Pause as e:' in text or 'except RuntimeError as e:' in text:
        raise AssertionError("obsolete direct exception handling survived fixup")
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raw = args.base.read_bytes()
    actual = git_blob_sha(raw)
    if actual != BASE_GIT_BLOB_SHA:
        raise AssertionError(f"P12-C3 checkpoint runner base blob changed: {actual}")
    derived = derive(raw.decode("utf-8"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(derived, encoding="utf-8")
    print(hashlib.sha256(derived.encode()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
