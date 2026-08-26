#!/usr/bin/env python3
"""P12-C4 NVIDIA one-shot live common-parent runner: 36/36 or terminal incomplete."""
from __future__ import annotations

import argparse, ast, hashlib, importlib.metadata, importlib.util, json, os, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

R = Path(__file__).resolve().parents[2]
M = R / "research/experiments/p12-c4-nvidia-one-shot-live-manifest-v1.json"
A = R / "research/frozen/p12-c4-nvidia-one-shot-live-execution-authorization-v1.json"
ACT = R / "research/experiments/p12-c2-exposed-pool-activation-eligibility-v1.json"
CASES = R / "research/fixtures/p12-c1-exposed-agent-input-cases-v1.json"
SEEDS = R / "research/frozen/p12-c4-fresh-seed-map-v1.json"
E10B = R / "scripts/research/e10b_dev_only_action_escalation_capture.py"
E14O = R / "scripts/research/e14o_dev_only_public_factual_grounding_prompt.py"
E14J = R / "scripts/research/e14j_strict_output_schema.py"

URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "openai/gpt-oss-120b"
HX = "0.28.1"
N = 36
PACE = 75
OUT = R / "research/live/p12-c4-nvidia-one-shot-v1"
PARENTS = OUT / "common-parents.jsonl"
LEDGER = OUT / "request-ledger.jsonl"
RESULT = OUT / "execution-result.json"

class PreflightBlocked(RuntimeError): pass
class TerminalIncomplete(RuntimeError): pass

def load(p: Path) -> Any: return json.loads(p.read_text(encoding="utf-8"))
def canon(x: Any) -> str: return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def sh(x: Any) -> str: return hashlib.sha256(canon(x).encode("utf-8")).hexdigest()
def shb(x: bytes) -> str: return hashlib.sha256(x).hexdigest()
def blob(p: Path) -> str:
    b = p.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
