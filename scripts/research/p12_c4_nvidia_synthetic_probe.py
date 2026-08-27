#!/usr/bin/env python3
"""P12-C4 NVIDIA hosted NIM synthetic gate. Fail closed; no retries/fallbacks."""
from __future__ import annotations
import argparse, hashlib, json, os, time
from datetime import datetime, timezone
from pathlib import Path

R=Path(__file__).resolve().parents[2]
P=R/"research/experiments/p12-c4-nvidia-synthetic-compatibility-probe-preregistration-v1.json"
S=R/"research/experiments/p12-c4-nvidia-provider-serving-contract-v1.json"
G=R/"research/frozen/p12-c4-nvidia-request-budget-and-pacing-v1.json"
CC=R/"research/results/p12-c4-cerebras-synthetic-live-probe-closure-2026-08-25.json"
OC=R/"research/results/p12-c4-openrouter-synthetic-live-probe-closure-2026-08-26.json"
A=R/"research/frozen/p12-c4-nvidia-synthetic-probe-live-authorization-v1.json"
ID="P12-C4-NVIDIA-SYNTHETIC-COMPATIBILITY-V1"; MODEL="openai/gpt-oss-120b"
URL="https://integrate.api.nvidia.com/v1/chat/completions"; HX="0.28.1"

