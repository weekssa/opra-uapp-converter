#!/usr/bin/env python3
"""Bump the tracked project VERSION using Semantic Versioning."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def parse_version(value: str) -> tuple[int, int, int]:
    match = SEMVER_RE.fullmatch(value.strip())
    if not match:
        raise ValueError(f"Invalid VERSION value: {value!r}; expected MAJOR.MINOR.PATCH")
    return tuple(int(part) for part in match.groups())


def bump_version(value: str, part: str) -> str:
    major, minor, patch = parse_version(value)
    if part == "major":
        major, minor, patch = major + 1, 0, 0
    elif part == "minor":
        minor, patch = minor + 1, 0
    elif part == "patch":
        patch += 1
    else:
        raise ValueError(f"Unsupported version bump: {part}")
    return f"{major}.{minor}.{patch}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bump", choices=("major", "minor", "patch"), required=True)
    args = parser.parse_args()

    current = VERSION_FILE.read_text(encoding="utf-8").strip()
    updated = bump_version(current, args.bump)
    VERSION_FILE.write_text(updated + "\n", encoding="utf-8")
    print(f"Version: {current} -> {updated} ({args.bump})")


if __name__ == "__main__":
    main()
