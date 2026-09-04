from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
for candidate in (SRC_ROOT, REPO_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from academy_tractian.observability_store import ObservabilityStore  # noqa: E402
from academy_tractian.semantic_annotation_sources import (  # noqa: E402
    SemanticSourceSelection,
    build_validation_semantic_annotation_sources,
    freeze_semantic_source_selection,
)


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid JSON {path}: {exc}") from exc


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize held-out semantic annotation sources from the persisted browser-safe "
            "DuckDB read model. Raw RunTrace/provider material is never accepted."
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)

    freeze = sub.add_parser("freeze-selection", help="Freeze exact safe run IDs before materialization")
    freeze.add_argument("--run-id", action="append", required=True, dest="run_ids")
    freeze.add_argument("--output", type=Path, required=True)

    build = sub.add_parser("build", help="Build VALIDATION SemanticAnnotationSource records")
    build.add_argument("--observability-db", type=Path, required=True)
    build.add_argument("--selection", type=Path, required=True)
    build.add_argument("--split-manifest", type=Path, required=True)
    build.add_argument("--sources-output", type=Path, required=True)
    build.add_argument("--source-manifest-output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "freeze-selection":
        selection = freeze_semantic_source_selection(args.run_ids)
        _write(args.output, selection.model_dump(mode="json"))
        print(
            json.dumps(
                {
                    "status": "FROZEN",
                    "run_count": len(selection.run_ids),
                    "selection_sha256": selection.selection_sha256,
                },
                sort_keys=True,
            )
        )
        return 0

    selection_payload = _load_json(args.selection)
    try:
        selection = SemanticSourceSelection.model_validate(selection_payload)
    except ValueError as exc:
        raise SystemExit(f"invalid semantic source selection: {exc}") from exc
    split_payload = _load_json(args.split_manifest)
    if not isinstance(split_payload, dict):
        raise SystemExit("split manifest must contain a JSON object")

    store = ObservabilityStore(args.observability_db)
    sources, manifest = build_validation_semantic_annotation_sources(
        store=store,
        selection=selection,
        frozen_split_payload=split_payload,
    )
    _write(args.sources_output, [source.model_dump(mode="json") for source in sources])
    _write(args.source_manifest_output, manifest.model_dump(mode="json"))
    print(
        json.dumps(
            {
                "status": "BUILT",
                "source_split": manifest.source_split,
                "source_count": manifest.source_count,
                "selection_sha256": manifest.selection_sha256,
                "frozen_split_sha256": manifest.frozen_split_sha256,
                "source_manifest_sha256": manifest.manifest_sha256,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())