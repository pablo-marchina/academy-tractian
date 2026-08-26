#!/usr/bin/env python3
"""P12-C4 OpenRouter/OpenInference synthetic gate. Fail closed; no retries/fallbacks."""
from __future__ import annotations
import argparse, hashlib, json, os, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

R=Path(__file__).resolve().parents[2]
P=R/"research/experiments/p12-c4-openrouter-synthetic-compatibility-probe-preregistration-v1.json"
S=R/"research/experiments/p12-c4-openrouter-provider-serving-contract-v1.json"
G=R/"research/frozen/p12-c4-openrouter-request-budget-and-pacing-v1.json"
C=R/"research/results/p12-c4-cerebras-synthetic-live-probe-closure-2026-08-25.json"
A=R/"research/frozen/p12-c4-openrouter-synthetic-probe-live-authorization-v1.json"
ID="P12-C4-OPENROUTER-SYNTHETIC-COMPATIBILITY-V1"; MODEL="openai/gpt-oss-120b:free"; UP="open-inference"
URL="https://openrouter.ai/api/v1/chat/completions"; HX="0.28.1"
ROUTE={"allow_fallbacks":False,"only":[UP],"order":[UP],"require_parameters":True}

class Blocked(RuntimeError): pass
def load(p): 
    x=json.loads(Path(p).read_text(encoding="utf-8"))
    if not isinstance(x,dict): raise Blocked(f"{p} not object")
    return x