class Blocked(RuntimeError): pass
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def h(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def write(p,x):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")

def contracts():
    p,s,g,cc,oc=map(load,(P,S,G,CC,OC))
    assert p["probe_id"]==ID and p["status"]=="PREREGISTERED_BLOCKED_PENDING_PROVIDER_FREE_GATE"
    assert s["status"]=="PROVIDER_CONTRACT_FROZEN_SYNTHETIC_NOT_AUTHORIZED"
    assert cc["status"]==oc["status"]=="CONSUMED_OPERATIONAL_FAILURE_NO_MODEL_OUTPUT"
    assert cc["transition_rule"]["same_authorization_reuse"]=="FORBIDDEN"
    assert oc["authorization"]["same_authorization_reuse"]=="FORBIDDEN"
    pv,tr=s["provider"],s["transport_contract"]; fp=g["frozen_pacing"]
    assert pv["endpoint"]==URL and pv["model_id"]==MODEL and pv["credential_env"]=="NVIDIA_API_KEY"
    assert pv["automatic_failover"] is False and pv["model_fallbacks"]==[]
    assert tr["version"]==HX and tr["application_retries"]==0 and tr["follow_redirects"] is False
    assert fp["minimum_seconds_between_any_provider_requests"]==75 and fp["automatic_retries"]==0
    assert fp["automatic_fallbacks"] is False and fp["synthetic_authorization_maximum_request_attempts"]==2
    assert fp["full_packet_capacity_authorized"] is False
    calls=p["frozen_probe_calls"]; assert len(calls)==2
    for z in calls:
        q=z["request_contract"]
        assert q["model"]==MODEL and q["temperature"]==0 and q["max_tokens"]==4096
        assert q["reasoning_effort"]=="medium" and q["stream"] is False and isinstance(q["seed"],int)
    assert calls[0]["request_contract"]["seed"]==624242
    assert calls[0]["request_contract"]["response_format"]["json_schema"]["strict"] is True
    assert calls[1]["request_contract"]["seed"]==624243
    assert calls[1]["request_contract"]["parallel_tool_calls"] is False
    assert calls[1]["request_contract"]["tool_choice"]["function"]["name"]=="synthetic_lookup"
    return p,s,g,cc,oc

def selfcheck():
    p,s,g,cc,oc=contracts()
    return {"schema_version":"p12-c4-nvidia-synthetic-provider-free-self-check-v1",
      "status":"PASS_PROVIDER_FREE_LIVE_STILL_BLOCKED","provider_calls":0,"credentials_read":0,"network_io":0,
      "benchmark_inputs_loaded":0,"private_oracle_accesses":0,"fresh_blind_accesses":0,"legacy_locked_test_accesses":0,
      "prior_cerebras_authorization_reuse_allowed":False,"prior_openrouter_authorization_reuse_allowed":False,
      "exact_frozen_probe_calls":2,"request_sha256":[h(z["request_contract"]) for z in p["frozen_probe_calls"]],
      "model_id":MODEL,"endpoint":URL,"serving_contract_sha256":h(s),"preregistration_sha256":h(p),"pacing_sha256":h(g),
      "cerebras_closure_sha256":h(cc),"openrouter_closure_sha256":h(oc),
      "minimum_seconds_between_any_provider_requests":75,"live_probe_authorized":False,
      "full_packet_capacity_authorized":False,"next_gate":"SEPARATE_NEW_NVIDIA_ONE_SHOT_AUTHORIZATION"}

def authorization():
    p,s,g,cc,oc=contracts(); sc=selfcheck()
    return {"schema_version":"p12-c4-nvidia-synthetic-probe-live-authorization-v1",
      "status":"AUTHORIZED_ONE_NVIDIA_SYNTHETIC_PROBE_ATTEMPT","created_at_utc":datetime.now(timezone.utc).isoformat(),
      "probe_id":ID,"hosting_path":"nvidia_hosted_nim","endpoint":URL,"model_id":MODEL,
      "serving_contract_sha256":h(s),"preregistration_sha256":h(p),"pacing_sha256":h(g),
      "prior_cerebras_closure_sha256":h(cc),"prior_openrouter_closure_sha256":h(oc),
      "provider_free_self_check_sha256":h(sc),"probe_request_sha256":[h(z["request_contract"]) for z in p["frozen_probe_calls"]],
      "minimum_seconds_between_any_provider_requests":75,"authorized_attempts":1,"github_actions_run_attempt_required":1,
      "maximum_provider_request_attempts":2,"rerun_allowed":False,"automatic_retry_allowed":False,
      "provider_fallback_allowed":False,"model_fallback_allowed":False,
      "prior_cerebras_authorization_reuse_allowed":False,"prior_openrouter_authorization_reuse_allowed":False,
      "exposed_pool_live_generation_authorized":False,"full_packet_capacity_authorized":False,
      "private_scoring_authorized":False,"fresh_blind_access_authorized":False,"legacy_locked_test_access_authorized":False,
      "authorization_scope":"AT_MOST_TWO_PREREGISTERED_SYNTHETIC_NVIDIA_CALLS_ONLY_2_OF_2_REQUIRED_FOR_PASS"}

def check_auth(path):
    p,s,g,cc,oc=contracts(); a=load(path)
    assert a["schema_version"]=="p12-c4-nvidia-synthetic-probe-live-authorization-v1"
    assert a["status"]=="AUTHORIZED_ONE_NVIDIA_SYNTHETIC_PROBE_ATTEMPT" and a["probe_id"]==ID
    for k in ("rerun_allowed","automatic_retry_allowed","provider_fallback_allowed","model_fallback_allowed",
              "prior_cerebras_authorization_reuse_allowed","prior_openrouter_authorization_reuse_allowed",
              "exposed_pool_live_generation_authorized","full_packet_capacity_authorized"):
        assert a[k] is False
    assert a["authorized_attempts"]==a["github_actions_run_attempt_required"]==1
    assert a["maximum_provider_request_attempts"]==2
    assert a["serving_contract_sha256"]==h(s) and a["preregistration_sha256"]==h(p) and a["pacing_sha256"]==h(g)
    assert a["prior_cerebras_closure_sha256"]==h(cc) and a["prior_openrouter_closure_sha256"]==h(oc)
    assert a["probe_request_sha256"]==[h(z["request_contract"]) for z in p["frozen_probe_calls"]]
    return a

def projection(x):
    if not isinstance(x,dict): return {}
    out={"model":x.get("model"),"usage":x.get("usage"),"choices":[]}
    for c in (x.get("choices") or [])[:1]:
        m=c.get("message") or {}
        out["choices"].append({"finish_reason":c.get("finish_reason"),
          "message":{"role":m.get("role"),"content":m.get("content"),"tool_calls":m.get("tool_calls")}})
    return out
def one(x):
    if not isinstance(x,dict) or "gpt-oss-120b" not in str(x.get("model","")).lower(): raise Blocked("wrong model")
    ch=x.get("choices")
    if not isinstance(ch,list) or len(ch)!=1: raise Blocked("expected one choice")
    return ch[0]
def sem1(x):
    ch=one(x)
    if ch.get("finish_reason")!="stop": raise Blocked("structured finish mismatch")
    try: y=json.loads((ch.get("message") or {}).get("content") or "")
    except Exception as e: raise Blocked("structured output not JSON") from e
    if y!={"contract_marker":"P12-C4-NVIDIA-SYNTHETIC","ok":True}: raise Blocked(f"structured mismatch {y!r}")
    return y
def sem2(x):
    ch=one(x); cs=(ch.get("message") or {}).get("tool_calls")
    if not isinstance(cs,list) or len(cs)!=1: raise Blocked(f"expected one tool call, finish={ch.get('finish_reason')!r}")
    z=cs[0]; f=z.get("function") or {}
    if z.get("type")!="function" or f.get("name")!="synthetic_lookup": raise Blocked("tool identity mismatch")
    a=f.get("arguments")
    if isinstance(a,str):
        try: a=json.loads(a)
        except Exception as e: raise Blocked("tool args not JSON") from e
    if not isinstance(a,dict) or a.get("marker")!="P12-C4-NVIDIA-TOOL": raise Blocked("tool marker mismatch")
    return a
def sh(raw): return hashlib.sha256(raw).hexdigest()
def hdrs(hd):
    allow={"x-request-id","request-id","retry-after","x-ratelimit-limit","x-ratelimit-remaining","x-ratelimit-reset"}
    return {str(k).lower():str(v) for k,v in dict(hd).items() if str(k).lower() in allow}

def live(auth,out):
    p,s,g,cc,oc=contracts(); a=check_auth(auth); key=os.environ.get("NVIDIA_API_KEY")
    if not key: raise Blocked("NVIDIA_API_KEY absent")
    import importlib.metadata, httpx
    if importlib.metadata.version("httpx")!=HX: raise Blocked("httpx pin mismatch")
    tr=s["transport_contract"]; tmo=httpx.Timeout(connect=tr["connect_timeout_seconds"],read=tr["read_timeout_seconds"],write=tr["write_timeout_seconds"],pool=tr["pool_timeout_seconds"])
    ev=[]; attempts=success=outputs=0; last=None
    try:
        with httpx.Client(timeout=tmo,transport=httpx.HTTPTransport(retries=0),follow_redirects=False) as client:
            for i,z in enumerate(p["frozen_probe_calls"]):
                if last is not None:
                    w=75-(time.monotonic()-last)
                    if w>0: time.sleep(w)
                q=z["request_contract"]; started=datetime.now(timezone.utc).isoformat(); t=time.monotonic(); attempts+=1
                r=client.post(URL,headers={"Authorization":f"Bearer {key}","Content-Type":"application/json","Accept":"application/json"},json=q)
                last=time.monotonic()
                try: x=r.json()
                except Exception: x={}
                px=projection(x); e={"ordinal":i+1,"probe":z["probe"],"started_at_utc":started,"elapsed_seconds":last-t,
                  "request":q,"request_sha256":h(q),"http_status":r.status_code,"response_headers_sanitized":hdrs(r.headers),
                  "raw_response_sha256":sh(r.content),"sanitized_response":px,"sanitized_response_sha256":h(px)}
                ev.append(e)
                if not 200<=r.status_code<300: raise Blocked(f"HTTP {r.status_code}; sanitized_response={json.dumps(px)[:600]}")
                success+=1
                if x.get("choices"): outputs+=1
                e["semantic_validation"]=sem1(x) if i==0 else sem2(x)
                e["model_identifier"]=x.get("model"); e["usage"]=x.get("usage")
        res={"schema_version":"p12-c4-nvidia-synthetic-compatibility-probe-result-v1","probe_id":ID,"status":"PASS",
          "executed_at_utc":datetime.now(timezone.utc).isoformat(),"provider_calls":2,"provider_request_attempts":attempts,
          "successful_http_responses":success,"model_outputs_observed":outputs,"automatic_retries":0,"provider_fallbacks":0,"model_fallbacks":0,
          "benchmark_inputs_loaded":0,"private_oracle_accesses":0,"fresh_blind_accesses":0,"legacy_locked_test_accesses":0,
          "reasoning_content_persisted":False,"provider_account_identifiers_persisted":False,
          "serving_contract_sha256":h(s),"preregistration_sha256":h(p),"pacing_sha256":h(g),"authorization_sha256":h(a),
          "prior_cerebras_closure_sha256":h(cc),"prior_openrouter_closure_sha256":h(oc),
          "minimum_seconds_between_any_provider_requests":75,"calls":ev,
          "exposed_pool_live_generation_authorized_by_this_result":False,"full_packet_capacity_authorized_by_this_result":False,
          "next_gate":"FULL_PROVIDER_FREE_C4_ACTIVATION_AND_CAPACITY_GATE"}
    except Exception as ex:
        res={"schema_version":"p12-c4-nvidia-synthetic-compatibility-probe-result-v1","probe_id":ID,"status":"BLOCKED_OR_FAIL",
          "executed_at_utc":datetime.now(timezone.utc).isoformat(),"error_type":type(ex).__name__,"error":str(ex),
          "provider_request_attempts":attempts,"successful_http_responses":success,"model_outputs_observed":outputs,
          "automatic_retries":0,"provider_fallbacks":0,"model_fallbacks":0,"benchmark_inputs_loaded":0,"private_oracle_accesses":0,
          "fresh_blind_accesses":0,"legacy_locked_test_accesses":0,"reasoning_content_persisted":False,
          "provider_account_identifiers_persisted":False,"calls":ev,"exposed_pool_live_generation_authorized_by_this_result":False,
          "full_packet_capacity_authorized_by_this_result":False}
    write(out,res); return res

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--provider-free-contract-check",action="store_true")
    ap.add_argument("--emit-authorization",type=Path); ap.add_argument("--authorization",type=Path,default=A)
    ap.add_argument("--output",type=Path,default=R/"research/results/p12-c4-nvidia-synthetic-compatibility-probe-result.json")
    z=ap.parse_args()
    if z.provider_free_contract_check: x=selfcheck()
    elif z.emit_authorization:
        if z.emit_authorization.exists(): raise Blocked("authorization already exists")
        x=authorization(); write(z.emit_authorization,x)
    else: x=live(z.authorization,z.output)
    print(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False))
    return 0 if x["status"] in {"PASS","PASS_PROVIDER_FREE_LIVE_STILL_BLOCKED","AUTHORIZED_ONE_NVIDIA_SYNTHETIC_PROBE_ATTEMPT"} else 1
if __name__=="__main__": raise SystemExit(main())
