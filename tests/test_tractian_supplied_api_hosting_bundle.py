from __future__ import annotations

import base64
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "services" / "tractian-supplied-api"
EXPECTED_UPSTREAM_ZIP_SHA256 = "37546f7abad4c573ab36384a171161f3ba6c7258024341cc42f0881d9606d134"
EXPECTED_UPSTREAM_MAIN_SHA256 = "a9bdfb8a5fc85e8f169438984f787ad5fd0db95cdd2dc41a15e05ca363a3ca78"
FORBIDDEN_CASE_FIELDS = {"root_question", "mode", "expected_path"}


def _runtime_bundle() -> bytes:
    parts = sorted(SERVICE.glob("runtime.bundle.b64.part*"))
    assert parts
    encoded = b"".join(item.read_bytes().strip() for item in parts)
    return base64.b64decode(encoded, validate=True)


def _read_tar_member(archive: tarfile.TarFile, basename: str) -> bytes:
    member = next(item for item in archive.getmembers() if Path(item.name).name == basename)
    handle = archive.extractfile(member)
    assert handle is not None
    return handle.read()


def test_supplied_api_hosting_manifest_matches_preserved_source() -> None:
    manifest = json.loads((SERVICE / "manifest.json").read_text(encoding="utf-8"))
    bundle = _runtime_bundle()
    assert manifest["upstream_zip_sha256"] == EXPECTED_UPSTREAM_ZIP_SHA256
    assert hashlib.sha256(bundle).hexdigest() == manifest["runtime_bundle_sha256"]
    assert len(list(SERVICE.glob("runtime.bundle.b64.part*"))) == manifest["runtime_bundle_parts"]
    assert manifest["gold_material_deployed"] is False

    with tarfile.open(fileobj=io.BytesIO(bundle), mode="r:gz") as archive:
        main_py = _read_tar_member(archive, "main.py")
    assert hashlib.sha256(main_py).hexdigest() == EXPECTED_UPSTREAM_MAIN_SHA256
    assert manifest["upstream_main_py_sha256"] == EXPECTED_UPSTREAM_MAIN_SHA256


def test_runtime_data_bundle_excludes_evaluator_gold() -> None:
    bundle = _runtime_bundle()
    with tarfile.open(fileobj=io.BytesIO(bundle), mode="r:gz") as archive:
        names = {item.name for item in archive.getmembers() if item.isfile()}
        basenames = {Path(name).name for name in names}
        assert "cases.parquet" not in basenames
        assert "expected-paths.json" not in basenames
        assert "test-scenarios.md" not in basenames
        assert all("/eval/" not in f"/{name}" for name in names)
        cases = json.loads(_read_tar_member(archive, "cases.json").decode("utf-8"))

    assert len(cases) == 17
    assert all(isinstance(item, dict) for item in cases)
    assert all(FORBIDDEN_CASE_FIELDS.isdisjoint(item) for item in cases)
    expected_fields = {"id", "ticket_id", "company_id", "user_id", "asset_id", "message"}
    assert all(set(item) == expected_fields for item in cases)
