#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tarfile
import urllib.request

FROZEN_RUNNER_SHA = "22ef052b292bb77618973cc6447f08970dc13159"
ARCHIVE_URL = (
    "https://github.com/pablo-marchina/academy-tractian/archive/"
    f"{FROZEN_RUNNER_SHA}.tar.gz"
)
ARCHIVE_PATH = Path("/tmp/academy-tractian-provider-v4-final.tar.gz")
REPO_ROOT = Path("/tmp") / f"academy-tractian-{FROZEN_RUNNER_SHA}"


def main() -> int:
    urllib.request.urlretrieve(ARCHIVE_URL, ARCHIVE_PATH)
    with tarfile.open(ARCHIVE_PATH, "r:gz") as archive:
        archive.extractall("/tmp")

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-q", "."],
        cwd=REPO_ROOT,
    )

    candidate = os.environ.get("TOURNAMENT_CANDIDATE", "both").strip() or "both"
    max_attempts = os.environ.get("TOURNAMENT_MAX_ATTEMPTS", "0").strip() or "0"
    command = [
        sys.executable,
        "-u",
        "scripts/verification/provider_tournament_v4_final_frozen.py",
        "--candidate",
        candidate,
    ]
    if max_attempts != "0":
        command.extend(["--max-attempts", max_attempts])

    environment = dict(os.environ)
    environment["PYTHONPATH"] = "src:."
    os.chdir(REPO_ROOT)
    os.execvpe(command[0], command, environment)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
