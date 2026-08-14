#!/usr/bin/env python3
"""Keep README and project description synchronized with config/targets.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "targets.json"
README = ROOT / "README.md"
PROJECT_DESCRIPTION = ROOT / "docs" / "PROJECT_DESCRIPTION.md"

HEADPHONES_START = "<!-- SUPPORTED_HEADPHONES_START -->"
HEADPHONES_END = "<!-- SUPPORTED_HEADPHONES_END -->"
DESCRIPTION_START = "<!-- PROJECT_DESCRIPTION_START -->"
DESCRIPTION_END = "<!-- PROJECT_DESCRIPTION_END -->"

DESCRIPTION_PREFIX = "OPRA → UAPP/ToneBoosters EQ converter with automatic Google Drive sync. Configured: "
DESCRIPTION_LIMIT = 330


def load_target_names() -> list[str]:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    names: list[str] = []
    seen: set[str] = set()
    for target in data.get("targets", []):
        output_path = str(target["output_path"]).strip(" /")
        name = " ".join(part.strip() for part in output_path.split("/") if part.strip())
        key = name.casefold()
        if name and key not in seen:
            seen.add(key)
            names.append(name)
    return names


def build_description(names: list[str]) -> str:
    if not names:
        return DESCRIPTION_PREFIX.rstrip() + " none"

    included: list[str] = []
    for index, name in enumerate(names):
        remaining = len(names) - len(included) - 1
        candidate_items = included + [name]
        suffix = f"; +{remaining} more" if remaining > 0 else ""
        candidate = DESCRIPTION_PREFIX + "; ".join(candidate_items) + suffix
        if len(candidate) <= DESCRIPTION_LIMIT:
            included.append(name)
        else:
            break

    remaining = len(names) - len(included)
    if not included:
        return DESCRIPTION_PREFIX + f"{len(names)} configured targets"
    result = DESCRIPTION_PREFIX + "; ".join(included)
    if remaining:
        result += f"; +{remaining} more"
    return result


def replace_generated_section(text: str, start: str, end: str, body: str) -> str:
    if start not in text or end not in text:
        raise RuntimeError(f"README is missing generated markers: {start} / {end}")
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    return before + start + "\n" + body.rstrip() + "\n" + end + after


def main() -> None:
    names = load_target_names()
    description = build_description(names)

    readme = README.read_text(encoding="utf-8")
    headphone_list = "\n".join(f"- {name}" for name in names) if names else "- None configured"
    readme = replace_generated_section(readme, HEADPHONES_START, HEADPHONES_END, headphone_list)
    readme = replace_generated_section(readme, DESCRIPTION_START, DESCRIPTION_END, description)
    README.write_text(readme, encoding="utf-8")

    project_text = (
        "# Project description\n\n"
        "This file is generated from `config/targets.json`. Do not edit the description line manually.\n\n"
        f"{description}\n"
    )
    PROJECT_DESCRIPTION.write_text(project_text, encoding="utf-8")

    print(f"Updated documentation for {len(names)} configured target(s).")
    print(description)


if __name__ == "__main__":
    main()
