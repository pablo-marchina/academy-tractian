#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tarfile
import urllib.request

DIAGNOSTIC_SHA = "8cec9f8d7e596bda27a4459ac4130319547d2f5e"
ARCHIVE = Path("/tmp/groq-benchmark-rate-v2.tar.gz")
ROOT = Path("/tmp") / f"academy-tractian-{DIAGNOSTIC_SHA}"
URL = f"https://github.com/pablo-marchina/academy-tractian/archive/{DIAGNOSTIC_SHA}.tar.gz"


def main() -> int:
    urllib.request.urlretrieve(URL, ARCHIVE)
    with tarfile.open(ARCHIVE, "r:gz") as tar:
        tar.extractall("/tmp")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "."], cwd=ROOT)
    process = subprocess.run(
        [sys.executable, "-u", "scripts/verification/groq_benchmark_rate_diagnostic_v2.py"],
        cwd=ROOT,
        check=False,
    )
    return process.returncode


if __name__ == "__main__":
    raise SystemExit(main())
