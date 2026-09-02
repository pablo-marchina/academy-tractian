from __future__ import annotations

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from academy_tractian.cloudflare_live_authorization_same_day_v3 import (  # noqa: E402
    validate_frozen_same_day_zero_use_amendment,
)


def main() -> None:
    protocol = validate_frozen_same_day_zero_use_amendment()
    print(
        json.dumps(
            {
                "status": "SAME_DAY_ZERO_USE_AMENDMENT_PROVIDER_FREE_VALIDATED",
                "schema_version": protocol["schema_version"],
                "provider_model_inference_calls": 0,
                "credential_account_probes": 0,
                "live_network_validation": 0,
                "comparison_attempts_consumed": 0,
                "attempt_1_authorized": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