def now() -> str: return datetime.now(timezone.utc).isoformat()
def write(p: Path, x: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
def append(p: Path, x: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(canon(x) + "\n"); f.flush(); os.fsync(f.fileno())
def mod(name: str, p: Path):
    s = importlib.util.spec_from_file_location(name, p)
    if s is None or s.loader is None: raise PreflightBlocked(f"cannot load {p}")
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def e14o_suffix() -> tuple[str, str]:
    tree = ast.parse(E14O.read_text(encoding="utf-8"), filename=str(E14O))
    marker = None; expr = None
    for n in tree.body:
        if not isinstance(n, ast.Assign) or len(n.targets) != 1 or not isinstance(n.targets[0], ast.Name): continue
        k = n.targets[0].id
        if k == "PROMPT_MARKER" and isinstance(n.value, ast.Constant): marker = n.value.value
        elif k == "FACTUAL_GROUNDING_SUFFIX": expr = n.value
    strip = False
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr == "rstrip":
        expr = expr.func.value; strip = True
    if not isinstance(marker, str) or not isinstance(expr, ast.JoinedStr):
        raise PreflightBlocked("E14o prompt constants changed")
    out = []
    for v in expr.values:
        if isinstance(v, ast.Constant) and isinstance(v.value, str): out.append(v.value)
        elif isinstance(v, ast.FormattedValue) and isinstance(v.value, ast.Name) and v.value.id == "PROMPT_MARKER": out.append(marker)
        else: raise PreflightBlocked("E14o suffix contains unapproved dynamic expression")
    text = "".join(out)
    return marker, text.rstrip() if strip else text

def cases(payload: Any) -> dict[str, dict[str, Any]]:
    rows = payload.get("cases") if isinstance(payload, dict) else payload
    if not isinstance(rows, list): raise PreflightBlocked("public cases shape changed")
    out = {}
    for x in rows:
        if isinstance(x, dict) and x.get("ticket_id"):
            k = str(x["ticket_id"])
            if k in out: raise PreflightBlocked(f"duplicate ticket {k}")
            out[k] = x
    return out

def schema_ok(x: Any, s: dict[str, Any], at="$") -> None:
    t = s.get("type")
    if t == "object":
        if not isinstance(x, dict): raise TerminalIncomplete(f"{at}: expected object")
        props = s.get("properties") or {}; req = s.get("required") or []
        miss = [k for k in req if k not in x]
        if miss: raise TerminalIncomplete(f"{at}: missing {miss}")
        if s.get("additionalProperties") is False:
            extra = sorted(set(x)-set(props))
            if extra: raise TerminalIncomplete(f"{at}: extra {extra}")
        for k, sub in props.items():
            if k in x: schema_ok(x[k], sub, f"{at}.{k}")
    elif t == "array":
        if not isinstance(x, list): raise TerminalIncomplete(f"{at}: expected array")
        for i, v in enumerate(x): schema_ok(v, s.get("items") or {}, f"{at}[{i}]")
    elif t == "string":
        if not isinstance(x, str): raise TerminalIncomplete(f"{at}: expected string")
    elif t == "boolean":
        if not isinstance(x, bool): raise TerminalIncomplete(f"{at}: expected boolean")
    elif t is not None: raise PreflightBlocked(f"unsupported public schema type {t}")
    if "enum" in s and x not in s["enum"]: raise TerminalIncomplete(f"{at}: enum violation")

def manifest() -> dict[str, Any]:
    m = load(M)
    if not isinstance(m, dict) or m.get("schema_version") != "p12-c4-nvidia-one-shot-live-manifest-v1":
        raise PreflightBlocked("manifest schema mismatch")
    if m.get("manifest_id") != "P12-C4-NVIDIA-ONE-SHOT-LIVE-V1" or m.get("status") != "FROZEN_PROVIDER_FREE_PENDING_LIVE_EXECUTION":
        raise PreflightBlocked("manifest identity/state mismatch")
    p = m.get("provider") or {}; q = m.get("request_semantics") or {}; t = m.get("transport") or {}; one = m.get("one_shot_execution") or {}
    if (p.get("name"),p.get("endpoint"),p.get("model_id"),p.get("credential_env")) != ("NVIDIA",URL,MODEL,"NVIDIA_API_KEY"):
        raise PreflightBlocked("provider mismatch")
    if p.get("fallback_provider") is not None or p.get("model_fallbacks") != [] or p.get("automatic_failover") is not False:
        raise PreflightBlocked("provider fallback contract changed")
    expected_q = {"temperature":0,"max_tokens":4096,"reasoning_effort":"medium","stream":False,"response_format":"json_schema_strict",
                  "seed_required_per_request":True,"parallel_tool_calls":False,"drop_reasoning_content_before_persistence":True}
    if any(q.get(k) != v for k,v in expected_q.items()): raise PreflightBlocked("request semantics changed")
    expected_t = {"client":"httpx","version":HX,"connect_timeout_seconds":10,"read_timeout_seconds":180,"write_timeout_seconds":30,
                  "pool_timeout_seconds":10,"follow_redirects":False,"application_retries":0,"implicit_retries_allowed":False}
    if any(t.get(k) != v for k,v in expected_t.items()): raise PreflightBlocked("transport changed")
    expected_one = {"common_parent_count":36,"maximum_provider_request_attempts":36,"maximum_attempts_per_parent":1,
                    "minimum_seconds_between_request_starts":75,"warming_requests":0,"automatic_retries":0,
                    "resume_after_incomplete_packet":False,"workflow_rerun_allowed":False,"completed_parent_regeneration_allowed":False,
                    "bursting_forbidden":True,"provider_fallbacks":0,"model_fallbacks":0}
    if any(one.get(k) != v for k,v in expected_one.items()): raise PreflightBlocked("one-shot contract changed")
    fail = one.get("failure_policy") or {}
    if len(fail) != 5 or set(fail.values()) != {"ABORT_PACKET_INCOMPLETE_NO_SCORING"}: raise PreflightBlocked("failure policy changed")
    b = m.get("packet_freeze_and_scoring_boundary") or {}
    if any(b.get(k) != "FORBIDDEN" for k in ("deterministic_private_scoring_before_packet_freeze","partial_packet_scoring","bootstrap_before_deterministic_scoring")):
        raise PreflightBlocked("scoring boundary changed")
    for name,pin in (m.get("source_pins") or {}).items():
        path = R / str(pin.get("path",""))
        if not path.is_file() or blob(path) != pin.get("git_blob_sha"): raise PreflightBlocked(f"manifest source pin mismatch: {name}")
    return m

def authorization(m: dict[str, Any], path=A) -> dict[str, Any]:
    if not path.is_file(): raise PreflightBlocked("one-shot authorization absent")
    a = load(path)
    need = {"schema_version":"p12-c4-nvidia-one-shot-live-execution-authorization-v1",
            "status":"AUTHORIZED_ONE_C4_NVIDIA_LIVE_EXECUTION_ATTEMPT","manifest_id":"P12-C4-NVIDIA-ONE-SHOT-LIVE-V1",
            "manifest_git_blob_sha":blob(M),"runner_git_blob_sha":blob(Path(__file__)),"authorized_live_execution_attempts":1,
            "maximum_provider_request_attempts":36,"maximum_attempts_per_parent":1,"minimum_seconds_between_request_starts":75,
            "automatic_retries":0,"provider_fallbacks":0,"model_fallbacks":0,"warming_requests":0,"rerun_allowed":False,
            "resume_allowed":False,"completed_parent_regeneration_allowed":False,"private_scoring_authorized":False,
            "fresh_blind_authorized":False,"legacy_locked_test_authorized":False}
    if not isinstance(a, dict) or any(a.get(k) != v for k,v in need.items()): raise PreflightBlocked("authorization mismatch")
    if (a.get("provider"),a.get("endpoint"),a.get("model_id")) != ("NVIDIA",URL,MODEL): raise PreflightBlocked("authorization provider mismatch")
    if a.get("failure_policy") != (m.get("one_shot_execution") or {}).get("failure_policy"): raise PreflightBlocked("authorization failure policy mismatch")
    pins = a.get("request_materialization_source_pins") or {}
    if not isinstance(pins,dict) or not pins: raise PreflightBlocked("authorization source pins absent")
    for name,pin in pins.items():
        p = R / str(pin.get("path",""))
        if not p.is_file() or blob(p) != pin.get("git_blob_sha"): raise PreflightBlocked(f"authorization source pin mismatch: {name}")
    return a

def requests(m: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str,Any]]:
    mapping = load(ACT).get("exposed_pool_mapping"); c = cases(load(CASES)); seeds = load(SEEDS).get("common_parents")
    if not isinstance(mapping,list) or len(mapping)!=12 or not isinstance(seeds,list) or len(seeds)!=36:
        raise PreflightBlocked("public 12x3 geometry changed")
    e10b=mod("p12_c4_live_e10b",E10B); e14j=mod("p12_c4_live_e14j",E14J); e14j.run_self_checks()
    marker,suffix=e14o_suffix(); sys=e10b.STRICT_E10B_SYSTEM_PROMPT.rstrip()+suffix
    if marker not in sys: raise PreflightBlocked("E14o marker missing")
    rf=e14j.strict_response_format(); ordered=m.get("ordered_requests") or []; out=[]; n=0
    if len(ordered)!=36: raise PreflightBlocked("ordered request count changed")
    for mp in mapping:
        ticket=str(mp["ticket_id"]); gid=str(mp["group_id"]); case=c.get(ticket)
        if case is None or str(case.get("asset_id"))!=gid: raise PreflightBlocked(f"ticket/group mismatch {ticket}")
        for repeat in range(3):
            n+=1; b=ordered[n-1]; sr=seeds[n-1]; pid=f"P{n:02d}"
            if (b.get("ordinal"),b.get("parent_id"),b.get("maximum_attempts"))!=(n,pid,1): raise PreflightBlocked(f"manifest binding {pid}")
            seed=int(b["seed"])
            if (sr.get("ordinal"),sr.get("parent_id"),int(sr.get("seed")))!=(n,pid,seed): raise PreflightBlocked(f"seed binding {pid}")
            packet=e10b.e10b_observation_packet("EXPOSED_POOL",gid,{gid:case}); user=e10b.e10b_build_prompt(packet,repeat)
            req={"model":MODEL,"messages":[{"role":"system","content":sys},{"role":"user","content":user}],"temperature":0,
                 "reasoning_effort":"medium","max_tokens":4096,"seed":seed,"stream":False,"parallel_tool_calls":False,"response_format":rf}
            out.append({"ordinal":n,"parent_id":pid,"ticket_id":ticket,"group_id":gid,"repeat_index":repeat,"seed":seed,
                        "packet_sha256":sh(packet),"system_prompt_sha256":shb(sys.encode()),"user_prompt_sha256":shb(user.encode()),
                        "request_sha256":sh(req),"request":req})
    return out,{"schema":e14j.OUTPUT_SCHEMA,"response_format_sha256":sh(rf)}

def parse_response(x: Any, schema: dict[str,Any]) -> tuple[dict[str,Any],dict[str,Any]]:
    if not isinstance(x,dict) or "gpt-oss-120b" not in str(x.get("model","")).lower(): raise TerminalIncomplete("model mismatch")
    ch=x.get("choices")
    if not isinstance(ch,list) or len(ch)!=1 or not isinstance(ch[0],dict): raise TerminalIncomplete("choice shape")
    if ch[0].get("finish_reason")!="stop": raise TerminalIncomplete(f"finish_reason={ch[0].get('finish_reason')!r}")
    msg=ch[0].get("message") or {}; content=msg.get("content") if isinstance(msg,dict) else None
    try: y=content if isinstance(content,dict) else json.loads(content) if isinstance(content,str) else None
    except Exception as e: raise TerminalIncomplete("final content is not JSON") from e
    if not isinstance(y,dict): raise TerminalIncomplete("final JSON is not object")
    schema_ok(y,schema)
    safe={"model":x.get("model"),"finish_reason":ch[0].get("finish_reason"),"usage":x.get("usage"),"parsed_output":y}
    return y,safe

def preflight() -> dict[str,Any]:
    m=manifest(); a=authorization(m); rows,meta=requests(m)
    return {"schema_version":"p12-c4-nvidia-one-shot-live-preflight-v1","status":"PASS_PROVIDER_FREE_LIVE_NOT_STARTED",
            "manifest_git_blob_sha":blob(M),"authorization_git_blob_sha":blob(A),"runner_git_blob_sha":blob(Path(__file__)),
            "materialized_common_parents":len(rows),"unique_parent_ids":len({r["parent_id"] for r in rows}),
            "unique_seeds":len({r["seed"] for r in rows}),"unique_requests":len({r["request_sha256"] for r in rows}),
            "response_format_sha256":meta["response_format_sha256"],"provider_calls":0,"network_io":0,
            "private_oracle_accesses":0,"fresh_blind_accesses":0,"legacy_locked_test_accesses":0,
            "authorized_live_execution_attempts":a["authorized_live_execution_attempts"],
            "next_gate":"ONE_NVIDIA_LIVE_EXECUTION_36_OF_36_OR_TERMINAL_INCOMPLETE"}

def live() -> dict[str,Any]:
    for p in (PARENTS,LEDGER,RESULT):
        if p.exists(): raise PreflightBlocked(f"output already exists; rerun/resume forbidden: {p}")
    m=manifest(); authorization(m); rows,meta=requests(m)
    try: hv=importlib.metadata.version("httpx")
    except importlib.metadata.PackageNotFoundError as e: raise PreflightBlocked("httpx absent") from e
    if hv!=HX: raise PreflightBlocked(f"httpx pin mismatch: {hv}")
    key=os.getenv("NVIDIA_API_KEY")
    if not key: raise PreflightBlocked("NVIDIA_API_KEY absent; zero provider attempts")
    import httpx
    t=m["transport"]; timeout=httpx.Timeout(connect=t["connect_timeout_seconds"],read=t["read_timeout_seconds"],
        write=t["write_timeout_seconds"],pool=t["pool_timeout_seconds"])
    try: client=httpx.Client(timeout=timeout,transport=httpx.HTTPTransport(retries=0),follow_redirects=False)
    except Exception as e: raise PreflightBlocked("HTTP client construction failed before provider attempt") from e
    attempts=valid=0; last=None; started=now()
    try:
        with client:
            for row in rows:
                if last is not None:
                    wait=PACE-(time.monotonic()-last)
                    if wait>0: time.sleep(wait)
                started_req=now(); start=time.monotonic(); last=start; attempts+=1
                r=client.post(URL,headers={"Authorization":f"Bearer {key}","Content-Type":"application/json","Accept":"application/json"},json=row["request"])
                elapsed=time.monotonic()-start
                allowed={"x-request-id","request-id","retry-after","x-ratelimit-limit","x-ratelimit-remaining","x-ratelimit-reset"}
                headers={str(k).lower():str(v) for k,v in r.headers.items() if str(k).lower() in allowed}
                append(LEDGER,{"ordinal":row["ordinal"],"parent_id":row["parent_id"],"ticket_id":row["ticket_id"],"group_id":row["group_id"],
                    "repeat_index":row["repeat_index"],"seed":row["seed"],"request_started_at_utc":started_req,
                    "elapsed_seconds":round(elapsed,6),"request_sha256":row["request_sha256"],"http_status":r.status_code,
                    "response_headers_sanitized":headers,"raw_response_sha256":shb(r.content)})
                if not 200<=r.status_code<300: raise TerminalIncomplete(f"{row['parent_id']}: HTTP {r.status_code}")
                try: payload=r.json()
                except Exception as e: raise TerminalIncomplete(f"{row['parent_id']}: non-JSON response") from e
                parsed,safe=parse_response(payload,meta["schema"])
                append(PARENTS,{"ordinal":row["ordinal"],"parent_id":row["parent_id"],"ticket_id":row["ticket_id"],"group_id":row["group_id"],
                    "repeat_index":row["repeat_index"],"seed":row["seed"],"packet_sha256":row["packet_sha256"],
                    "system_prompt_sha256":row["system_prompt_sha256"],"user_prompt_sha256":row["user_prompt_sha256"],
                    "request_sha256":row["request_sha256"],"response_sha256":sh(safe),"provider_model":safe["model"],
                    "finish_reason":safe["finish_reason"],"usage":safe["usage"],"parsed_output":parsed})
                valid+=1
        if attempts!=36 or valid!=36: raise TerminalIncomplete(f"incomplete: attempts={attempts}, valid={valid}")
        z={"schema_version":"p12-c4-nvidia-one-shot-live-execution-result-v1","manifest_id":m["manifest_id"],
           "status":"PASS_36_OF_36_FRESH_COMMON_PARENTS","started_at_utc":started,"completed_at_utc":now(),
           "provider":"NVIDIA","endpoint":URL,"model_id":MODEL,"provider_request_attempts":attempts,"valid_common_parents":valid,
           "required_common_parents":36,"automatic_retries":0,"provider_fallbacks":0,"model_fallbacks":0,"warming_requests":0,
           "resume_allowed":False,"rerun_allowed":False,"reasoning_content_persisted":False,"private_oracle_accesses":0,
           "fresh_blind_accesses":0,"legacy_locked_test_accesses":0,"local_arm_expansion_authorized":True,
           "expected_local_arm_outputs":144,"private_scoring_authorized":False,"bootstrap_authorized":False,
           "manifest_git_blob_sha":blob(M),"authorization_git_blob_sha":blob(A),"runner_git_blob_sha":blob(Path(__file__)),
           "common_parents_sha256":shb(PARENTS.read_bytes()),"request_ledger_sha256":shb(LEDGER.read_bytes()),
           "next_gate":"C4_144_OF_144_LOCAL_ARM_OUTPUTS"}
        write(RESULT,z); return z
    except Exception as e:
        z={"schema_version":"p12-c4-nvidia-one-shot-live-execution-result-v1","manifest_id":m["manifest_id"],
           "status":"CONSUMED_TERMINAL_INCOMPLETE_NO_SCORING","started_at_utc":started,"completed_at_utc":now(),
           "provider":"NVIDIA","endpoint":URL,"model_id":MODEL,"provider_request_attempts":attempts,"valid_common_parents":valid,
           "required_common_parents":36,"terminal_error":{"type":type(e).__name__,"message":str(e)},
           "automatic_retries":0,"provider_fallbacks":0,"model_fallbacks":0,"warming_requests":0,"resume_allowed":False,
           "rerun_allowed":False,"reasoning_content_persisted":False,"private_oracle_accesses":0,"fresh_blind_accesses":0,
           "legacy_locked_test_accesses":0,"local_arm_expansion_authorized":False,"private_scoring_authorized":False,
           "bootstrap_authorized":False,"partial_packet_scoring":False,"complete_case_reinterpretation":False,
           "manifest_git_blob_sha":blob(M),"authorization_git_blob_sha":blob(A),"runner_git_blob_sha":blob(Path(__file__)),
           "common_parents_sha256":shb(PARENTS.read_bytes()) if PARENTS.exists() else None,
           "request_ledger_sha256":shb(LEDGER.read_bytes()) if LEDGER.exists() else None,
           "next_gate":"STOP_C4_TERMINAL_INCOMPLETE_NO_SCORING"}
        write(RESULT,z); return z

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--provider-free-check",action="store_true"); x=ap.parse_args()
    try: z=preflight() if x.provider_free_check else live()
    except PreflightBlocked as e:
        z={"schema_version":"p12-c4-nvidia-one-shot-live-preflight-v1",
           "status":"BLOCKED_BEFORE_PROVIDER_ATTEMPT_AUTHORIZATION_NOT_CONSUMED","error_type":type(e).__name__,"error":str(e),
           "provider_calls":0,"provider_request_attempts":0,"private_scoring_authorized":False,
           "next_gate":"FIX_PREFLIGHT_WITHOUT_PROVIDER_CALL_THEN_EXECUTE_SAME_FROZEN_MANIFEST"}
        print(json.dumps(z,indent=2,sort_keys=True)); return 2
    print(json.dumps(z,indent=2,sort_keys=True))
    return 0 if z["status"] in {"PASS_PROVIDER_FREE_LIVE_NOT_STARTED","PASS_36_OF_36_FRESH_COMMON_PARENTS"} else 1

if __name__=="__main__": raise SystemExit(main())
