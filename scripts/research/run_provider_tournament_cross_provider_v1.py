from __future__ import annotations

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from academy_tractian.provider_tournament_cross_provider_v1 import (  # noqa: E402
    CANDIDATES,
    REPETITIONS,
    analyze_tournament,
    run_packet,
)


def _required_secret(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"required hosted secret is absent: {name}")
    return value


def main() -> int:
    output_dir = Path(os.environ.get("DP005_OUTPUT_DIR", "artifacts/provider-tournament-cross-provider-v1"))
    output_dir.mkdir(parents=True, exist_ok=True)
    api_keys = {
        candidate.candidate_id: _required_secret(candidate.secret_name)
        for candidate in CANDIDATES
    }
    packet_paths: list[Path] = []
    for repetition_index in range(REPETITIONS):
        path = output_dir / f"packet-{repetition_index}.json"
        packet = run_packet(
            repetition_index=repetition_index,
            api_keys=api_keys,
            output_path=path,
            repo_root=ROOT,
        )
        packet_paths.append(path)
        print(
            json.dumps(
                {
                    "event": "dp005_packet_complete",
                    "repetition_index": repetition_index,
                    "attempt_count": packet["attempt_count"],
                    "complete": packet["complete"],
                },
                sort_keys=True,
            ),
            flush=True,
        )
    analysis = analyze_tournament(packet_paths)
    final_path = output_dir / "final-analysis.json"
    final_path.write_text(
        json.dumps(analysis, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "event": "dp005_final_analysis",
                "selection": analysis["selection"],
                "selection_reason": analysis["selection_reason"],
                "eligible_candidates": analysis["eligible_candidates"],
                "candidate_summaries": analysis["candidate_summaries"],
                "raw_provider_material_recorded": analysis["raw_provider_material_recorded"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
