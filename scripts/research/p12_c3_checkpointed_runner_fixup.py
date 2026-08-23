#!/usr/bin/env python3
from __future__ import annotations

"""Canonical P12-C3 checkpoint-runner derivation entrypoint.

The original pre-amendment implementation is preserved byte-for-byte at
`p12_c3_checkpointed_runner_fixup_v1_frozen.py`. After B1 run 32671370930
failed before any provider request, the provider-free-qualified pre-provider
amendment became the canonical derivation path. It only bridges the retained
E14l historical transport assertion and restores the frozen P12-C3 controller
transport overrides before any provider request.
"""

from p12_c3_checkpointed_runner_preprovider_amendment import main


if __name__ == "__main__":
    raise SystemExit(main())
