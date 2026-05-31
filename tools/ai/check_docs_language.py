#!/usr/bin/env python3
"""Validate that AI support Markdown files are written in English."""

from __future__ import annotations

import argparse
import pathlib
import sys

from langdetect import DetectorFactory
from langdetect import LangDetectException
from langdetect import detect_langs


ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

# Keep detection deterministic across runs.
DetectorFactory.seed = 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate that selected Markdown files are written in English.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Workspace-relative or absolute paths to markdown files.",
    )
    return parser.parse_args(argv)


def normalize_file_path(path_value: str) -> pathlib.Path:
    path_obj = pathlib.Path(path_value)
    if path_obj.is_absolute():
        return path_obj
    return ROOT / path_obj


def pretty_path(path_obj: pathlib.Path) -> str:
    try:
        return str(path_obj.relative_to(ROOT))
    except ValueError:
        return str(path_obj)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    errors: list[str] = []

    if not args.files:
        print("AI docs language check FAILED:")
        print("- No input files were provided. Pass markdown files as arguments.")
        return 1

    for file_value in args.files:
        file_path = normalize_file_path(file_value)
        file_label = pretty_path(file_path)

        if not file_path.exists():
            errors.append(f"Missing required file: {file_label}")
            continue

        try:
            text = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{file_label}: could not read file ({exc}).")
            continue

        try:
            ranked_langs = detect_langs(text)
        except LangDetectException as exc:
            errors.append(f"{file_label}: language detection failed ({exc}).")
            continue

        if not ranked_langs:
            errors.append(f"{file_label}: language detection returned no result.")
            continue

        top_match = ranked_langs[0]
        if top_match.lang != "en":
            errors.append(
                f"{file_label}: detected '{top_match.lang}' (confidence {top_match.prob:.3f}), expected 'en'."
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
