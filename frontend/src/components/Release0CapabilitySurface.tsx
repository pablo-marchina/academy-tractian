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
  if (tool.availability === "LIVE_READ") return "Can read live data";
  if (tool.availability === "PROPOSAL_ONLY") return "Can propose only";
  return "Not available";
}

function availabilityTone(tool: Release0ToolCapability): string {
  if (tool.availability === "LIVE_READ") return "live";
  if (tool.availability === "PROPOSAL_ONLY") return "proposal";
  return "unavailable";
}

function humanize(value: string): string {
  const words = value.replaceAll("_", " ").toLowerCase();
  return words.charAt(0).toUpperCase() + words.slice(1);
}

export function Release0CapabilitySurface({ events, onUsePrompt }: Props) {
  const query = useQuery({ queryKey: ["release0-capabilities"], queryFn: fetchRelease0Capabilities, staleTime: 60_000 });

  const usedTools = useMemo(
    () => new Set(events.filter((event) => event.tool_name && ["tool_call", "tool_result", "observation"].includes(event.event_type)).map((event) => event.tool_name!)),
    [events],
  );

  if (query.isLoading) {
    return (
      <section className="panel release0-surface" aria-busy="true">
        <p className="eyebrow">CURRENT CAPABILITIES</p>
        <h2>Loading the production capability contract…</h2>
        <p className="muted">Capabilities are read from the server instead of being guessed by the interface.</p>
      </section>
    );
  }
  if (!query.data) {
    return <section className="panel release0-surface"><p className="eyebrow">CURRENT CAPABILITIES</p><h2>Capability contract unavailable</h2><p className="muted">The UI will not substitute a hard-coded tool catalog when the production manifest is missing.</p></section>;
  }

  const manifest = query.data;
  const observedCount = manifest.tools.filter((tool) => usedTools.has(tool.name)).length;

  return (
    <section className="panel release0-surface" aria-label="Current production capabilities and readiness">
      <div className="section-heading">
        <div>
          <p className="eyebrow">CURRENT PRODUCTION CAPABILITIES</p>
          <h2>What this release can do</h2>
          <p className="section-supporting-copy">This view comes from the server-owned contract. It distinguishes what is available in production from what happened in the selected analysis.</p>
        </div>
        <div className="release0-heading-meta">
          <span className={`release0-badge ${manifest.release.read_only_user_path_enabled ? "live" : "unavailable"}`}>{manifest.release.read_only_user_path_enabled ? "READ-ONLY ANALYSIS READY" : "READ-ONLY ANALYSIS BLOCKED"}</span>
          <span className="count-pill">{observedCount}/{manifest.tool_summary.total} operations used in this analysis</span>
        </div>
      </div>

      <div className="release0-readiness-grid">
        <article><span>AI provider</span><strong>{manifest.provider.calls_enabled ? "Live calls enabled" : "Calls disabled"}</strong><small>{manifest.provider.model_id ?? humanize(manifest.provider.selection_state)}</small></article>
        <article><span>TRACTIAN data</span><strong>{manifest.tractian.read_path_enabled ? "Live read path available" : "Read path blocked"}</strong><small>{humanize(manifest.tractian.transport_state)}</small></article>
        <article><span>External actions</span><strong>Proposal only</strong><small>No external side effect from the ordinary user path</small></article>
        <article><span>Cost boundary</span><strong>{humanize(manifest.release.cost_policy)}</strong><small>Paid fallback: {manifest.release.paid_fallback_enabled ? "enabled" : "disabled"}</small></article>
        <article><span>Release identity</span><strong>{manifest.release.git_sha.slice(0, 12)}</strong><small>Exact source revision reported by the server</small></article>
      </div>

      <div className="release0-section">
        <div className="section-heading compact">
          <div><p className="eyebrow">GUIDED STARTS</p><h2>Example investigation approaches</h2><p className="section-supporting-copy">These buttons only fill the question box. You can edit the wording before starting, and the runtime remains authoritative.</p></div>
        </div>
        <div className="intent-grid">
          {manifest.guided_intents.map((intent) => (
            <button key={intent.intent_id} type="button" className="intent-card" onClick={() => onUsePrompt(intent.prompt_template)}>
              <strong>{intent.label}</strong>
              <small>{humanize(intent.release0_behavior)}</small>
              <span className="visually-hidden">{intent.intent_id} · {intent.runtime_mapping}</span>
              <p>Fill the question box with this starting point</p>
            </button>
          ))}
        </div>
      </div>

      <details className="technical-disclosure release0-section release0-tool-disclosure">
        <summary>
          <span><strong>Inspect all TRACTIAN operations</strong><small>{manifest.tool_summary.reads} reads · {manifest.tool_summary.actions} actions · {manifest.tool_summary.total} total</small></span>
        </summary>
        <div className="release0-disclosure-body">
          <p className="release0-disclosure">“Available” means the operation exists at the production tool boundary. “Used in this analysis” means the selected analysis actually invoked it. Action operations remain inspectable for proposals and policy evaluation even when external execution is disabled.</p>
          <div className="capability-grid">
            {manifest.tools.map((tool) => {
              const used = usedTools.has(tool.name);
              const required = tool.parameters.filter((parameter) => parameter.required).map((parameter) => parameter.name);
              return (
                <article key={tool.name} className={`capability-card ${used ? "observed" : ""}`}>
                  <div className="capability-card-top"><span className={`release0-badge ${availabilityTone(tool)}`}>{availabilityLabel(tool)}</span>{used && <span className="observed-mark">USED IN THIS ANALYSIS</span>}</div>
                  <strong>{humanize(tool.name)}</strong>
                  <small>{tool.kind === "action" ? `${humanize(tool.impact)} impact action` : "Read-only operation"}</small>
                  <details className="technical-disclosure compact-disclosure">
                    <summary>API details</summary>
                    <code>{tool.method} {tool.path_template}</code>
                    <p>{tool.operation_id}</p>
                    <p>{required.length ? `Required parameters: ${required.join(", ")}` : "No required model-supplied parameters"}</p>
                  </details>
                </article>
              );
            })}
          </div>
        </div>
      </details>

      <div className="release0-output-grid">
        <div className="release0-section">
          <p className="eyebrow">UNCERTAINTY HANDLING</p><h2>The assistant can stop instead of inventing an answer</h2>
          <div className="semantic-pills">{manifest.read_semantics.map((mode) => <span key={mode}>{humanize(mode)}</span>)}</div>
        </div>
        <div className="release0-section">
          <p className="eyebrow">OUTPUTS</p><h2>What the product keeps available for review</h2>
          <div className="output-contract-list">{manifest.expected_outputs.map((output) => <div key={output.output_id}><strong>{output.label}</strong><small>{output.description}</small></div>)}</div>
        </div>
      </div>

      <p className="release0-safety-note">This screen intentionally excludes raw credentials, raw TRACTIAN payloads, tenant authority, private action authorization material and private chain-of-thought.</p>
    </section>
  );
}
