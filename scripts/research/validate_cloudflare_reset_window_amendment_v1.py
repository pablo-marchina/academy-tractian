from __future__ import annotations

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from academy_tractian.cloudflare_live_authorization_reset_v2 import (  # noqa: E402
    AMENDMENT_PROTOCOL_VERSION,
    validate_frozen_reset_window_amendment,
)


def main() -> None:
    protocol = validate_frozen_reset_window_amendment()
    fallback = protocol["fallback_mode"]
    boundary = protocol["future_execution_boundary"]
    print(
        json.dumps(
            {
                "status": "PASS",
                "schema_version": AMENDMENT_PROTOCOL_VERSION,
                "mode": fallback["name"],
                "reset_capture_max_offset_seconds": fallback["reset_capture_max_offset_seconds"],
                "derived_free_neurons_at_evidence": fallback["derived_free_neurons_at_evidence"],
                "provider_model_inference_calls": boundary["provider_model_inference_calls_in_this_task"],
                "credential_account_probes": boundary["credential_account_probes_in_this_task"],
                "live_network_validation": boundary["live_network_validation_in_this_task"],
                "attempt_1_authorized": boundary["attempt_1_authorized"],
            },
            sort_keys=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
