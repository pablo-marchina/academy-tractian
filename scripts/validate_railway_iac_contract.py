from __future__ import annotations

from pathlib import Path
import re

IAC_PATH = Path(".railway/railway.ts")


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing Railway IaC contract fragment: {needle}")


def main() -> None:
    if not IAC_PATH.is_file():
        raise SystemExit("missing .railway/railway.ts")
    text = IAC_PATH.read_text(encoding="utf-8")
    for item in (
        'export const partial = "production"', 'service("production-api"', 'service("production-web"',
        'github("pablo-marchina/academy-tractian"', 'branch: "release/production-final"',
        'dockerfilePath: "Dockerfile"', 'rootDirectory: "frontend"', 'dockerfilePath: "Dockerfile.production"',
        'healthcheck: "/health"', 'healthcheckTimeout: 60', 'healthcheck: "/"', 'healthcheckTimeout: 120',
        '"us-east4-eqdc4a": 1', 'restarts: "on_failure"', 'restartLimit: 5',
        'ACADEMY_POSTGRES_INTERNAL_DSN: preserve()', 'ACADEMY_POSTGRES_SCOPED_DSN: preserve()',
        'ACADEMY_PROVIDER_CALLS_ENABLED: preserve()', 'ACADEMY_BROWSER_IAM_MODE: preserve()',
        'ACADEMY_NEON_AUTH_BASE_URL: preserve()', 'NEON_AUTH_BASE_PATH: preserve()', 'NEON_AUTH_HOST: preserve()',
        'resources: [productionApi, productionWeb]',
    ):
        require(text, item)
    if 'service("hosted-pilot"' in text:
        raise SystemExit("historical hosted-pilot must not be managed by production IaC")
    for pattern in (r"postgres(?:ql)?://", r"ACADEMY_POSTGRES_INTERNAL_DSN\s*:\s*[\"']", r"ACADEMY_POSTGRES_SCOPED_DSN\s*:\s*[\"']", r"password\s*[:=]\s*[\"'][^\"']+"):
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise SystemExit(f"forbidden literal/secret pattern: {pattern}")
    services = re.findall(r'service\("([^"]+)"', text)
    if services != ["production-api", "production-web"]:
        raise SystemExit(f"unexpected service scope: {services!r}")
    print("RAILWAY_IAC_CONTRACT=PASS")


if __name__ == "__main__":
    main()
