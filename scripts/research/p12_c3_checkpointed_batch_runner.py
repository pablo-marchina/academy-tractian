#!/usr/bin/env python3
from __future__ import annotations

"""P12-C3 checkpointed six-batch collection over the qualified P12-C2 runner.

One workflow cell job handles at most one predeclared parent. Controlled
pre-output capacity pauses persist a checkpoint and may resume; any unexpected
job failure after provider execution is fail-closed and may not be retried.
"""
import argparse, hashlib, importlib.util, json, math, os, time, urllib.error, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

EXP="P12-C3_EXPOSED_POOL_CAPACITY_CONTROLLED_FACTORIAL"
ACT="P12-C3-CAPACITY-ACTIVATION-2026-08-23"
SCOPE="ONE_P12_C3_CAPACITY_CONTROLLED_A00_A10_A01_A11_EXPOSED_POOL_EXPERIMENT_WITH_SIX_FIXED_BATCHES"
PARENT_CFG="9033a78a5bab46e4c48ebfc0ec70b6476570519fa62f0526625916d0cd3d3b89"
SEEDS=[2026082307,2026082308,2026082309]
ARMS=["A00","A10","A01","A11"]
SCHEMA="p12-c3-private-checkpoint-v1"
INLINE_WAIT_MAX=1800


def load(p:Path): return json.loads(p.read_text(encoding="utf-8"))
def write(p:Path,v:Any):
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+".tmp"); t.write_text(json.dumps(v,indent=2),encoding="utf-8"); os.replace(t,p)
def mod(name:str,p:Path):
    s=importlib.util.spec_from_file_location(name,p); assert s and s.loader; m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def now(): return datetime.now(timezone.utc)
