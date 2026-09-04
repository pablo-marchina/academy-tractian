from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping

from pydantic import ValidationError

from academy_tractian.hosted_integration_evidence_recorder import HostedIntegrationEvidenceRecorder
from academy_tractian.hosted_tractian_transport import HostedTractianTransport
from academy_tractian.postgres_integration_evidence_store import PostgresIntegrationEvidenceStore
from academy_tractian.postgres_operational import PostgresOperationalDatabase
from academy_tractian.tractian_integration_campaign import build_tractian_integration_campaign_report
from academy_tractian.tractian_transport_campaign import (
    TractianTransportCampaignManifest,
    run_tractian_transport_campaign,
)


def _required_environment(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"missing_required_environment:{name}")
    return value


def _read_json_object(path: Path) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid_transport_campaign_manifest") from exc
    if not isinstance(payload, dict):
        raise ValueError("transport_campaign_manifest_must_be_object")
    return payload


def _failure(reason: str) -> int:
    print(
        json.dumps(
            {
                "schema_version": "tractian-transport-campaign-cli-v1",
                "status": "FAIL",
                "status_scope": "runner_execution_only_not_18_of_18",
                "transport_gate_passed": False,
                "reason": reason,
            },
            sort_keys=True,
        )
    )
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run bounded hosted TRACTIAN transport probes. A consequential valid probe requires "
            "per-fixture approval, an approval reference and --allow-actions. A consequential "
            "HTTP-error probe is a second mutation and additionally requires "
            "action_error_probe_approved=true in that fixture. Raw arguments and response bodies "
            "are never printed."
        )
    )
    parser.add_argument("manifest", help="tractian-transport-campaign-manifest-v1 JSON file")
    parser.add_argument(
        "--allow-actions",
        action="store_true",
        help=(
            "invocation-level gate for action fixtures already approved in the manifest; this does "
            "not by itself authorize an action error probe"
        ),
    )
    parser.add_argument(
        "--persist",
        action="store_true",
        help="persist bounded transport evidence to the migrated managed PostgreSQL store",
    )
    args = parser.parse_args()

    database: PostgresOperationalDatabase | None = None
    try:
        try:
            manifest = TractianTransportCampaignManifest.model_validate(
                _read_json_object(Path(args.manifest))
            )
        except ValidationError:
            return _failure("transport_campaign_manifest_validation_failed")

        transport = HostedTractianTransport(
            base_url=_required_environment("ACADEMY_TRACTIAN_BASE_URL"),
            bearer_token=os.environ.get("ACADEMY_TRACTIAN_BEARER_TOKEN", "").strip() or None,
        )
        recorder = HostedIntegrationEvidenceRecorder()

        if args.persist:
            database = PostgresOperationalDatabase(
                internal_dsn=_required_environment("ACADEMY_POSTGRES_INTERNAL_DSN"),
                scoped_dsn=_required_environment("ACADEMY_POSTGRES_SCOPED_DSN"),
                schema=os.environ.get("ACADEMY_POSTGRES_SCHEMA", "academy_operational").strip(),
                initialize=False,
            )
            store = PostgresIntegrationEvidenceStore(
                database,
                schema=os.environ.get(
                    "ACADEMY_OBSERVABILITY_SCHEMA", "academy_observability"
                ).strip(),
                initialize=False,
            )
            if not store.ready():
                return _failure("postgres_integration_evidence_store_not_ready")
            recorder.attach_persistent_store(store)
            if not recorder.ledger().valid:
                return _failure("postgres_integration_evidence_store_invalid")

        run, ledger = run_tractian_transport_campaign(
            manifest=manifest,
            transport=transport,
            allow_actions=args.allow_actions,
            recorder=recorder,
        )
        if not ledger.valid:
            return _failure("transport_campaign_evidence_invalid")

        campaign = build_tractian_integration_campaign_report(hosted_evidence=ledger)
        unexpected = [
            result.operation
            for result in run.results
            if result.valid_probe not in {"success", "blocked_by_safety"}
            or result.error_probe not in {"http_error_observed", "not_configured"}
        ]
        runner_passed = not unexpected
        transport_gate_passed = campaign.transport_complete_operations == campaign.normalized_operations
        approved_action_error_probes = sum(
            fixture.action_error_probe_approved for fixture in manifest.fixtures
        )
        executed_action_error_probes = sum(
            result.action_error_probe_enabled for result in run.results
        )
        payload = {
            "schema_version": "tractian-transport-campaign-cli-v1",
            "status": "PASS" if runner_passed else "FAIL",
            "status_scope": "runner_execution_only_not_18_of_18",
            "persisted": bool(args.persist),
            "actions_invocation_gate_enabled": bool(args.allow_actions),
            "approved_action_error_probes": approved_action_error_probes,
            "executed_action_error_probes": executed_action_error_probes,
            "configured_operations": run.configured_operations,
            "executed_operations": run.executed_operations,
            "safety_blocked_actions": run.safety_blocked_actions,
            "successful_valid_probes": run.successful_valid_probes,
            "observed_http_error_probes": run.observed_http_error_probes,
            "transport_complete_operations": campaign.transport_complete_operations,
            "transport_incomplete_operations": campaign.transport_incomplete_operations,
            "transport_completion_status": campaign.transport_completion_status,
            "transport_gate_passed": transport_gate_passed,
            "unexpected_probe_operation_count": len(unexpected),
            "unexpected_probe_operations": sorted(unexpected),
            "results": [
                {
                    "operation": result.operation,
                    "kind": result.kind,
                    "valid_probe": result.valid_probe,
                    "error_probe": result.error_probe,
                    "action_live_execution_enabled": result.action_live_execution_enabled,
                    "action_error_probe_enabled": result.action_error_probe_enabled,
                }
                for result in run.results
            ],
        }
        print(json.dumps(payload, sort_keys=True))
        return 0 if runner_passed else 2
    except ValueError as exc:
        reason = str(exc)
        if not reason.startswith("missing_required_environment:"):
            reason = "transport_campaign_rejected"
        return _failure(reason)
    except Exception:
        return _failure("transport_campaign_failed")
    finally:
        if database is not None:
            database.close()


if __name__ == "__main__":
    sys.exit(main())
