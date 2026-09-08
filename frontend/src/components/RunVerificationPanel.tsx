import { useQuery } from "@tanstack/react-query";

import { fetchRunVerification } from "../api/verificationClient";
import type { VerificationDimension, VerificationStatus } from "../api/verificationTypes";

function statusClass(status: VerificationStatus): string {
  if (status === "VERIFIED") return "check-pass";
  if (status === "FAILED") return "check-fail";
  return "muted";
}

function label(name: string): string {
  return name.replaceAll("_", " ").replace(/(^|\s)\S/g, (character) => character.toUpperCase());
}

function DimensionRow({ dimension }: { dimension: VerificationDimension }) {
  return (
    <li>
      <span className={statusClass(dimension.status)}>{dimension.status}</span>
      <span>
        <strong>{label(dimension.name)}</strong>
        <small className="muted"> — {dimension.summary}</small>
      </span>
    </li>
  );
}

export function RunVerificationPanel({ runId, completed }: { runId: string | null; completed: boolean }) {
  const query = useQuery({
    queryKey: ["run-verification", runId],
    queryFn: () => fetchRunVerification(runId!),
    enabled: Boolean(runId && completed),
  });

  return (
    <article className="panel evaluation-panel" aria-label="Selected analysis verification">
      <div className="section-heading compact">
        <div>
          <h2>Selected analysis verification</h2>
          <p className="section-supporting-copy">Runtime integrity, task success, evidence, trajectory, availability and safety are separate claims. Structural green is never presented as overall quality.</p>
        </div>
      </div>

      {!runId ? (
        <div className="empty-state small"><strong>No analysis selected</strong><p>Select or run an analysis to inspect its verification state.</p></div>
      ) : !completed ? (
        <div className="empty-state small"><strong>Verification waits for terminal state</strong><p>The assurance report is generated from persisted post-runtime evidence.</p></div>
      ) : query.isLoading ? (
        <p className="muted">Loading claim-bounded verification…</p>
      ) : query.error ? (
        <div className="error-banner friendly-error" role="alert"><strong>Verification could not be loaded.</strong><span>{query.error.message}</span></div>
      ) : query.data ? (
        <>
          <div className="evaluation-score"><strong>{query.data.overall_status}</strong><span>overall hard-gate status</span></div>
          <ul className="check-list">{query.data.dimensions.map((dimension) => <DimensionRow key={dimension.name} dimension={dimension} />)}</ul>
          <details className="technical-disclosure">
            <summary>How to read this</summary>
            <p><strong>VERIFIED</strong> means the scoped claim has affirmative evidence. <strong>FAILED</strong> means evidence contradicts it. <strong>NOT_VERIFIED</strong> means evidence is missing or insufficient and is never counted as a pass.</p>
            <p>Semantic correctness and operational value remain separate evidence classes; they cannot be inferred from runtime-integrity checks.</p>
          </details>
        </>
      ) : null}
    </article>
  );
}