def dt(v):
    if not v:return None
    x=datetime.fromisoformat(str(v).replace("Z","+00:00")); return (x if x.tzinfo else x.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
def h(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def cells(bm): return [c for b in bm["batches"] for c in b["cells"]]
def bids(bm): return {b["batch_id"]:b for b in bm["batches"]}
def ids(bm): return {str(c["cell_id"]) for c in cells(bm)}


def static(a,bm):
    assert a["experiment_id"]==EXP and a["activation_id"]==ACT
    assert a["status"]=="ACTIVATION_ELIGIBILITY_PASS" and a["execution_authorized"] is True
    assert int(a["authorized_live_experiments"])==1 and a["authorized_scope_if_passed"]==SCOPE
    assert a["candidate_definition_changed_from_p12_c2"] is False and a["common_parent_config_sha256"]==PARENT_CFG
    g=a["collection_geometry"]; assert g["seeds"]==SEEDS and g["common_parent_cells"]==36 and g["fixed_batches"]==6 and g["parents_per_batch"]==6 and g["expected_fixed_arm_outputs"]==144
    assert bm["status"]=="FROZEN" and bm["expected_cells"]==36 and len(cells(bm))==36 and len(ids(bm))==36 and bm["seed_schedule"]==SEEDS


def fresh(execution,bm):
    x=[str(c["cell_id"]) for c in cells(bm)]
    return {"schema_version":SCHEMA,"experiment_id":EXP,"execution_id":execution,"first_live_call_at":None,"horizon_deadline":None,"completed":{},"pending":x,"pre_output_attempt_counts":{k:0 for k in x},"transport_failure_count":0,"rate_limit_event_count":0,"provider_reset_timestamp_or_duration":None,"last_request_at":None,"last_capacity_snapshot":None,"cell_resume_at":{},"terminal_failure":None,"checkpoint_version":0}


def valid(cap,cp,bm,execution):
    assert cp["schema_version"]==SCHEMA and cp["experiment_id"]==EXP and cp["execution_id"]==execution
    cap.validate_checkpoint(cp,ids(bm)); assert cp.get("terminal_failure") is None
    for k in ids(bm): assert 0<=int(cp["pre_output_attempt_counts"].get(k,0))<=cap.MAX_PRE_OUTPUT_TRANSPORT_ATTEMPTS_PER_CELL
    f,z=dt(cp.get("first_live_call_at")),dt(cp.get("horizon_deadline")); assert (f is None)==(z is None)
    if f: assert z==f+timedelta(hours=cap.MAX_COLLECTION_HOURS)


def sequence(cp,bm,batch):
    bs=bids(bm); assert batch in bs; o=int(bs[batch]["ordinal"]); done=set(cp["completed"])
    for b in bm["batches"]:
        s={str(c["cell_id"]) for c in b["cells"]}; bo=int(b["ordinal"])
        if bo<o: assert s<=done
        if bo>o: assert not(s&done)
    seen=False
    for c in bs[batch]["cells"]:
        k=str(c["cell_id"])
        if k not in done: seen=True
        elif seen: raise AssertionError("non-prefix checkpoint inside selected batch")


def pub(cap,cp,batch):
    r=cap.public_checkpoint_record(cp)
    return {"schema_version":"p12-c3-public-checkpoint-v1","experiment_id":EXP,"batch_id":batch,**r,"first_live_call_at":cp.get("first_live_call_at"),"horizon_deadline":cp.get("horizon_deadline"),"terminal_failure_present":cp.get("terminal_failure") is not None,"raw_outputs_present":False,"private_oracle_present":False}
def persist(cap,cp,raw,public,batch): cp["checkpoint_version"]=int(cp.get("checkpoint_version",0))+1; write(raw,cp); write(public,pub(cap,cp,batch))


def prepare(a):
    ac,bm,cap=load(a.activation),load(a.batch_map),mod("c3cap",a.capacity_control); static(ac,bm)
    cp=load(a.checkpoint_in) if a.checkpoint_in and a.checkpoint_in.exists() else fresh(a.execution_id,bm)
    if not (a.checkpoint_in and a.checkpoint_in.exists()): assert a.allow_initialize and a.batch_id=="B1"
    valid(cap,cp,bm,a.execution_id); sequence(cp,bm,a.batch_id)
    f=dt(cp.get("first_live_call_at")); assert not f or cap.within_horizon(f,now())
    persist(cap,cp,a.checkpoint_out,a.public_out,a.batch_id); return 0


def token_est(payload): return math.ceil(len(json.dumps(payload.get("messages",[]),ensure_ascii=False).encode())/4)+int(payload.get("max_completion_tokens") or 0)
def snap(headers:Mapping[str,str],cap,t):
    x=cap.normalized_headers(headers); deadline=cap.provider_wait_deadline(x,t)
    def n(k):
        try:return int(x[k])
        except:return None
    return {"observed_at":t.isoformat(),"remaining_requests":n("x-ratelimit-remaining-requests"),"remaining_tokens":n("x-ratelimit-remaining-tokens"),"reset_deadline_with_margin":deadline.isoformat() if deadline else None}


class Pause(Exception):
    def __init__(self,reason,resume=None): self.reason,self.resume=reason,resume

class C3Post:
    def __init__(self,runner,cap,cp,cell,raw,public,batch): self.r,self.cap,self.cp,self.cell,self.raw,self.public,self.batch=runner,cap,cp,cell,raw,public,batch; self.response_seen=False; self.last=None
    def save(self): persist(self.cap,self.cp,self.raw,self.public,self.batch)
    def horizon(self):
        t=now(); f=dt(self.cp.get("first_live_call_at"))
        if not f: self.cp["first_live_call_at"]=t.isoformat(); self.cp["horizon_deadline"]=self.cap.horizon_deadline(t).isoformat(); self.save(); return
        if not self.cap.within_horizon(f,t): raise RuntimeError("c3_terminal_pre_output:COLLECTION_HORIZON_EXPIRED")
    def delay(self):
        x=dt(self.cp.get("last_request_at")); rem=self.cap.MIN_INTER_REQUEST_DELAY_SECONDS-(now()-x).total_seconds() if x else 0
        if rem>0: time.sleep(rem)
    def headroom(self,payload):
        s=self.cp.get("last_capacity_snapshot"); t=now()
        if not isinstance(s,dict): return
        reset=dt(s.get("reset_deadline_with_margin"));
        if reset and reset<=t:return
        need=token_est(payload); rr,rt=s.get("remaining_requests"),s.get("remaining_tokens"); bad=(isinstance(rr,int) and rr<1) or (isinstance(rt,int) and rt<need)
        if not bad:return
        if not reset: raise RuntimeError("c3_terminal_pre_output:INSUFFICIENT_HEADROOM_NO_RESET_METADATA")
        wait=max(0,(reset-t).total_seconds())
        if wait>INLINE_WAIT_MAX: self.cp["cell_resume_at"][self.cell]=reset.isoformat(); self.cp["provider_reset_timestamp_or_duration"]=reset.isoformat(); self.save(); raise Pause("PROACTIVE_HEADROOM_PAUSE",reset.isoformat())
        if wait: time.sleep(wait)
    def __call__(self,url,headers,payload,timeout):
        if not self.response_seen:
            resume=dt(self.cp.get("cell_resume_at",{}).get(self.cell));
            if resume and now()<resume: raise Pause("RESET_WINDOW_NOT_REACHED",resume.isoformat())
            self.horizon(); self.headroom(payload)
        else:
            s=self.last or self.cp.get("last_capacity_snapshot"); reset=dt(s.get("reset_deadline_with_margin")) if isinstance(s,dict) else None
            need=token_est(payload); rr=s.get("remaining_requests") if isinstance(s,dict) else None; rt=s.get("remaining_tokens") if isinstance(s,dict) else None
            if (isinstance(rr,int) and rr<1) or (isinstance(rt,int) and rt<need):
                if not reset: raise RuntimeError("c3_terminal_post_output:REPAIR_HEADROOM_NO_RESET")
                wait=max(0,(reset-now()).total_seconds())
                if wait>INLINE_WAIT_MAX: raise RuntimeError("c3_terminal_post_output:REPAIR_WAIT_EXCEEDS_INLINE_WINDOW")
                if wait: time.sleep(wait)
        attempts=int(self.cp["pre_output_attempt_counts"].get(self.cell,0))
        if not self.response_seen and attempts>=self.cap.MAX_PRE_OUTPUT_TRANSPORT_ATTEMPTS_PER_CELL: raise RuntimeError("c3_terminal_pre_output:ATTEMPTS_EXHAUSTED")
        self.delay(); t=now(); self.cp["last_request_at"]=t.isoformat()
        if not self.response_seen: self.cp["pre_output_attempt_counts"][self.cell]=attempts+1
        self.save()
        rh={"Accept":"application/json","Content-Type":"application/json","User-Agent":os.getenv("E8_HTTP_USER_AGENT",self.r.transport.DEFAULT_USER_AGENT),**headers}
        req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers=rh,method="POST")
        try:
            with urllib.request.urlopen(req,timeout=timeout) as resp:
                data=json.loads(resp.read().decode()); self.last=snap(dict(resp.headers.items()),self.cap,now()); self.cp["last_capacity_snapshot"]=self.last; self.cp["provider_reset_timestamp_or_duration"]=self.last.get("reset_deadline_with_margin"); self.response_seen=True; self.save()
                return data,{"provider_attempts":1,"rate_limit_events":0,"provider_retry_wait_seconds_total":0.0,"c3_capacity_snapshot":self.last}
        except urllib.error.HTTPError as e:
            body=e.read().decode(errors="replace"); self.cp["transport_failure_count"]+=1
            if int(e.code)==429:self.cp["rate_limit_event_count"]+=1
            self.save(); category=self.r.transport.classify_failure(int(e.code),body)
            if self.response_seen: raise RuntimeError("c3_terminal_post_output:"+category)
            if int(e.code)==429:
                d=self.cap.rate_limit_decision(429,dict(e.headers.items()),False,now()); resume=dt(d.get("resume_at"));
                if d.get("abort_batch") or not resume: raise RuntimeError("c3_terminal_pre_output:RATE_LIMIT_NO_RESET_METADATA")
                self.cp["provider_reset_timestamp_or_duration"]=resume.isoformat(); self.cp["cell_resume_at"][self.cell]=resume.isoformat(); self.save(); raise Pause("RATE_LIMIT_PAUSE",resume.isoformat())
            if int(e.code) in {408,409,425,500,502,503,504}:
                resume=now()+timedelta(seconds=self.cap.MIN_INTER_REQUEST_DELAY_SECONDS); self.cp["cell_resume_at"][self.cell]=resume.isoformat(); self.save(); raise Pause("TRANSIENT_TRANSPORT_PAUSE",resume.isoformat())
            raise RuntimeError("c3_terminal_pre_output:"+category)
        except Pause: raise
        except Exception as e:
            self.cp["transport_failure_count"]+=1; self.save(); category=self.r.transport.classify_failure(None,str(e))
            if self.response_seen: raise RuntimeError("c3_terminal_post_output:"+category)
            if category=="network_or_transient_failure":
                resume=now()+timedelta(seconds=self.cap.MIN_INTER_REQUEST_DELAY_SECONDS); self.cp["cell_resume_at"][self.cell]=resume.isoformat(); self.save(); raise Pause("TRANSIENT_TRANSPORT_PAUSE",resume.isoformat())
            raise RuntimeError("c3_terminal_pre_output:"+category)


def run_cell(a):
    ac,bm,cap,runner=load(a.activation),load(a.batch_map),mod("c3capcell",a.capacity_control),mod("c3base",a.base_runner); static(ac,bm)
    cp=load(a.checkpoint_in); valid(cap,cp,bm,a.execution_id); sequence(cp,bm,a.batch_id); batch=bids(bm)[a.batch_id]; cell=batch["cells"][a.cell_ordinal-1]; cid=str(cell["cell_id"])
    assert all(str(c["cell_id"]) in cp["completed"] for c in batch["cells"][:a.cell_ordinal-1])
    if cid in cp["completed"]:
        write(a.checkpoint_out,cp); write(a.public_out,pub(cap,cp,a.batch_id)); write(a.cell_summary,{"status":"SKIPPED_ALREADY_COMPLETE","continue_with_batch":True,"cell_id":cid,"provider_call_made":False}); return 0
    runner.assert_no_private_files(); os.environ["E14_MAX_RETRIES"]="0"
    if not a.dry_run:
        runner.e14o.e14l.assert_frozen_configuration(dry_run=False); runner.e14o.e14l.schema.run_self_checks(); runner.base.assert_zero_cost_guard("groq",False); assert os.getenv("GROQ_API_KEY")
    cases=runner.exact_case_by_ticket(load(a.agent_input_cases)); case=cases[str(cell["ticket_id"])]; assert str(case["asset_id"])==str(cell["group_id"]); split=runner.source_split_for_group(load(a.split_manifest),str(cell["group_id"])); assert split in {"DEV","VALIDATION"}
    ctl=C3Post(runner,cap,cp,cid,a.checkpoint_out,a.public_out,a.batch_id); old=runner.transport.post_json; runner.transport.post_json=ctl
    try:
        rec=runner.generate_one(mapping=cell,visible_case=case,source_split=split,seed=int(cell["seed"]),repeat_index=int(cell["repeat_index"]),timeout=a.timeout_seconds,dry_run=a.dry_run,is_first_call=True)
    except Pause as e:
        persist(cap,cp,a.checkpoint_out,a.public_out,a.batch_id); write(a.cell_summary,{"status":"PAUSED_PRE_OUTPUT","continue_with_batch":False,"terminal":False,"cell_id":cid,"reason":e.reason,"resume_at":e.resume,"provider_call_made":not a.dry_run}); return 0
    except RuntimeError as e:
        reason=str(e); post=reason.startswith("c3_terminal_post_output:"); cp["terminal_failure"]={"cell_id":cid,"batch_id":a.batch_id,"reason":reason,"post_initial_output":post,"recorded_at":now().isoformat()}; persist(cap,cp,a.checkpoint_out,a.public_out,a.batch_id); write(a.cell_summary,{"status":"TERMINAL_EXPERIMENT_FAILURE","continue_with_batch":False,"terminal":True,"cell_id":cid,"reason":reason,"provider_call_made":not a.dry_run}); return 0
    finally: runner.transport.post_json=old
    if rec.get("success") is not True:
        reason=str(rec.get("error_category") or "UNKNOWN_PARENT_FAILURE"); cp["terminal_failure"]={"cell_id":cid,"batch_id":a.batch_id,"reason":reason,"post_initial_output":not reason.startswith("c3_terminal_pre_output:"),"recorded_at":now().isoformat()}; persist(cap,cp,a.checkpoint_out,a.public_out,a.batch_id); write(a.cell_summary,{"status":"TERMINAL_EXPERIMENT_FAILURE","continue_with_batch":False,"terminal":True,"cell_id":cid,"reason":reason,"provider_call_made":not a.dry_run}); return 0
    cap.accept_parent(cp,cid,str(rec["parent_hash"]),rec); cp["cell_resume_at"].pop(cid,None); persist(cap,cp,a.checkpoint_out,a.public_out,a.batch_id); write(a.cell_summary,{"status":"PARENT_ACCEPTED","continue_with_batch":True,"terminal":False,"cell_id":cid,"parent_hash":rec["parent_hash"],"provider_call_made":not a.dry_run,"completed_cell_count":len(cp["completed"])}); return 0


def order(bm):
    by={(int(c["seed"]),str(c["ticket_id"])):str(c["cell_id"]) for c in cells(bm)}
    return [by[(s,t)] for t in bm["ticket_order"] for s in SEEDS]
def finalize(a):
    ac,bm,cap,runner=load(a.activation),load(a.batch_map),mod("c3capfin",a.capacity_control),mod("c3basefin",a.base_runner); static(ac,bm); cp=load(a.checkpoint_in); valid(cap,cp,bm,a.execution_id); assert not cp["pending"] and len(cp["completed"])==36
    common=[cp["completed"][k]["raw_parent"] for k in order(bm)]; freeze=h([{"call_id":r["call_id"],"parent_hash":r["parent_hash"]} for r in common]); e0in=[{"visible_case":r["visible_case"],"output":r["parent_output"]} for r in common]; e0,e0m=runner.candidates.apply_e0_batch(e0in); e1=[runner.candidates.apply_e1(r["visible_case"],r["parent_output"])[0] for r in common]
    out=[]; sm={x:0 for x in ARMS}
    for i,r in enumerate(common):
        a00,m00=runner.candidates.apply_s0(e0[i]); a10,m10=runner.candidates.apply_s0(e1[i]); x,_=runner.candidates.apply_s0(e0[i]); a01,m01=runner.candidates.apply_s1(x,r["visible_case"]); y,_=runner.candidates.apply_s0(e1[i]); a11,m11=runner.candidates.apply_s1(y,r["visible_case"])
        for arm,z,ef,sf,m in [("A00",a00,"E0","S0",m00),("A10",a10,"E1","S0",m10),("A01",a01,"E0","S1",m01),("A11",a11,"E1","S1",m11)]:
            if arm in {"A01","A11"} and m.get("certificate_failure_reason") is not None:sm[arm]+=1
            out.append({"arm":arm,"evidence_factor":ef,"safety_factor":sf,"call_id":r["call_id"],"group_id":r["group_id"],"scenario_id":r["scenario_id"],"ticket_id":r["ticket_id"],"modality":r["modality"],"source_split":r["source_split"],"partition":"EXPOSED_POOL","seed":r["seed"],"repeat_index":r["repeat_index"],"common_parent_hash":r["parent_hash"],"parsed_output":z,"output_hash":h(z),"arm_transform_meta":m})
    assert len(out)==144
    fixed={"schema_version":"p12-c3-fixed-factorial-outputs-v1","status":"P12_C3_FIXED_FACTORIAL_OUTPUTS_PASS","activation_id":ac["activation_id"],"experiment_id":EXP,"execution_id":a.execution_id,"partition":"EXPOSED_POOL","participating_arms":ARMS,"common_parent_count":36,"fixed_arm_output_count":144,"common_parent_freeze_hash":freeze,"private_checkpoint_hash":cap.checkpoint_hash(cp),"e0_policy_meta":e0m,"s1_certificate_failure_counts":sm,"candidate_private_oracle_accesses":0,"fresh_blind_accesses":0,"legacy_locked_test_accesses":0,"arm_specific_provider_calls":0,"fixed_before_private_scoring":True,"calls":out}; write(a.fixed_outputs,fixed)
    write(a.generation_summary,{"schema_version":"p12-c3-capacity-controlled-generation-summary-v1","status":"PASS","experiment_id":EXP,"execution_id":a.execution_id,"successful_common_parent_generations":36,"fixed_arm_outputs":144,"same_parent_hash_for_all_four_arms":True,"candidate_outputs_fixed_before_private_scoring":True,"common_parent_freeze_hash":freeze,"private_checkpoint_hash":cap.checkpoint_hash(cp),"transport_failure_count":cp["transport_failure_count"],"rate_limit_event_count":cp["rate_limit_event_count"],"candidate_private_oracle_accesses":0,"fresh_blind_accesses":0,"legacy_locked_test_accesses":0,"arm_specific_provider_calls":0,"raw_outputs_in_summary":False}); return 0


def summarize(a):
    bm,cap=load(a.batch_map),mod("c3capsum",a.capacity_control); cp=load(a.checkpoint_in); valid(cap,cp,bm,a.execution_id); b=bids(bm)[a.batch_id]; complete=all(str(c["cell_id"]) in cp["completed"] for c in b["cells"]); f=dt(cp.get("first_live_call_at")); expired=bool(f and not cap.within_horizon(f,now())); terminal=cp.get("terminal_failure") is not None
    write(a.summary_out,{"schema_version":"p12-c3-batch-handoff-summary-v1","experiment_id":EXP,"execution_id":a.execution_id,"batch_id":a.batch_id,"batch_complete":complete,"all_36_complete":len(cp["completed"])==36 and not cp["pending"],"terminal_failure":terminal,"horizon_expired":expired,"completed_cell_count":len(cp["completed"]),"pending_cell_count":len(cp["pending"]),"transport_failure_count":cp["transport_failure_count"],"rate_limit_event_count":cp["rate_limit_event_count"],"provider_reset_timestamp_or_duration":cp.get("provider_reset_timestamp_or_duration"),"checkpoint_hash":cap.checkpoint_hash(cp),"raw_outputs_in_summary":False}); return 3 if terminal or expired else (0 if complete else 2)


def common(p): p.add_argument("--execution-id",required=True);p.add_argument("--activation",type=Path,required=True);p.add_argument("--batch-map",type=Path,required=True);p.add_argument("--capacity-control",type=Path,required=True)
def main():
    q=argparse.ArgumentParser();s=q.add_subparsers(dest="cmd",required=True)
    p=s.add_parser("prepare");common(p);p.add_argument("--batch-id",required=True);p.add_argument("--checkpoint-in",type=Path);p.add_argument("--checkpoint-out",type=Path,required=True);p.add_argument("--public-out",type=Path,required=True);p.add_argument("--allow-initialize",action="store_true");p.set_defaults(f=prepare)
    p=s.add_parser("run-cell");common(p);p.add_argument("--batch-id",required=True);p.add_argument("--cell-ordinal",type=int,required=True);p.add_argument("--base-runner",type=Path,required=True);p.add_argument("--checkpoint-in",type=Path,required=True);p.add_argument("--checkpoint-out",type=Path,required=True);p.add_argument("--public-out",type=Path,required=True);p.add_argument("--cell-summary",type=Path,required=True);p.add_argument("--split-manifest",type=Path,default=Path("research/frozen/benchmark-split-v1.json"));p.add_argument("--agent-input-cases",type=Path,default=Path("agent-input/cases.json"));p.add_argument("--timeout-seconds",type=int,default=90);p.add_argument("--dry-run",action="store_true");p.set_defaults(f=run_cell)
    p=s.add_parser("finalize");common(p);p.add_argument("--base-runner",type=Path,required=True);p.add_argument("--checkpoint-in",type=Path,required=True);p.add_argument("--fixed-outputs",type=Path,required=True);p.add_argument("--generation-summary",type=Path,required=True);p.set_defaults(f=finalize)
    p=s.add_parser("summarize");common(p);p.add_argument("--batch-id",required=True);p.add_argument("--checkpoint-in",type=Path,required=True);p.add_argument("--summary-out",type=Path,required=True);p.set_defaults(f=summarize)
    a=q.parse_args();return int(a.f(a))
if __name__=="__main__":raise SystemExit(main())
