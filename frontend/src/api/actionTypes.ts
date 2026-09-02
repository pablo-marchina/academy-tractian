export type PendingActionState =
  | "PENDING_CONFIRMATION"
  | "CONFIRMED"
  | "EXECUTING"
  | "ACCEPTED"
  | "BLOCKED"
  | "NOT_ACCEPTED"
  | "UNCERTAIN";

export interface PendingActionSafe {
  action_id: string;
  origin_run_id: string;
  tool_name: string;
  action_fingerprint: string;
  impact: string;
  required_permissions: string[];
  confirmation_required: true;
  state: PendingActionState;
  execution_run_id: string | null;
}

export interface ActionExecutionAccepted {
  action_id: string;
  status: "accepted";
  execution_run_id: string;
  stream_path: string;
  run_path: string;
  execution_path: string;
}
