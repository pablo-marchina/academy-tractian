#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tarfile
import urllib.request

RUNNER_SHA = "d60a9c44c07c803eac78768f8565034be32f51ff"
ARCHIVE_URL = f"https://github.com/pablo-marchina/academy-tractian/archive/{RUNNER_SHA}.tar.gz"
ARCHIVE_PATH = Path("/tmp/academy-tractian-v4.tar.gz")
REPO_ROOT = Path("/tmp") / f"academy-tractian-{RUNNER_SHA}"


def main() -> int:
    urllib.request.urlretrieve(ARCHIVE_URL, ARCHIVE_PATH)
    with tarfile.open(ARCHIVE_PATH, "r:gz") as archive:
        archive.extractall("/tmp")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "."], cwd=REPO_ROOT)

    candidate = os.environ.get("TOURNAMENT_CANDIDATE", "cloudflare-gpt-oss-120b")
    max_attempts = os.environ.get("TOURNAMENT_MAX_ATTEMPTS", "2").strip()
    command = [
        sys.executable,
        "-u",
        "scripts/verification/provider_tournament_v4_final_entry.py",
        "--candidate",
        candidate,
    ]
    if max_attempts not in {"", "0"}:
        command.extend(["--max-attempts", max_attempts])
    environment = dict(os.environ)
    environment["PYTHONPATH"] = "src:."
    os.chdir(REPO_ROOT)
    os.execvpe(command[0], command, environment)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
