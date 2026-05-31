#!/usr/bin/env python3
"""List AI-support Markdown files declared in AI docs language policy."""

from __future__ import annotations

import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
POLICY_FILE = ROOT / "docs" / "AI_DOCS_LANGUAGE_POLICY.md"


def extract_scope_lines(policy_text: str) -> list[str]:
    lines = policy_text.splitlines()
    in_scope = False
    scope_items: list[str] = []

    for line in lines:
        if line.strip() == "## Scope":
            in_scope = True
            continue

        if in_scope and line.startswith("## "):
            break

        if in_scope and line.lstrip().startswith("- "):
            item = line.strip()[2:].strip()
            item = item.strip("`")
            if item.endswith(".md"):
                scope_items.append(item)

    return scope_items


def main() -> int:
    if not POLICY_FILE.exists():
        print(f"Missing policy file: {POLICY_FILE}", file=sys.stderr)
        return 1

    try:
        policy_text = POLICY_FILE.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Failed to read policy file: {exc}", file=sys.stderr)
        return 1

    scope_items = extract_scope_lines(policy_text)
    if not scope_items:
        print("No markdown files found in policy Scope section.", file=sys.stderr)
        return 1

    for item in scope_items:
        print(item)

    return 0


if __name__ == "__main__":
    sys.exit(main())
