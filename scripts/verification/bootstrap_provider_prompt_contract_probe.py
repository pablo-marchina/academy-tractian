#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tarfile
import urllib.request


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing:{name}")
    return value


def main() -> int:
    sha = required("PROVIDER_PROMPT_PROBE_SHA")
    if len(sha) != 40 or any(ch not in "0123456789abcdef" for ch in sha.lower()):
        raise RuntimeError("invalid:PROVIDER_PROMPT_PROBE_SHA")
    archive = Path("/tmp/provider-prompt-contract-probe.tar.gz")
    root = Path("/tmp") / f"academy-tractian-{sha}"
    url = f"https://github.com/pablo-marchina/academy-tractian/archive/{sha}.tar.gz"
    urllib.request.urlretrieve(url, archive)
    with tarfile.open(archive, "r:gz") as tar:
        tar.extractall("/tmp")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "."], cwd=root)
    process = subprocess.run(
        [sys.executable, "-u", "scripts/verification/provider_prompt_contract_probe.py"],
        cwd=root,
        check=False,
    )
    return process.returncode


if __name__ == "__main__":
    raise SystemExit(main())
