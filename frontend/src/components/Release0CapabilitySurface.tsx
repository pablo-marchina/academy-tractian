import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";

import { fetchRelease0Capabilities } from "../api/release0Client";
import type { Release0ToolCapability } from "../api/release0Types";
import type { SafeEvent } from "../api/types";

interface Props {
  events: SafeEvent[];
  onUsePrompt: (prompt: string) => void;
}

function availabilityLabel(tool: Release0ToolCapability): string {
  if (tool.availability === "LIVE_READ") return "LIVE READ";
  if (tool.availability === "PROPOSAL_ONLY") return "PROPOSAL ONLY";
  return "UNAVAILABLE";
}

function availabilityTone(tool: Release0ToolCapability): string {
  if (tool.availability === "LIVE_READ") return "live";
  if (tool.availability === "PROPOSAL_ONLY") return "proposal";
  return "unavailable";
}

export function Release0CapabilitySurface({ events, onUsePrompt }: Props) {
  const query = useQuery({
    queryKey: ["release0-capabilities"],
    queryFn: fetchRelease0Capabilities,
    staleTime: 60_000,
  });

  const usedTools = useMemo(
    () => new Set(events.filter((event) => event.tool_name && ["tool_call", "tool_result", "observation"].includes(event.event_type)).map((event) => event.tool_name!)),
    [events],
  );

  if (query.isLoading) {
    return <section className="panel release0-surface"><p className="eyebrow">RELEASE 0</p><h2>Loading server-owned capability contract…</h2></section>;
  }
  if (!query.data) {
    return <section className="panel release0-surface"><p className="eyebrow">RELEASE 0</p><h2>Capability contract unavailable</h2><p className="muted">The UI will not substitute a hard-coded tool catalog when the production manifest is missing.</p></section>;
  }

  const manifest = query.data;
  const observedCount = manifest.tools.filter((tool) => usedTools.has(tool.name)).length;

  return (
    <section className="panel release0-surface" aria-label="Release 0 capability and readiness">
      <div className="section-heading">
        <div>
          <p className="eyebrow">RELEASE 0 · SERVER-OWNED CONTRACT</p>
          <h2>Industrial capability & readiness</h2>
        </div>
        <div className="release0-heading-meta">
          <span className={`release0-badge ${manifest.release.read_only_user_path_enabled ? "live" : "unavailable"}`}>{manifest.release.read_only_user_path_enabled ? "READ-ONLY PATH READY" : "READ-ONLY PATH BLOCKED"}</span>
          <span className="count-pill">{observedCount}/{manifest.tool_summary.total} observed in selected run</span>
        </div>
      </div>

      <div className="release0-readiness-grid">
        <article><span>Provider</span><strong>{manifest.provider.calls_enabled ? `${manifest.provider.provider_id ?? "configured"} · live calls` : "disabled"}</strong><small>{manifest.provider.model_id ?? manifest.provider.selection_state}</small></article>
        <article><span>TRACTIAN</span><strong>{manifest.tractian.read_path_enabled ? "live read path" : "read path blocked"}</strong><small>{manifest.tractian.transport_state}</small></article>
        <article><span>Actions</span><strong>proposal only</strong><small>external side effects disabled</small></article>
        <article><span>Cost boundary</span><strong>{manifest.release.cost_policy}</strong><small>paid fallback: {manifest.release.paid_fallback_enabled ? "enabled" : "disabled"}</small></article>
        <article><span>Release</span><strong>{manifest.release.git_sha.slice(0, 12)}</strong><small>immutable artifact identity</small></article>
      </div>

      <div className="release0-section">
        <div className="section-heading compact"><div><p className="eyebrow">GUIDED INTENTS</p><h2>Start with the right operating posture</h2></div><span className="count-pill">prompt presets · runtime remains authoritative</span></div>
        <div className="intent-grid">
          {manifest.guided_intents.map((intent) => (
            <button key={intent.intent_id} type="button" className="intent-card" onClick={() => onUsePrompt(intent.prompt_template)}>
              <span>{intent.intent_id}</span><strong>{intent.label}</strong><small>{intent.runtime_mapping}</small><p>{intent.release0_behavior.replaceAll("_", " ").toLowerCase()}</p>
            </button>
          ))}
        </div>
      </div>

      <div className="release0-section">
        <div className="section-heading compact"><div><p className="eyebrow">CANONICAL TOOL REGISTRY</p><h2>All 18 TRACTIAN operations</h2></div><span className="count-pill">{manifest.tool_summary.reads} reads · {manifest.tool_summary.actions} actions</span></div>
        <p className="release0-disclosure">Supported means present at the production HarnessRunner boundary. “Observed” means the selected run actually used the operation. Action tools stay inspectable for proposals and policy evaluation, while Release 0 forbids external execution.</p>
        <div className="capability-grid">
          {manifest.tools.map((tool) => {
            const used = usedTools.has(tool.name);
            const required = tool.parameters.filter((parameter) => parameter.required).map((parameter) => parameter.name);
            return (
              <article key={tool.name} className={`capability-card ${used ? "observed" : ""}`}>
                <div className="capability-card-top"><span className={`release0-badge ${availabilityTone(tool)}`}>{availabilityLabel(tool)}</span>{used && <span className="observed-mark">OBSERVED</span>}</div>
                <strong>{tool.name}</strong>
                <code>{tool.method} {tool.path_template}</code>
                <small>{tool.operation_id} · {tool.kind}{tool.kind === "action" ? ` · ${tool.impact} impact` : ""}</small>
                <p>{required.length ? `required: ${required.join(", ")}` : "no required model-supplied parameters"}</p>
              </article>
            );
          })}
        </div>
      </div>

      <div className="release0-output-grid">
        <div className="release0-section">
          <p className="eyebrow">READ SEMANTICS</p><h2>Evidence can be uncertain without becoming a false answer</h2>
          <div className="semantic-pills">{manifest.read_semantics.map((mode) => <span key={mode}>{mode}</span>)}</div>
        </div>
        <div className="release0-section">
          <p className="eyebrow">EXPECTED OUTPUT CONTRACT</p><h2>Every relevant artifact remains visible</h2>
          <div className="output-contract-list">{manifest.expected_outputs.map((output) => <div key={output.output_id}><strong>{output.label}</strong><small>{output.description}</small></div>)}</div>
        </div>
      </div>

      <p className="release0-safety-note">No raw credentials, raw TRACTIAN payloads, tenant authority, private action authorization material, or chain-of-thought are exposed by this surface.</p>
    </section>
  );
}
