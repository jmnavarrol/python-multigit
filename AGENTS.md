# AGENTS.md - Quick Guide for AI Agents

This file defines how to work on python-multigit safely, usefully, and consistently.

## 1) Project Goal
multigit manages multiple Git repositories declared in a YAML file named subrepos, processing them recursively from a base directory.

Key components:
- CLI: src/multigit/__main__.py
- Recursive orchestration: src/multigit/subrepos.py
- Per-repository Git operations: src/multigit/gitrepo.py
- YAML load/validation: src/multigit/subrepofile.py

## 2) Functional Source of Truth
Before changing behavior, always align with:
- README.md for user experience, subrepos semantics, and usage expectations.
- Makefile for the official development workflow (test, build, doc, clean, upload*).
- pyproject.toml for packaging, dependencies, entry script, and build backend.

Explicit build requirement:
- The build backend is hatchling.build (via Hatch). Do not replace or diverge from it unless explicitly required.

## 3) Official Development Commands
From the repository root:

```bash
make test
make build
make doc
make clean
```

Notes:
- make test runs unittest discover over src/tests.
- make test is the default suite and must remain offline.
- make build depends on test.
- make clean also removes potentially sensitive paths; review impact carefully before running it in non-isolated environments.

Local test scaffolding:
- The suite builds temporary local Git remotes to simulate clone/fetch/pull, branches, and repository states without network access.
- The support module is src/tests/git_scaffold.py.
- gitrepo and subrepos tests consume those local remotes in setUp.

## 4) Constraints Agents Must Respect
- Do not break CLI behavior (multigit --run, multigit --status, -V, -h).
- Preserve compatibility with the subrepos YAML structure.
- Do not introduce new test frameworks without clear necessity (current framework is unittest).
- Do not change the semantics of relative configuration paths.
- Avoid broad non-functional style-only rewrites.
- Keep Sphinx documentation as part of the deliverable when a change requires it.
- Respect the documentation structure under src/sphinx and its generation/publication workflow.
- When adding or editing Python comments/docstrings, use Sphinx-compatible syntax (reStructuredText style when applicable).

## 5) Real Risks Seen in the Suite
The suite in src/tests remains integration-like in several places, but its default execution is designed to be offline.

Risks to monitor:
- Behavior differences between local Git versions.
- Fragility from leftover state if src/tests/*/scenarios is not cleaned correctly.
- Implicit filesystem/permissions dependencies from the host OS.

When reporting test results, always distinguish:
1. Logical code failures.
2. Local environment failures (filesystem, permissions, or Git tooling).

## 6) Minimum Checklist Before Calling a Change Complete
1. Run make test and record results.
2. Verify CLI flow still works with --help and --version.
3. Confirm the subrepos contract was not unintentionally altered.
4. If build/dependencies changed, validate consistency with pyproject.toml and Makefile.
5. Briefly document functional impact and residual risks.
6. If documentation or public API is affected, update src/sphinx content and validate make doc.

## 8) What an Agent Delivery Must Include
- Short summary of functional changes.
- Modified files and reason for each change.
- Executed test results.
- Pending risks/limitations.
- Concrete next steps, if applicable.
