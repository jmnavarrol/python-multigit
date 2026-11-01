# AI Development Playbook for python-multigit

## Purpose
This document is intended for AI agents that modify the python-multigit repository in future iterations. Its goal is to reduce context errors and accelerate safe changes.

## 1. Essential Technical Context

### 1.1 Application Entry Point
- Script CLI: `cli/src/multigit_cli/__main__.py`
- Main behaviors:
  - `--run`: processes subrepositories and applies changes.
  - `--status`: reports status only.
  - `--version` and `--help`: CLI utilities.

### 1.2 Component Responsibilities
- `cli/src/multigit_cli/subrepos_orchestration.py`
  - Locates `subrepos` files from the working directory or parent Git repository root.
  - Loads definitions through the CLI-owned parser, walks recursively, and renders results.

- `cli/src/multigit_cli/subrepofile.py`
  - Loads YAML, validates it with the CLI-owned schema, and resolves paths relative to each file.

- `lib/src/multigit_lib/gitrepo.py`
  - `status(repoconf)`: classifies each sandbox into statuses such as:
    - `NOT_CLONED`, `ERROR`, `WRONG_REMOTE`, `EMPTY`, `DIRTY`, `PENDING_UPDATE`, `UP_TO_DATE`.
  - `update(repoconf)`: acts according to status:
    - Clones (`CLONED`) if missing.
    - Performs checkout/pull when `PENDING_UPDATE` is detected.
    - Avoids touching repos with `DIRTY`, `WRONG_REMOTE`, `ERROR`, and similar states.

- The library accepts normalized native repository configuration and performs per-repository Git operations; it does not read configuration files.

## 2. subrepos File: Functional Contract

According to `README.md`:
- Root key: `subrepos` (list).
- Each entry requires:
  - `repo`
  - `path`
- Optionally, one of:
  - `branch`
  - `tag`
  - `commit`

Ordering semantics matter: the list is processed in order, which enables hierarchical layouts.

## 3. Official Development Workflow (Derived from Makefile)

Relevant targets:
- `test`: delegates to offline suites in `lib/tests` and `cli/tests`.
- `build`: delegates to component builds after their test and documentation gates.
- `doc`: builds component Sphinx sites and linkchecks.
- `clean`: cleans ignored root/component build artifacts.

Implications for agents:
- If you change behavior, always run `make test`.
- If you change packaging, also validate with `make build`.
- Keep clean targets limited to repository build outputs and component artifacts.
- If you touch documentation or public contracts, also run `make doc`.

Default execution rule:
- The suite run by `make test` must remain offline to avoid dependence on network access and external credentials.

Example CLI acceptance gate before stage completion/publication:
- From `example/`, begin with only the original `subrepos` file present.
- Run `multigit -h|--help`, `multigit -V|--version`, and `multigit -s|--status`; run `multigit -r|--run` last.
- Repeat all modes after `--run` to detect state-dependent regressions.
- Restore `example/` to its original state by removing generated subrepository content.
- Keep this as a development-process gate, not a Makefile target.

Publication/documentation:
- Project documentation is built with Sphinx and published from those artifacts.
- Evaluate documentation changes in the owning component under `cli/docs` or `lib/docs`.

## 4. Packaging and Dependencies (Component pyproject.toml files)

- Library distribution: `multigit-lib`; imports as `multigit_lib` and requires Python `>=3.7`.
- CLI distribution: `multigit`; imports as `multigit_cli` and requires Python `>=3.8`.
- The CLI owns YAML parsing and recursive workflows. The library owns per-repository Git operations.
- Runtime dependencies are declared independently in each component's `pyproject.toml`.
- Installed script:
  - `multigit = multigit_cli.__main__:main`
- Build backend:
  - `hatchling.build`
- Component version sources are specified by each component's Hatch metadata.

Change-safety rule:
- If you touch versioning, keep consistency with changelog and release process.
- If you change dependencies, justify runtime or development workflow impact.
- If you modify build/packaging, keep `hatchling.build` unless a formal migration is requested.

## 4.1 Sphinx Documentation Rules for Agents

- Structure and maintain content under `cli/docs` and `lib/docs` without breaking component navigation.
- Keep style consistent with reStructuredText in documentation files.
- When modifying Python docstrings/comments that are part of technical documentation, use Sphinx-compatible syntax.
- Avoid ambiguous or low-value comments; prefer clear technical descriptions focused on APIs, parameters, returns, and side effects.

## 5. Tests: How to Interpret Them Correctly

Locations: `lib/tests` and `cli/tests`

Important characteristics:
- Current framework: `unittest` (automatic discovery).
- Nature: mixed unit/integration.
- Default suite: offline (no network access).
- Remote simulation: local scaffolding of temporary Git repositories.

Local scaffolding (summary):
- Local Git fixture helpers are component-owned.
- Creates local bare remotes and temporary working repositories to populate commits/branches.
- Exposes utilities to generate scenarios equivalent to previous remote-based cases.
- Integrates into test `setUp` so each run is isolated and reproducible.

Reading results:
- If it fails with `Permission denied`, local `Repository not found`, or Git CLI errors, it is likely a local environment issue.
- If it fails on expected-state comparisons (`UP_TO_DATE`, `DIRTY`, etc.), it is likely a functional regression.

## 6. Change Guide by Task Type

### 6.1 CLI Changes
1. Modify `cli/src/multigit_cli/`.
2. Verify mutually exclusive options and help messages.
3. Run `make test`.
4. Update README if UX changes.
5. Evaluate impact on `cli/docs` and update when applicable.

### 6.2 YAML Parsing/Validation Changes
1. Modify `cli/src/multigit_cli/subrepofile.py` and, when needed, its schema.
2. Ensure normalization of `path` and `gitref_type` is preserved.
3. Run `make test`.
4. Extend or adjust CLI-local test fixtures when the contract changes.
5. Update Sphinx documentation and examples if the `subrepos` contract changes.

### 6.3 Git Logic Changes
1. Modify `lib/src/multigit_lib/gitrepo.py` for per-repository operations or `cli/src/multigit_cli/subrepos_orchestration.py` for config discovery and recursive CLI workflow.
2. Preserve existing statuses and semantics.
3. Run `make test`.
4. Explicitly report which statuses changed and why.
5. Review touched docstrings/comments to keep Sphinx compatibility.

## 7. Recommended Conventions for AI Agents

- Prioritize minimal, localized changes.
- Preserve status names and observable behavior unless explicitly requested.
- Avoid style refactors mixed with functional changes.
- Document in the final report:
  1. What changed.
  2. Why.
  3. How it was verified.
  4. What remains pending.

## 8. Reusable Prompt Templates for Agents

### 8.1 Targeted Functional Fix
"Analyze the failure in [file/test], apply the smallest change in the owning component, run its focused suite, and return a summary with root cause, logical diff, and residual risks."

### 8.2 subrepos Contract Evolution
"Extend the `subrepos` contract to support [new field], update Cerberus validation and associated tests/fixtures, preserve backward compatibility, and report impact on README and CLI."

### 8.3 Git Error Hardening
"Harden error handling in `gitrepo.py` for [case], preserve existing status semantics, and add test coverage without introducing new dependencies."

## 9. Maintenance Notes for Technical Backlog

- There is guard code `if __name__ == '__main__'` in some non-CLI modules that references an undefined `main()`; it usually does not affect library use, but it should be cleaned up in the future.
- Keep the "offline by default" principle explicit in any new test added to `make test`.
- If new scenarios are added, reuse `git_scaffold.py` before introducing mocks or external dependencies.
- Verify and constrain the real scope of `clean` when used in environments with relevant adjacent folders.
