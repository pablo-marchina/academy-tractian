#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import tarfile
import urllib.request

DIAGNOSTIC_SHA = "426b0ecacf8b794199b78380a5de5837603e29e3"
ARCHIVE = Path("/tmp/provider-diagnostic-v1.tar.gz")
ROOT = Path("/tmp") / f"academy-tractian-{DIAGNOSTIC_SHA}"
URL = f"https://github.com/pablo-marchina/academy-tractian/archive/{DIAGNOSTIC_SHA}.tar.gz"


def main() -> int:
    urllib.request.urlretrieve(URL, ARCHIVE)
    with tarfile.open(ARCHIVE, "r:gz") as tar:
        tar.extractall("/tmp")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "."], cwd=ROOT)
    env = dict(os.environ)
    env["PYTHONPATH"] = "src:."
    command = [sys.executable, "-u", "scripts/verification/provider_failure_diagnostic_v1.py"]
    os.chdir(ROOT)
    os.execvpe(command[0], command, env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
