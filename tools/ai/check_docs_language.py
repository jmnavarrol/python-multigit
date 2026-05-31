#!/usr/bin/env python3
"""Validate that AI support Markdown files are written in English."""

from __future__ import annotations

import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

AI_DOC_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "docs" / "AI_DEVELOPMENT_PLAYBOOK.md",
    ROOT / "docs" / "AI_DOCS_LANGUAGE_POLICY.md",
]

# Distinctive Spanish markers. A few hits are enough to flag likely non-English text.
SPANISH_MARKERS = {
    "agentes",
    "archivo",
    "archivos",
    "asegurar",
    "cambios",
    "carga",
    "contrato",
    "desarrollo",
    "debe",
    "deben",
    "documentacion",
    "ejecutar",
    "entorno",
    "errores",
    "flujo",
    "fuente",
    "mantener",
    "objetivo",
    "predeterminado",
    "pruebas",
    "regla",
    "repositorio",
    "riesgos",
    "siempre",
    "siguiente",
    "validacion",
}

TOKEN_RE = re.compile(r"[A-Za-zÀ-ÿ']+")


def find_suspicious_tokens(text: str) -> list[str]:
    lowered = text.lower()
    normalized = (
        lowered.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ñ", "n")
    )
    tokens = TOKEN_RE.findall(normalized)
    return [token for token in tokens if token in SPANISH_MARKERS]


def main() -> int:
    errors: list[str] = []

    for file_path in AI_DOC_FILES:
        if not file_path.exists():
            errors.append(f"Missing required file: {file_path.relative_to(ROOT)}")
            continue

        text = file_path.read_text(encoding="utf-8")
        suspicious_tokens = find_suspicious_tokens(text)

        if "¿" in text or "¡" in text:
            errors.append(
                f"{file_path.relative_to(ROOT)}: found Spanish punctuation (¿ or ¡)."
            )

        if len(suspicious_tokens) >= 3:
            sample = ", ".join(sorted(set(suspicious_tokens))[:8])
            errors.append(
                f"{file_path.relative_to(ROOT)}: found likely Spanish text markers ({sample})."
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
