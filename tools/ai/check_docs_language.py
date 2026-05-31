#!/usr/bin/env python3
"""Validate that AI support Markdown files are written in English."""

from __future__ import annotations

import pathlib
import sys

from langdetect import DetectorFactory
from langdetect import LangDetectException
from langdetect import detect_langs


ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

AI_DOC_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "docs" / "AI_DEVELOPMENT_PLAYBOOK.md",
    ROOT / "docs" / "AI_DOCS_LANGUAGE_POLICY.md",
]

# Keep detection deterministic across runs.
DetectorFactory.seed = 0


def main() -> int:
    errors: list[str] = []

    for file_path in AI_DOC_FILES:
        if not file_path.exists():
            errors.append(f"Missing required file: {file_path.relative_to(ROOT)}")
            continue

        text = file_path.read_text(encoding="utf-8")
        try:
            ranked_langs = detect_langs(text)
        except LangDetectException as exc:
            errors.append(
                f"{file_path.relative_to(ROOT)}: language detection failed ({exc})."
            )
            continue

        if not ranked_langs:
            errors.append(
                f"{file_path.relative_to(ROOT)}: language detection returned no result."
            )
            continue

        top_match = ranked_langs[0]
        if top_match.lang != "en":
            errors.append(
                f"{file_path.relative_to(ROOT)}: detected '{top_match.lang}' (confidence {top_match.prob:.3f}), expected 'en'."
            )

    if errors:
        print("AI docs language check FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("AI docs language check OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
