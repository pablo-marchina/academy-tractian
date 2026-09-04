export type SemanticDimension =
  | "groundedness"
  | "operational_usefulness"
  | "customer_safe_clarity"
  | "escalation_quality";

export type SemanticScore = 0 | 1 | 2;

export type HumanLabelReason =
  | "UNSUPPORTED_CLAIM"
  | "CONTRADICTED_CLAIM"
  | "UNCERTAINTY_OVERSTATED"
  | "WRONG_OPERATIONAL_CONCLUSION"
  | "MISSING_NEXT_STEP"
  | "WEAK_PRIORITIZATION"
  | "AMBIGUOUS_COMMUNICATION"
  | "UNNECESSARY_INTERNAL_DETAIL"
  | "UNSAFE_DISCLOSURE"
  | "ESCALATION_UNJUSTIFIED"
  | "ESCALATION_CONTEXT_INCOMPLETE"
  | "HUMAN_ACTION_UNCLEAR"
  | "NO_MATERIAL_DEFECT";

export interface SemanticReviewerTaskSafe {
  task_id: string;
  response_mode: string;
  dimension: SemanticDimension;
  terminal_decision: string;
  terminal_message: string;
  safe_evidence_context: string[];
  criterion_description: string;
  score_0_anchor: string;
  score_1_anchor: string;
  score_2_anchor: string;
}

export interface SemanticReviewAssignment {
  assignment_id: string;
  packet_id: string;
  task: SemanticReviewerTaskSafe;
}

export interface SemanticReviewSubmission {
  score: SemanticScore;
  reason_codes: HumanLabelReason[];
}

export interface SemanticReviewAccepted {
  assignment_id: string;
  packet_id: string;
  task_id: string;
  state: "COMPLETED";
}

export interface SemanticReviewWithdrawn {
  assignment_id: string;
  packet_id: string;
  task_id: string;
  state: "WITHDRAWN";
}