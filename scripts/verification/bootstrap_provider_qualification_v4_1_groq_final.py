#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import tarfile
import urllib.request

FROZEN_QUALIFICATION_SHA = "1ad041fdcbe4424a79239fff6382df67e8bc2bfe"
ARCHIVE_URL = f"https://github.com/pablo-marchina/academy-tractian/archive/{FROZEN_QUALIFICATION_SHA}.tar.gz"
ARCHIVE_PATH = Path("/tmp/academy-tractian-provider-qualification-v4-1.tar.gz")
REPO_ROOT = Path("/tmp") / f"academy-tractian-{FROZEN_QUALIFICATION_SHA}"


def main() -> int:
    urllib.request.urlretrieve(ARCHIVE_URL, ARCHIVE_PATH)
    with tarfile.open(ARCHIVE_PATH, "r:gz") as archive:
        archive.extractall("/tmp")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "."], cwd=REPO_ROOT)
    environment = dict(os.environ)
    environment["PYTHONPATH"] = "src:."
    command = [sys.executable, "-u", "scripts/verification/provider_qualification_v4_1_groq_final.py"]
    os.chdir(REPO_ROOT)
    os.execvpe(command[0], command, environment)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
