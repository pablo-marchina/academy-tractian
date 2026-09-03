export type OperationalPilotCondition = "MANUAL" | "ASSISTED";
export type HumanPilotTerminationStatus = "INTERRUPTED" | "WITHDRAWN";

export interface OperationalPilotAssistance {
  terminal_decision: string;
  terminal_message: string;
  safe_evidence_context: string[];
}

export interface OperationalPilotTask {
  task_id: string;
  condition: OperationalPilotCondition;
  ticket_request: string;
  assistance: OperationalPilotAssistance | null;
}

export interface OperationalPilotAssignment {
  assignment_id: string;
  packet_id: string;
  task: OperationalPilotTask;
}

export interface OperationalPilotCompletionAccepted {
  assignment_id: string;
  packet_id: string;
  task_id: string;
  status: "VALID" | "INTERRUPTED" | "TECHNICAL_FAILURE" | "WITHDRAWN";
  elapsed_seconds: number | null;
}

export interface OperationalPilotValidSubmission {
  terminal_decision: string;
  conclusion_summary: string;
}

export interface OperationalPilotTerminationSubmission {
  status: HumanPilotTerminationStatus;
}
