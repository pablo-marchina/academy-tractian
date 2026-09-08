#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tarfile
import urllib.request

RUNNER_SHA = "9ef6dcc72e221476256965ce4e9f6a19ec7dc416"
ARCHIVE_URL = (
    "https://github.com/pablo-marchina/academy-tractian/archive/"
    f"{RUNNER_SHA}.tar.gz"
)
ARCHIVE_PATH = Path("/tmp/academy-tractian-v4.tar.gz")
EXTRACT_ROOT = Path("/tmp")
REPO_ROOT = EXTRACT_ROOT / f"academy-tractian-{RUNNER_SHA}"


def main() -> int:
    urllib.request.urlretrieve(ARCHIVE_URL, ARCHIVE_PATH)
    with tarfile.open(ARCHIVE_PATH, "r:gz") as archive:
        archive.extractall(EXTRACT_ROOT)

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-q", "."],
        cwd=REPO_ROOT,
    )

    candidate = os.environ.get("TOURNAMENT_CANDIDATE", "cloudflare-gpt-oss-120b")
    max_attempts = os.environ.get("TOURNAMENT_MAX_ATTEMPTS", "2")
    command = [
        sys.executable,
        "-u",
        "scripts/verification/provider_tournament_v4_final.py",
        "--candidate",
        candidate,
    ]
    if max_attempts.strip() not in {"", "0"}:
        command.extend(["--max-attempts", max_attempts.strip()])

    environment = dict(os.environ)
    environment["PYTHONPATH"] = "src:."
    os.chdir(REPO_ROOT)
    os.execvpe(command[0], command, environment)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
