from __future__ import annotations
import json, os, time, urllib.error, urllib.request
from datetime import datetime, timezone
from typing import Any, Mapping

from academy_tractian.decision_source import ProviderDecisionPayload, build_provider_decision_request
from academy_tractian.provider_clients import PROVIDER_DECISION_JSON_SCHEMA, PROVIDER_DECISION_SYSTEM_INSTRUCTION
from academy_tractian.runtime import canonical_tool_registry
from research.e2.controller import ControllerContext

SCHEMA_VERSION = "provider-prompt-contract-probe-v1"
SYNTHETIC_ASSET_ID = "asset_prompt_probe_001"
EXPECTED_TOOL = "get_asset"
PROVIDERS = {
    "groq": {"token_env":"GROQ_API_KEY","endpoint":"https://api.groq.com/openai/v1/chat/completions","model":"openai/gpt-oss-120b"},
    "nvidia": {"token_env":"NVIDIA_API_KEY","endpoint":"https://integrate.api.nvidia.com/v1/chat/completions","model":"nvidia/llama-3.3-nemotron-super-49b-v1"},
    "openrouter": {"token_env":"OPENROUTER_API_KEY","endpoint":"https://openrouter.ai/api/v1/chat/completions","model":"nvidia/nemotron-3-super-120b-a12b:free"},
}

def canonical_json(v: Any)->str:
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def safe_error(p:Any)->dict[str,str]:
    if not isinstance(p,Mapping) or not isinstance(p.get("error"),Mapping): return {}
    e=p["error"]
    return {k:str(e[k])[:500] for k in ("type","code","message") if e.get(k) is not None}

def request_body(pid:str,model:str,text:str)->dict[str,Any]:
    b={"model":model,"messages":[{"role":"system","content":PROVIDER_DECISION_SYSTEM_INSTRUCTION},{"role":"user","content":text}],"temperature":0,"n":1,"stream":False}
    if pid=="groq":
        b.update({"max_completion_tokens":512,"reasoning_effort":"medium","response_format":{"type":"json_schema","json_schema":{"name":"provider_decision_payload","strict":False,"schema":json.loads(json.dumps(PROVIDER_DECISION_JSON_SCHEMA))}}})
    elif pid=="nvidia":
        b.update({"max_tokens":512,"response_format":{"type":"json_object"}})
    elif pid=="openrouter":
        b.update({"max_completion_tokens":512,"response_format":{"type":"json_schema","json_schema":{"name":"provider_decision_payload","strict":False,"schema":json.loads(json.dumps(PROVIDER_DECISION_JSON_SCHEMA))}},"provider":{"require_parameters":True,"allow_fallbacks":False}})
    else:
        raise RuntimeError(f"unsupported_provider:{pid}")
    return b

def extract(p:Any):
    if not isinstance(p,Mapping): return None,None,None,None,None
    model=p.get("model") if isinstance(p.get("model"),str) else None
    c=None
    choices=p.get("choices")
    if isinstance(choices,list) and len(choices)==1 and isinstance(choices[0],Mapping):
        m=choices[0].get("message")
        if isinstance(m,Mapping) and isinstance(m.get("content"),str): c=m["content"]
    u=p.get("usage") if isinstance(p.get("usage"),Mapping) else {}
    iv=lambda x: x if isinstance(x,int) and not isinstance(x,bool) else None
    return c,model,iv(u.get("prompt_tokens")),iv(u.get("completion_tokens")),iv(u.get("total_tokens"))

def main()->int:
    pid=os.environ.get("PROVIDER_PROMPT_PROBE_PROVIDER","").strip().lower()
    if pid not in PROVIDERS:
        raise RuntimeError("PROVIDER_PROMPT_PROBE_PROVIDER must be groq, nvidia, or openrouter")
    cfg=PROVIDERS[pid]
    token=os.environ.get(cfg["token_env"],"").strip()
    if not token:
        raise RuntimeError(f"missing:{cfg['token_env']}")
    registry=canonical_tool_registry()
    if EXPECTED_TOOL not in registry:
        raise RuntimeError(f"missing_canonical_tool:{EXPECTED_TOOL}")
    ctx=ControllerContext(user_request=f"Synthetic provider-contract probe only; no industrial benchmark data is present. Propose the canonical {EXPECTED_TOOL} tool with asset_id exactly {SYNTHETIC_ASSET_ID!r}. Do not execute the tool.",turn_index=0,tool_call_count=0)
    dr=build_provider_decision_request(context=ctx,registry=registry)
    body=request_body(pid,cfg["model"],canonical_json(dr.model_dump(mode="json")))
    req=urllib.request.Request(cfg["endpoint"],data=canonical_json(body).encode(),method="POST",headers={"Authorization":f"Bearer {token}","Content-Type":"application/json","Accept":"application/json","User-Agent":"academy-tractian-provider-prompt-contract-probe/1.0"})
    started=time.perf_counter_ns(); raw=""; headers={}
    try:
        with urllib.request.urlopen(req,timeout=90) as r:
            status=int(r.status); raw=r.read().decode("utf-8",errors="replace"); headers={k.casefold():v for k,v in r.headers.items()}
    except urllib.error.HTTPError as e:
        status=int(e.code); raw=e.read().decode("utf-8",errors="replace"); headers={k.casefold():v for k,v in e.headers.items()}
    except Exception:
        status=None
    latency_ms=max(0,time.perf_counter_ns()-started)//1_000_000
    try:
        payload=json.loads(raw) if raw else {}
    except Exception:
        payload={}
    content,served_model,prompt_tokens,completion_tokens,total_tokens=extract(payload)
    parsed=None; parse_ok=False; semantic_ok=False
    if isinstance(content,str) and content.strip():
        try:
            parsed=ProviderDecisionPayload.model_validate_json(content); parse_ok=True
            semantic_ok=(parsed.kind.value=="TOOL" and parsed.tool_name==EXPECTED_TOOL and parsed.arguments.get("asset_id")==SYNTHETIC_ASSET_ID and parsed.final is None and parsed.message is None and parsed.reason_code is None)
        except Exception:
            pass
    rate={k:v for k,v in headers.items() if k.startswith("x-ratelimit-") or k in {"retry-after","date"}}
    result="PASS" if status==200 and parse_ok and semantic_ok else "FAIL"
    report={"schema_version":SCHEMA_VERSION,"checked_at":datetime.now(timezone.utc).isoformat(),"provider_id":pid,"route":cfg["endpoint"].replace("https://",""),"requested_model":cfg["model"],"served_model":served_model,"http_status":status,"latency_ms":latency_ms,"provider_decision_parse_ok":parse_ok,"synthetic_semantic_contract_ok":semantic_ok,"decision_kind":parsed.kind.value if parsed else None,"decision_tool_name":parsed.tool_name if parsed else None,"prompt_tokens":prompt_tokens,"completion_tokens":completion_tokens,"total_tokens":total_tokens,"rate_headers":rate,"error":safe_error(payload),"benchmark_inputs_loaded":0,"raw_provider_material_recorded":False,"credentials_recorded":False,"result":result}
    print("PROVIDER_PROMPT_CONTRACT_PROBE="+canonical_json(report),flush=True)
    return 0 if result=="PASS" else 2

if __name__=="__main__":
    raise SystemExit(main())
