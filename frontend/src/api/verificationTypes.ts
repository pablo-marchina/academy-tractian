export type VerificationStatus = "VERIFIED" | "FAILED" | "NOT_VERIFIED" | "NOT_APPLICABLE";

export interface VerificationDimension {
  name: string;
  status: VerificationStatus;
  blocking: boolean;
  scope: string;
  summary: string;
  evidence: string[];
  metrics: Record<string, string | number | boolean | null>;
  limitations: string[];
}

export interface RunVerificationReport {
  schema_version: "run-verification-v1";
  run_id: string;
  overall_status: VerificationStatus;
  dimensions: VerificationDimension[];
}
