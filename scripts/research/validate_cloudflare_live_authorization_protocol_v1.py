from __future__ import annotations

import json

from academy_tractian.cloudflare_live_authorization_v1 import (
    AUTHORIZATION_PROTOCOL_VERSION,
    validate_frozen_authorization_protocol,
)


def main() -> None:
    protocol = validate_frozen_authorization_protocol()
    print(
        json.dumps(
            {
                "status": "PASS",
                "schema_version": AUTHORIZATION_PROTOCOL_VERSION,
                "attempt_1_authorized": protocol["current_task_boundaries"]["attempt_1_authorized"],
                "provider_model_inference_calls": 0,
                "credential_account_probes": 0,
                "live_network_validation": 0,
                "comparison_attempts_consumed": 0,
                "minimum_free_neurons_remaining": protocol["authorization_evidence"]["minimum_free_neurons_remaining"],
                "evidence_max_age_seconds": protocol["authorization_evidence"]["max_age_seconds"],
                "receipt_max_lifetime_seconds": protocol["authorization_receipt"]["max_lifetime_seconds"],
            },
            sort_keys=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
