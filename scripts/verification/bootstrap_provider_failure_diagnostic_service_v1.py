#!/usr/bin/env python3
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import threading
import urllib.request

DIAGNOSTIC_SHA = "426b0ecacf8b794199b78380a5de5837603e29e3"
ARCHIVE = Path("/tmp/provider-diagnostic-v1-isolated.tar.gz")
ROOT = Path("/tmp") / f"academy-tractian-{DIAGNOSTIC_SHA}"
URL = f"https://github.com/pablo-marchina/academy-tractian/archive/{DIAGNOSTIC_SHA}.tar.gz"


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            body = b'{"status":"provider-diagnostic-running"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> int:
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print("PROVIDER_DIAGNOSTIC_HEALTH_READY", flush=True)

    urllib.request.urlretrieve(URL, ARCHIVE)
    with tarfile.open(ARCHIVE, "r:gz") as tar:
        tar.extractall("/tmp")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "."], cwd=ROOT)
    env = dict(os.environ)
    env["PYTHONPATH"] = "src:."
    process = subprocess.run(
        [sys.executable, "-u", "scripts/verification/provider_failure_diagnostic_v1.py"],
        cwd=ROOT,
        env=env,
        check=False,
    )
    print(f"PROVIDER_DIAGNOSTIC_PROCESS_EXIT={process.returncode}", flush=True)
    server.shutdown()
    return process.returncode


if __name__ == "__main__":
    raise SystemExit(main())