def h(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def write(p,x):
    Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")

def contracts():
    p,s,g,c=map(load,(P,S,G,C))
    assert p["probe_id"]==ID and p["status"]=="PREREGISTERED_BLOCKED_PENDING_PROVIDER_FREE_GATE"
    assert s["status"]=="PROVIDER_CONTRACT_FROZEN_SYNTHETIC_NOT_AUTHORIZED"
    assert c["status"]=="CONSUMED_OPERATIONAL_FAILURE_NO_MODEL_OUTPUT" and c["transition_rule"]["same_authorization_reuse"]=="FORBIDDEN"
    pv,rt,tr=s["provider"],s["routing_contract"],s["transport_contract"]
    assert (pv["gateway"],pv["model_id"],pv["upstream_provider_slug"],pv["credential_env"])==("openrouter",MODEL,UP,"OPENROUTER_API_KEY")
    assert pv["automatic_failover"] is False and pv["model_fallbacks"]==[]
    assert rt["only"]==[UP] and rt["order"]==[UP] and rt["allow_fallbacks"] is False and rt["require_parameters"] is True
    assert tr["package"]=="httpx" and tr["version"]==HX and tr["application_retries"]==0
    fp=g["frozen_pacing"]; assert g["status"]=="FROZEN_PROVIDER_FREE" and fp["minimum_seconds_between_any_provider_requests"]==75
    assert fp["automatic_retries"]==0 and fp["automatic_fallbacks"] is False
    calls=p["frozen_probe_calls"]; assert len(calls)==2 and [z["ordinal"] for z in calls]==[1,2]
    assert [z["probe"] for z in calls]==["strict_structured_output","forced_function_tool_call"]
    for z in calls:
        q=z["request_contract"]; assert q["model"]==MODEL and q["temperature"]==0 and q["max_tokens"]==4096
        assert q["reasoning"]=={"effort":"medium","exclude":True} and q["provider"]==ROUTE and q["stream"] is False
    assert calls[0]["request_contract"]["seed"]==524242 and calls[1]["request_contract"]["seed"]==524243
    assert calls[1]["request_contract"]["parallel_tool_calls"] is False
    return p,s,g,c

def selfcheck():
    p,s,g,c=contracts()
    return {"schema_version":"p12-c4-openrouter-synthetic-provider-free-self-check-v1",
      "status":"PASS_PROVIDER_FREE_LIVE_STILL_BLOCKED","provider_calls":0,"credentials_read":0,"network_io":0,
      "benchmark_inputs_loaded":0,"private_oracle_accesses":0,"fresh_blind_accesses":0,"legacy_locked_test_accesses":0,
      "prior_cerebras_authorization_reuse_allowed":False,"exact_frozen_probe_calls":2,
      "request_sha256":[h(z["request_contract"]) for z in p["frozen_probe_calls"]],"model_id":MODEL,"upstream_provider_slug":UP,
      "routing_contract":s["routing_contract"],"transport_contract":s["transport_contract"],
      "minimum_seconds_between_any_provider_requests":g["frozen_pacing"]["minimum_seconds_between_any_provider_requests"],
      "cerebras_closure_sha256":h(c),"live_probe_authorized":False,"next_gate":"SEPARATE_NEW_OPENROUTER_ONE_SHOT_AUTHORIZATION"}

def authorization():
    p,s,g,c=contracts(); sc=selfcheck()
    return {"schema_version":"p12-c4-openrouter-synthetic-probe-live-authorization-v1",
      "status":"AUTHORIZED_ONE_OPENROUTER_SYNTHETIC_PROBE_ATTEMPT","created_at_utc":datetime.now(timezone.utc).isoformat(),
      "probe_id":ID,"gateway":"openrouter","model_id":MODEL,"upstream_provider_slug":UP,
      "serving_contract_sha256":h(s),"preregistration_sha256":h(p),"prior_cerebras_closure_sha256":h(c),
      "provider_free_self_check_sha256":h(sc),"probe_request_sha256":[h(z["request_contract"]) for z in p["frozen_probe_calls"]],
      "minimum_seconds_between_any_provider_requests":g["frozen_pacing"]["minimum_seconds_between_any_provider_requests"],
      "authorized_attempts":1,"github_actions_run_attempt_required":1,"rerun_allowed":False,"automatic_retry_allowed":False,
      "provider_fallback_allowed":False,"model_fallback_allowed":False,"prior_cerebras_authorization_reuse_allowed":False,
      "exposed_pool_live_generation_authorized":False,"private_scoring_authorized":False,"fresh_blind_access_authorized":False,
      "legacy_locked_test_access_authorized":False,
      "authorization_scope":"AT_MOST_TWO_PREREGISTERED_SYNTHETIC_OPENROUTER_CALLS_ONLY_2_OF_2_REQUIRED_FOR_PASS"}

def check_auth(path):
    p,s,g,c=contracts(); a=load(path)
    assert a["schema_version"]=="p12-c4-openrouter-synthetic-probe-live-authorization-v1"
    assert a["status"]=="AUTHORIZED_ONE_OPENROUTER_SYNTHETIC_PROBE_ATTEMPT" and a["probe_id"]==ID
    for k in ("rerun_allowed","automatic_retry_allowed","provider_fallback_allowed","model_fallback_allowed","exposed_pool_live_generation_authorized"):
        assert a[k] is False
    assert a["authorized_attempts"]==a["github_actions_run_attempt_required"]==1
    assert a["serving_contract_sha256"]==h(s) and a["preregistration_sha256"]==h(p) and a["prior_cerebras_closure_sha256"]==h(c)
    assert a["probe_request_sha256"]==[h(z["request_contract"]) for z in p["frozen_probe_calls"]]
    assert a["minimum_seconds_between_any_provider_requests"]==g["frozen_pacing"]["minimum_seconds_between_any_provider_requests"]
    return a

def norm(v): return "".join(x for x in v.lower() if x.isalnum()) if isinstance(v,str) else ""
def common(x):
    if norm(x.get("provider"))!="openinference": raise Blocked(f"wrong provider {x.get('provider')!r}")
    if x.get("model") not in {"openai/gpt-oss-120b","openai/gpt-oss-120b:free"}: raise Blocked(f"wrong model {x.get('model')!r}")
    ch=x.get("choices"); 
    if not isinstance(ch,list) or len(ch)!=1: raise Blocked("expected one choice")
    m=ch[0].get("message") or {}
    if m.get("reasoning") not in (None,"") or m.get("reasoning_details") not in (None,[]): raise Blocked("reasoning not hidden")
    return ch[0]
def sem1(x):
    ch=common(x)
    if ch.get("finish_reason")!="stop": raise Blocked("structured finish mismatch")
    try: y=json.loads((ch.get("message") or {})["content"])
    except Exception as e: raise Blocked("structured output not JSON") from e
    if y!={"contract_marker":"P12-C4-OPENROUTER-SYNTHETIC","ok":True}: raise Blocked(f"structured mismatch {y!r}")
    return y
def sem2(x):
    ch=common(x)
    if ch.get("finish_reason")!="tool_calls": raise Blocked("tool finish mismatch")
    cs=(ch.get("message") or {}).get("tool_calls")
    if not isinstance(cs,list) or len(cs)!=1: raise Blocked("expected one tool call")
    z=cs[0]; f=z.get("function") or {}
    if z.get("type")!="function" or f.get("name")!="synthetic_lookup": raise Blocked("tool identity mismatch")
    a=f.get("arguments")
    if isinstance(a,str):
        try: a=json.loads(a)
        except Exception as e: raise Blocked("tool args not JSON") from e
    if not isinstance(a,dict) or a.get("marker")!="P12-C4-OPENROUTER-TOOL": raise Blocked("tool marker mismatch")
    return a
def headers(hd): 
    return {str(k).lower():str(v) for k,v in dict(hd).items() if str(k).lower() in {"x-request-id","request-id","retry-after"} or str(k).lower().startswith("x-ratelimit-")}

def live(auth,out):
    p,s,g,c=contracts(); a=check_auth(auth); key=os.environ.get("OPENROUTER_API_KEY")
    if not key: raise Blocked("OPENROUTER_API_KEY absent")
    import importlib.metadata, httpx
    if importlib.metadata.version("httpx")!=HX: raise Blocked("httpx pin mismatch")
    tr=s["transport_contract"]; to=httpx.Timeout(connect=tr["connect_timeout_seconds"],read=tr["read_timeout_seconds"],write=tr["write_timeout_seconds"],pool=tr["pool_timeout_seconds"])
    ev=[]; attempts=success=outputs=0; last=None
    try:
        with httpx.Client(timeout=to,transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
            for i,z in enumerate(p["frozen_probe_calls"]):
                if last is not None:
                    w=g["frozen_pacing"]["minimum_seconds_between_any_provider_requests"]-(time.monotonic()-last)
                    if w>0: time.sleep(w)
                q=z["request_contract"]; start=datetime.now(timezone.utc).isoformat(); t=time.monotonic(); attempts+=1
                r=client.post(URL,headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},json=q); last=time.monotonic()
                try: x=r.json()
                except Exception: x={"non_json_body_prefix":r.text[:500]}
                e={"ordinal":i+1,"probe":z["probe"],"started_at_utc":start,"elapsed_seconds":time.monotonic()-t,
                   "request":q,"request_sha256":h(q),"http_status":r.status_code,"response_headers_sanitized":headers(r.headers),"response":x,"response_sha256":h(x)}
                ev.append(e)
                if not 200<=r.status_code<300: raise Blocked(f"HTTP {r.status_code}: {json.dumps(x,ensure_ascii=False)[:800]}")
                success+=1
                if isinstance(x,dict) and x.get("choices"): outputs+=1
                y=sem1(x) if i==0 else sem2(x); e.update({"semantic_validation":y,"provider_identifier":x.get("provider"),"model_identifier":x.get("model"),"usage":x.get("usage")})
        res={"schema_version":"p12-c4-openrouter-synthetic-compatibility-probe-result-v1","probe_id":ID,"status":"PASS",
          "executed_at_utc":datetime.now(timezone.utc).isoformat(),"gateway":"openrouter","upstream_provider":"OpenInference","model_id_requested":MODEL,
          "provider_calls":2,"provider_request_attempts":attempts,"successful_http_responses":success,"model_outputs_observed":outputs,
          "automatic_retries":0,"provider_fallbacks":0,"model_fallbacks":0,"benchmark_inputs_loaded":0,"private_oracle_accesses":0,"fresh_blind_accesses":0,"legacy_locked_test_accesses":0,
          "serving_contract_sha256":h(s),"preregistration_sha256":h(p),"prior_cerebras_closure_sha256":h(c),"authorization_sha256":h(a),"calls":ev,
          "exposed_pool_live_generation_authorized_by_this_result":False,"next_gate":"FULL_PROVIDER_FREE_C4_ACTIVATION_AND_LIVE_MANIFEST_FREEZE"}
    except Exception as ex:
        res={"schema_version":"p12-c4-openrouter-synthetic-compatibility-probe-result-v1","probe_id":ID,"status":"BLOCKED_OR_FAIL",
          "executed_at_utc":datetime.now(timezone.utc).isoformat(),"error_type":type(ex).__name__,"error":str(ex),
          "provider_request_attempts":attempts,"successful_http_responses":success,"model_outputs_observed":outputs,
          "automatic_retries":0,"provider_fallbacks":0,"model_fallbacks":0,"benchmark_inputs_loaded":0,"private_oracle_accesses":0,"fresh_blind_accesses":0,"legacy_locked_test_accesses":0,
          "calls":ev,"exposed_pool_live_generation_authorized_by_this_result":False}
    write(out,res); return res

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--provider-free-contract-check",action="store_true"); ap.add_argument("--emit-authorization",type=Path)
    ap.add_argument("--authorization",type=Path,default=A); ap.add_argument("--output",type=Path,default=R/"research/results/p12-c4-openrouter-synthetic-compatibility-probe-result.json")
    z=ap.parse_args()
    if z.provider_free_contract_check: x=selfcheck()
    elif z.emit_authorization:
        if z.emit_authorization.exists(): raise Blocked("authorization already exists")
        x=authorization(); write(z.emit_authorization,x)
    else:
        try: x=live(z.authorization,z.output)
        except Exception as ex:
            x={"schema_version":"p12-c4-openrouter-synthetic-compatibility-probe-result-v1","probe_id":ID,"status":"BLOCKED_OR_FAIL","error_type":type(ex).__name__,"error":str(ex),
               "provider_request_attempts":0,"successful_http_responses":0,"model_outputs_observed":0,"automatic_retries":0,"provider_fallbacks":0,"model_fallbacks":0,
               "benchmark_inputs_loaded":0,"private_oracle_accesses":0,"fresh_blind_accesses":0,"legacy_locked_test_accesses":0,"calls":[],"exposed_pool_live_generation_authorized_by_this_result":False}
            write(z.output,x)
    print(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False))
    return 0 if x["status"] in {"PASS","PASS_PROVIDER_FREE_LIVE_STILL_BLOCKED","AUTHORIZED_ONE_OPENROUTER_SYNTHETIC_PROBE_ATTEMPT"} else 1
if __name__=="__main__": raise SystemExit(main())
