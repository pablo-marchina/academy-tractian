from __future__ import annotations

import argparse
import re
from importlib import metadata
from pathlib import Path

_LOCK_LINE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s]+)$")
_BOOTSTRAP_ALLOWLIST = {"pip", "setuptools", "wheel"}
_PROJECT_DISTRIBUTIONS = {"academy-tractian", "academy-tractian-e2"}


def canonical_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def load_lock(path: Path) -> dict[str, tuple[str, str]]:
    locked: dict[str, tuple[str, str]] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = _LOCK_LINE.fullmatch(line)
        if match is None:
            raise ValueError(f"non_exact_lock_entry:{line_number}")
        display_name, expected_version = match.groups()
        key = canonical_name(display_name)
        if key in locked:
            raise ValueError(f"duplicate_lock_entry:{key}")
        locked[key] = (display_name, expected_version)
    if not locked:
        raise ValueError("empty_dependency_lock")
    return locked


def installed_versions() -> dict[str, str]:
    installed: dict[str, str] = {}
    for distribution in metadata.distributions():
        name = distribution.metadata.get("Name")
        if not name:
            continue
        installed[canonical_name(name)] = distribution.version
    return installed


def validate_lock(
    locked: dict[str, tuple[str, str]],
    installed: dict[str, str],
    *,
    require_complete_environment: bool,
) -> list[str]:
    violations: list[str] = []
    for key, (_, expected_version) in sorted(locked.items()):
        actual = installed.get(key)
        if actual is None:
            violations.append(f"missing:{key}")
        elif actual != expected_version:
            violations.append(f"version_mismatch:{key}:{expected_version}:{actual}")

    if require_complete_environment:
        allowed_unlocked = _BOOTSTRAP_ALLOWLIST | _PROJECT_DISTRIBUTIONS
        unexpected = sorted(set(installed) - set(locked) - allowed_unlocked)
        violations.extend(f"unlocked_installed_distribution:{name}" for name in unexpected)
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the installed Python dependency set drifts from requirements.lock."
    )
    parser.add_argument("--lock", type=Path, default=Path("requirements.lock"))
    parser.add_argument(
        "--allow-subset",
        action="store_true",
        help="Validate locked versions that are installed without requiring every lock entry to be present.",
    )
    args = parser.parse_args()

    try:
        locked = load_lock(args.lock)
        installed = installed_versions()
        if args.allow_subset:
            locked_for_validation = {key: value for key, value in locked.items() if key in installed}
            violations = validate_lock(
                locked_for_validation,
                installed,
                require_complete_environment=False,
            )
        else:
            violations = validate_lock(
                locked,
                installed,
                require_complete_environment=True,
            )
    except (OSError, ValueError) as exc:
        print("PYTHON_DEPENDENCY_LOCK=FAIL")
        print(f"PYTHON_DEPENDENCY_LOCK_ERROR={exc}")
        return 1

    if violations:
        print("PYTHON_DEPENDENCY_LOCK=FAIL")
        print(f"PYTHON_DEPENDENCY_LOCK_VIOLATIONS={len(violations)}")
        for violation in violations:
            print(f"PYTHON_DEPENDENCY_LOCK_VIOLATION={violation}")
        return 1

    print("PYTHON_DEPENDENCY_LOCK=PASS")
    print(f"PYTHON_DEPENDENCY_LOCK_ENTRIES={len(locked)}")
    print(f"PYTHON_INSTALLED_DISTRIBUTIONS={len(installed)}")
    print(f"PYTHON_DEPENDENCY_LOCK_COMPLETE_ENVIRONMENT={str(not args.allow_subset).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
