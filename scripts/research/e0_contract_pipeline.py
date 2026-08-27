from __future__ import annotations

"""E0: normalize and conformance-audit the supplied TRACTIAN OpenAPI contract.

The partner artifact is never modified. Outputs are derived artifacts and should normally be
written under a private/generated directory until publication policy is clarified.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "trace"}


class MergeDuplicateLoader(yaml.SafeLoader):
    """Preserve duplicate-key evidence and merge only disjoint duplicate mappings."""

    def __init__(self, stream: str):
        super().__init__(stream)
        self.duplicates: list[dict[str, Any]] = []
        self._path: list[str] = []

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False):  # type: ignore[override]
        mapping: dict[Any, Any] = {}
        first_lines: dict[Any, int] = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            self._path.append(str(key))
            value = self.construct_object(value_node, deep=True)
            self._path.pop()
            if key not in mapping:
                mapping[key] = value
                first_lines[key] = key_node.start_mark.line + 1
                continue

            finding = {
                "key": str(key),
                "path": "/" + "/".join(self._path + [str(key)]),
                "first_line": first_lines[key],
                "duplicate_line": key_node.start_mark.line + 1,
            }
            old = mapping[key]
            if isinstance(old, dict) and isinstance(value, dict):
                overlap = set(old) & set(value)
                if overlap:
                    finding.update(resolution="ERROR_OVERLAPPING_MAPPING_KEYS", overlap=sorted(overlap))
                    self.duplicates.append(finding)
                    raise ValueError(f"Non-mergeable duplicate key: {finding}")
                old.update(value)
                finding["resolution"] = "MERGED_DISJOINT_MAPPING"
            elif old == value:
                finding["resolution"] = "DEDUP_IDENTICAL"
            else:
                finding["resolution"] = "ERROR_NONMERGEABLE"
                self.duplicates.append(finding)
                raise ValueError(f"Non-mergeable duplicate key: {finding}")
            self.duplicates.append(finding)
        return mapping


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_path(path: str) -> str:
    return re.sub(r"\{[^{}]+\}", "{}", path)


def operations(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    global_security = spec.get("security")
    for path, path_item in (spec.get("paths") or {}).items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            key = f"{method.upper()} {canonical_path(path)}"
            params = []
            for param in operation.get("parameters", []) or []:
                if "$ref" in param:
                    ref_name = param["$ref"].split("/")[-1]
                    param = spec.get("components", {}).get("parameters", {}).get(ref_name, {})
                params.append({
                    "name": param.get("name"),
                    "in": param.get("in"),
                    "required": bool(param.get("required", False)),
                    "schema": param.get("schema", {}),
                })
            result[key] = {
                "source_path": path,
                "operationId": operation.get("operationId"),
                "tags": operation.get("tags"),
                "parameters": params,
                "security": operation["security"] if "security" in operation else global_security,
                "requestBody": operation.get("requestBody"),
                "responses": sorted((operation.get("responses") or {}).keys()),
            }
    return result


def request_schema(operation: dict[str, Any]) -> Any:
    body = operation.get("requestBody")
    if not body:
        return None
    return (((body.get("content") or {}).get("application/json") or {}).get("schema"))


def build_runtime_openapi(package_root: Path) -> dict[str, Any]:
    sys.path.insert(0, str(package_root / "api"))
    from app.main import app  # type: ignore
    return app.openapi()


def semantic_probes(package_root: Path) -> dict[str, Any]:
    import pandas as pd
    from fastapi.testclient import TestClient

    sys.path.insert(0, str(package_root / "api"))
    import seed_data  # type: ignore
    from app import store  # type: ignore
    from app.main import app  # type: ignore

    tables = {
        "companies": pd.DataFrame(seed_data.COMPANIES),
        "users": pd.DataFrame(seed_data.USERS),
        "assets": pd.DataFrame(seed_data.ASSETS),
        "points": pd.DataFrame(seed_data.POINTS),
        "baselines": pd.DataFrame(seed_data.BASELINES),
        "analyses": pd.DataFrame(seed_data.ANALYSES + seed_data._gen_healthy_analyses()),
        "models": pd.DataFrame(seed_data.MODELS),
        "knowledge": pd.DataFrame(seed_data.KNOWLEDGE),
        "rms": pd.DataFrame(seed_data.RMS_ROWS),
        "spectra": pd.DataFrame(seed_data.SPECTRA + seed_data._gen_extra_spectra()),
        "data_quality": pd.DataFrame(seed_data.DATA_QUALITY),
        "cases": pd.DataFrame(seed_data.CASES),
    }
    store._tables = lambda: tables
    store.seed_config = lambda: seed_data.SEED_JSON
    client = TestClient(app)

    read_urls = [
        "/companies/comp_forja_br", "/companies/comp_forja_br/assets", "/assets/asset_M101",
        "/assets/asset_M101/analyses", "/analyses/an_9903", "/assets/asset_M101/baseline",
        "/assets/asset_M101/rms", "/assets/asset_M101/spectrum", "/assets/asset_M101/data-quality",
        "/models/mdl_vib_v3", "/knowledge/search?q=BPFO", "/knowledge/kb_glos_001",
    ]
    auth_reads = [{"url": u.split("?")[0], "status_without_user": client.get(u).status_code} for u in read_urls]
    users_me_without_header = client.get("/users/me").status_code

    actions = [
        ("PATCH", "/assets/asset_V301", "usr_helena", {"justification": "Ventilador deixou de ser crítico para produção após reconfiguração operacional.", "changes": {"criticality": "medium"}}),
        ("POST", "/analyses/an_9906/reprocess", "usr_lucas", {"justification": "Rolamento foi trocado e o baseline anterior foi invalidado após manutenção."}),
        ("POST", "/analyses/an_9902/request-specialist", "usr_sofia", {"justification": "RMS segue elevado e a análise automática permanece pendente, exigindo revisão especializada."}),
        ("POST", "/models/mdl_vib_v3/request-retraining", "usr_carla", {"justification": "Há falso positivo documentado e conflito recorrente para o spindle, justificando retreinamento."}),
        ("POST", "/cases/case_tkt_exe_16/escalate", "usr_pedro", {"justification": "Dados ausentes e baseline insuficiente após quebra exigem investigação humana em campo."}),
    ]
    action_results = []
    for method, url, user, body in actions:
        without = client.request(method, url, json=body)
        with_user = client.request(method, url, json=body, headers={"x-user-id": user})
        action_results.append({
            "operation": f"{method} {url}", "without_user_status": without.status_code,
            "authorized_status": with_user.status_code,
            "authorized_accepted": with_user.json().get("accepted") if with_user.status_code == 200 else None,
        })

    def patch(body: dict[str, Any], user: str = "usr_helena"):
        return client.patch("/assets/asset_V301", headers={"x-user-id": user}, json=body)

    invalid = patch({"justification": "Justificativa suficientemente longa para testar criticidade inválida.", "changes": {"criticality": "banana"}})
    missing = patch({"justification": "Justificativa suficientemente longa mesmo sem informar alterações estruturadas."})
    extra = patch({"justification": "Justificativa suficientemente longa para testar campos arbitrários adicionais.", "unexpected": "x"})
    cross = patch({"justification": "Teste controlado de autorização entre empresas com justificativa suficientemente longa.", "changes": {"criticality": "medium"}}, user="usr_ana")

    before = client.get("/assets/asset_V301", params={"seed": "complete"}).json()["data"].get("criticality")
    accepted = patch({"justification": "Ventilador deixou de ser crítico para produção após reconfiguração operacional.", "changes": {"criticality": "medium"}})
    after = client.get("/assets/asset_V301", params={"seed": "complete"}).json()["data"].get("criticality")

    first = client.get("/assets/asset_M101/rms").json()
    second = client.get("/assets/asset_M101/rms").json()
    override = client.get("/assets/asset_G501/rms", params={"seed": "complete"}).json()

    return {
        "read_auth": auth_reads,
        "users_me_without_header_status": users_me_without_header,
        "actions": action_results,
        "weak_validation": {
            "invalid_criticality": [invalid.status_code, invalid.json().get("accepted") if invalid.status_code == 200 else None],
            "missing_changes": [missing.status_code, missing.json().get("accepted") if missing.status_code == 200 else None],
            "extra_field": [extra.status_code, extra.json().get("accepted") if extra.status_code == 200 else None],
        },
        "cross_company": {"status": cross.status_code, "accepted": cross.json().get("accepted") if cross.status_code == 200 else None},
        "action_persistence": {"before": before, "accepted": accepted.json().get("accepted"), "after": after, "persisted": before != after},
        "seed": {
            "same_unseeded_response_equal": first == second,
            "same_unseeded_mode": [first.get("mode"), second.get("mode")],
            "fixed_override_wins_seed_complete": override.get("mode") == "unavailable",
            "override_mode": override.get("mode"),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", required=True)
    parser.add_argument("--normalized-out", required=True)
    parser.add_argument("--manifest-out", required=True)
    parser.add_argument("--runtime-openapi-out", required=True)
    parser.add_argument("--report-out", required=True)
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    raw_path = package_root / "docs" / "api-contract.openapi.yaml"
    raw_bytes = raw_path.read_bytes()

    loader = MergeDuplicateLoader(raw_bytes.decode("utf-8"))
    try:
        normalized = loader.get_single_data()
    finally:
        loader.dispose()

    normalized_text = yaml.safe_dump(normalized, allow_unicode=True, sort_keys=False, width=120)
    normalized_path = Path(args.normalized_out)
    normalized_path.parent.mkdir(parents=True, exist_ok=True)
    normalized_path.write_text(normalized_text, encoding="utf-8")

    runtime = build_runtime_openapi(package_root)
    runtime_text = json.dumps(runtime, indent=2, ensure_ascii=False) + "\n"
    Path(args.runtime_openapi_out).write_text(runtime_text, encoding="utf-8")

    norm_ops = operations(normalized)
    runtime_ops = operations(runtime)
    differences: list[dict[str, Any]] = []
    for key in sorted(set(norm_ops) | set(runtime_ops)):
        left, right = norm_ops.get(key), runtime_ops.get(key)
        if left is None or right is None:
            differences.append({"operation": key, "kind": "operation_presence", "normalized": bool(left), "runtime": bool(right)})
            continue
        if left["source_path"] != right["source_path"]:
            differences.append({"operation": key, "kind": "path_parameter_naming", "normalized": left["source_path"], "runtime": right["source_path"]})
        if left["parameters"] != right["parameters"]:
            differences.append({"operation": key, "kind": "parameters", "normalized": left["parameters"], "runtime": right["parameters"]})
        if request_schema(left) != request_schema(right):
            differences.append({"operation": key, "kind": "request_body_schema", "normalized": request_schema(left), "runtime": request_schema(right)})
        if left["responses"] != right["responses"]:
            differences.append({"operation": key, "kind": "response_codes", "normalized": left["responses"], "runtime": right["responses"]})

    counts: dict[str, int] = {}
    for item in differences:
        counts[item["kind"]] = counts.get(item["kind"], 0) + 1

    probes = semantic_probes(package_root)
    manifest = {
        "schema_version": "tractian-contract-normalization-manifest-v1-candidate",
        "raw_contract_sha256": sha256_bytes(raw_bytes),
        "normalized_contract_sha256": sha256_bytes(normalized_text.encode()),
        "runtime_openapi_sha256": sha256_bytes(runtime_text.encode()),
        "openapi_version": normalized.get("openapi"),
        "duplicate_keys": loader.duplicates,
        "normalized_operation_count": len(norm_ops),
        "normalized_unique_path_count": len(normalized.get("paths") or {}),
        "runtime_operation_count": len(runtime_ops),
        "runtime_unique_path_count": len(runtime.get("paths") or {}),
        "structural_operation_match": set(norm_ops) == set(runtime_ops),
    }
    Path(args.manifest_out).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = {
        "schema_version": "tractian-contract-conformance-report-v1-candidate",
        "manifest": manifest,
        "difference_counts": counts,
        "differences": differences,
        "semantic_probes": probes,
        "status": "CANDIDATE_NOT_FROZEN",
    }
    Path(args.report_out).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": report["status"],
        "structural_operation_match": manifest["structural_operation_match"],
        "operations": len(norm_ops),
        "paths": manifest["normalized_unique_path_count"],
        "duplicate_keys": loader.duplicates,
        "difference_counts": counts,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
