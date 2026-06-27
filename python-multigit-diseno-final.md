# Final Design Snapshot: python-multigit Split

## Working Repository

- GitHub repository to modify: https://github.com/jmnavarrol/python-multigit

## Final Objective

Split the current single Python distribution into two independent distributions, kept in a single Git repository and still built with hatchling:

1. A reusable library distribution.
2. A command-line distribution.

Both distributions must evolve and be versioned independently.

This split is designed to be implemented in a single repository now while preserving low-coupling boundaries for a possible future extraction into three repositories: command-line, library, and lifecycle/orchestration.

Important rollout constraint:

1. The first released `multigit-lib` version is a compatibility-focused drop-in for current behavior and contracts.
2. Full alignment with the final cmd/lib architecture goals is deferred until the split and migration process is fully completed.
3. During split-parity stages, implementation prioritizes easiest safe split progression and behavior preservation over early architectural purity refactors.

## Final Naming Decisions

### Distribution names (PyPI level)

1. multigit-lib: library distribution.
2. multigit: command-line distribution.

### Import package names (Python level)

1. multigit: import package for the library.
2. multigit_cli: internal import package for the CLI application.

### Shell command name

1. multigit: command exposed by the CLI distribution.

### Transitional naming (PoC and parallel development phase)

During the PoC and the parallel library development phase, the library must use names that do not collide with the currently published `multigit` package. The final target names (`multigit` import namespace) are applied only once the library reaches feature parity with the current implementation and the CLI is ready to be migrated to consume it.

1. Transitional PyPI distribution name: multigit-lib (unchanged from final target — no collision).
2. Transitional import package name: multigit_lib (avoids shadowing the currently installed `multigit` namespace).
3. Rename gate: the import package is renamed from `multigit_lib` to `multigit` only after the offline parity gate passes, the CLI migration has started, and the legacy `src/multigit` path is retired.

## Architecture Boundaries

### Library responsibilities (multigit-lib)

1. Receive already-processed native Python data structures.
2. Validate domain-level input coherence.
3. Execute repository status/update logic.
4. Return structured results and raise domain exceptions.

### Library non-responsibilities

1. No direct reading of config files.
2. No environment variable lookup.
3. No console rendering.
4. No sys.exit process termination behavior.

### CLI responsibilities (multigit)

1. Parse command-line arguments.
2. Resolve config sources (file, env vars, flags, future providers).
3. Parse YAML and map it to library input structures.
4. Call library services.
5. Render output and decide exit codes.

### Transitional execution mode (current split stages)

Until split completion is declared, the execution policy is intentionally compatibility-first:

1. Prefer copy-as-is of legacy implementation into `lib/` with minimal behavior changes.
2. Preserve current printing/status/exception behaviors unless a change is strictly required to make packaging, tests, or docs pass.
3. Defer architecture-purity refactors (strict rendering separation, exception-model redesign, boundary cleanup) to post-split hardening phases.
4. Keep legacy root distribution buildable and publishable throughout these stages for urgent bugfix releases.

## Data Flow Contract

1. Input adapters live in CLI (for example YAML loader).
2. CLI transforms input into native domain objects accepted by library.
3. Library processes and returns structured result objects.
4. CLI formats those results for end users.

## Pre-Implementation Constraints Gate

All implementation decisions for this split must satisfy the following constraints before code changes are considered valid:

1. Build backend continuity: hatchling remains the build backend for both distributions.
2. CLI compatibility: `multigit --run`, `multigit --status`, `-V`, and `-h` behavior must be preserved.
3. Subrepos compatibility: current YAML contract and relative path semantics remain backward compatible unless explicitly versioned.
4. Test policy: default test execution remains offline, based on local scaffolding and no external network dependency.
5. Documentation policy: Sphinx documentation remains part of deliverables when public API or behavior changes.
6. Tooling policy: no new test framework is introduced unless strictly required.
7. Transitional compatibility policy: the initial library release prioritizes drop-in compatibility over immediate target-architecture purity.
8. Final-architecture policy: strict enforcement of final cmd/lib boundary goals is applied after split completion.
9. Offline parity policy: no migration phase can advance without passing the documented offline parity gate.
10. Publish gate policy: CLI publication is blocked unless the required `multigit-lib` version is already available in the target index.
11. Test migration policy: legacy tests are explicitly migrated by responsibility (library vs CLI) before legacy deletions.
12. Legacy retirement policy: command/code removals are allowed only after replacement coverage and zero-reference checks pass.
13. CI policy: component lanes are mandatory release gates; root smoke lane is optional and non-blocking.
14. Makefile dependency policy: component Makefile targets must declare real source-to-target dependencies with concrete outputs; build/package targets must depend on test and doc quality gates.
15. Copy-first migration policy: during parity stages, code/tests/docs are copied into `lib/` and validated there; legacy sources remain in place until explicit retirement gates are met.
16. Legacy releaseability policy: throughout parity stages, the current root/legacy distribution must remain buildable and publishable so urgent bugfix releases can be produced without waiting for split completion.
17. Split-first pragmatism policy: during parity stages, prefer the direct implementation path that preserves current runtime behavior and avoids unnecessary redesign.
18. Deferred-refactor policy: enforce final architecture boundaries strictly only after split completion; before that, boundary violations inherited from legacy code may be tolerated when needed for low-risk parity.

## Target Repository Layout

Root repository acts as control surface only. It contains shared top-level guidance and recursive orchestration, while component implementation remains isolated inside component directories.

		python-multigit/
			README.md
			AGENTS.md
			Makefile  # recursive orchestration only (test/build/doc/clean)
			.bme_project
			.bme_env
			python-virtualenvs/
			cli/ # CLI distribution: multigit
				README.md
				pyproject.toml
				Makefile
				src/
					multigit_cli/
				tests/
				docs/  # sphinx stack owned by cli
			lib/ # Library distribution: multigit-lib
				README.md
				pyproject.toml
				Makefile
				src/
					multigit_lib/  # transitional name; renamed to multigit/ after rename gate
				tests/
				docs/  # sphinx stack owned by lib

Ownership rules:

1. Root directory: orchestration and cross-component guidance only.
2. cli/: command UX, adapters, rendering, exit-code decisions.
3. lib/: reusable domain processing and repository operations.
4. Each component keeps independent package metadata, tests, docs, and version stream.

## Packaging Rules

### Library
1. project.name = multigit-lib
2. Build backend: hatchling
3. Version source independent from CLI
4. Package to build during transitional phase: lib/src/multigit_lib
5. Package to build after rename gate: lib/src/multigit

### CLI
1. project.name = multigit
2. Build backend: hatchling
3. Console entry point command: multigit
4. Console entry point target: multigit_cli.__main__:main
5. Dependency on library with compatibility range

## Documentation Topology

Documentation is component-owned and recursively orchestrated:

1. lib/docs provides its own Sphinx stack and Makefile-driven doc targets.
2. cli/docs provides its own Sphinx stack and Makefile-driven doc targets.
3. Root Makefile doc target only calls component Makefile doc targets recursively.
4. Documentation publication strategy is component-local unless explicitly redefined later.

## BME Development Environment Strategy

Bash Magic Enviro remains rooted at repository top level:

1. Keep a single root `.bme_project` and root `.bme_env` as default project context.
2. Use optional subdirectory `.bme_env` files only for local context adjustments.
3. Do not introduce nested `.bme_project` files by default, to avoid unnecessary project-context switching.
4. Keep virtualenv lifecycle aligned with BME `python3-virtualenvs` conventions and root `python-virtualenvs` requirements files.

## Dependency Contract Between Distributions

CLI distribution depends on library distribution using a compatible major range:

1. Transitional phase: multigit depends on multigit-lib>=0.1,<1
2. Post-split-finalization phase: multigit depends on multigit-lib>=1.0,<2

This allows independent evolution while protecting runtime compatibility.

## Versioning Policy

### Independent versions

1. multigit-lib version is independent.
2. multigit version is independent.

### Initial baseline

1. multigit-lib: 0.1.0
2. multigit: 0.12.0

### Update rules

1. Library internal changes without API break: bump only multigit-lib.
2. CLI behavior/features without library API change: bump only multigit.
3. Library API breaking change: major bump in multigit-lib and update CLI dependency range.

### Coordinated major-bump procedure

1. If multigit-lib requires a major bump, publish the new library major first.
2. Publish a CLI release that updates dependency range to the new major.
3. Do not publish CLI with a range that is not yet available in the target package index.

## Release Order

For each release cycle:

1. Build and validate multigit-lib locally first.
2. Build and validate multigit locally against the selected multigit-lib range.
3. Publish multigit-lib to development PyPI and validate installation/compatibility.
4. Pre-flight gate for CLI publish: verify required multigit-lib version exists in target index.
5. Publish multigit to development PyPI and validate full-stack installation.
6. Publish multigit-lib to production PyPI.
7. Pre-flight gate for CLI publish: verify required multigit-lib version exists in target index.
8. Publish multigit to production PyPI.

Clarification:

1. Root repository Makefile does not orchestrate publish operations.
2. Publish commands are owned and executed per component (lib and cli).

## Operational Gates

### Offline parity gate (required before first multigit-lib stable release)

1. All migrated library tests pass offline.
2. Behavior parity is validated for subrepos loading, status, and update flows.
3. CLI compatibility checks pass for `--run`, `--status`, `-h`, and `-V` against the compatibility target behavior.

### Test migration rules

1. Tests focused on repository/domain logic migrate to library test ownership.
2. Tests focused on argument parsing, rendering, and exit-code mapping migrate to CLI test ownership.
3. During transition, legacy tests may coexist but must remain offline.

### Legacy retirement gate

1. Equivalent replacement capability exists and is reviewed.
2. Replacement tests pass offline in the owning component.
3. CLI integration with published library is validated for releasability.
4. No references to retired legacy internals remain.

### CI ownership model

1. Component CI lanes are mandatory gates for release.
2. Root smoke lane is optional and non-blocking.

## Functional Design Requirements Preserved

1. CLI remains responsible for user-facing behavior and output.
2. Library remains reusable by external programs without CLI installation.
3. Future extensions, such as configurable subrepos file naming, are handled in CLI adapters unless they require library API evolution.

## Implementation Sequence (Approved)

1. Incubate a new library track in parallel, without moving current production files from their existing locations.
2. Build the first library package, tests, and docs as a compatibility-focused drop-in until behavior parity is reached against the current implementation, using copy-first and minimal-change principles.
3. Publish a first stable `multigit-lib` release only after offline parity and compatibility checks pass.
4. Keep current CLI releaseability unchanged while the new library matures.
5. Adapt the current CLI in place to consume published `multigit-lib` through explicit adapter boundaries.
6. Validate compatibility for `--run`, `--status`, `-h`, `-V`, and subrepos semantics while releasing CLI versions that depend on `multigit-lib`.
7. After integration stability is proven, extract remaining command-only code from legacy areas into the cmd-focused structure.
8. Retire duplicated legacy internals only when replacement coverage is complete.
9. Perform the final repository layout refactor only after functional migration is complete and releases are stable.
10. Refactor both cmd and library components to fully honor the final design goals once split completion is achieved.
11. Normalize root recursive orchestration, component docs/test ownership, and future extraction seams for cmd/lib/lifecycle.

## Current Refactoring Status (2026-JUN-27)

This snapshot records the currently completed point of the split effort so later sessions can resume safely without reconstructing the PoC milestone from scratch. The 0.0.1.dev2 parity stage is tracked step-by-step, and this section is updated after each completed step.

### Completed in the current milestone

1. A new `lib/` subtree exists as an isolated PoC component for the future `multigit-lib` distribution.
2. The transitional import package name is `multigit_lib`, with version sourced dynamically from `lib/src/multigit_lib/__init__.py`.
3. The component includes its own `pyproject.toml`, `Makefile`, `README.md`, `CHANGELOG.md`, `tests/`, and `docs/`.
4. Component-local Makefile targets exist for `test`, `build`, `doc`, `upload-tmp`, and `clean`, with real source-to-target dependency modeling.
5. Offline smoke tests for `multigit_lib` import and version exposure are in place and passing.
6. Component-local Sphinx documentation is in place and builds successfully.
7. Local build validation is complete: sdist and wheel are produced successfully for the PoC component.
8. Isolated installability validation is complete: installing the PoC library does not expose the `multigit` shell command.
9. Coexistence validation is complete: the PoC `multigit_lib` package does not shadow the production `multigit` package when both are installed in the same virtualenv.
10. Root-level documentation now warns that `lib/` is a PoC incubation area and not the current production runtime source.
11. Publication to TestPyPI is complete for `multigit-lib` version `0.0.1.dev1`.
12. TestPyPI artifact availability has been externally validated at `https://test.pypi.org/project/multigit-lib/0.0.1.dev1/`.
13. Fresh-install smoke validation from TestPyPI is complete in a clean temporary virtualenv: `multigit_lib` imports successfully, `__version__` resolves to `0.0.1.dev1`, and no `multigit` CLI command is exposed.
14. Stage `0.0.1.dev2` implementation has started with Phase 0 Step 1 completed: scope lock and baseline references are established in `plan-multigitLibDev2ParityStage.prompt.md`.
15. Phase 0 Step 2 is completed and explicitly confirmed: this stage ends at "ready to start main-code migration to consume library" and excludes CLI entrypoint migration itself.
16. Phase 0 Step 3 is completed with legacy parity baseline captured from `src/multigit`: `Gitrepo.status` status semantics, `Gitrepo.update` transition outcomes, `Subrepofile.load` normalization behavior, and current error semantics are now fixed as parity reference for dev2.
17. Phase 0 Step 4 is completed with copy-first guardrail enforced: legacy code/tests/docs remain in place and this stage preserves root build/test/release workflow operability while publication execution remains out of scope.
18. Phase 0 Step 5 is completed: `multigit-lib` release target is now `0.0.1.dev2` in `lib/src/multigit_lib/__init__.py`, and `lib/CHANGELOG.md` Next Release draft was updated accordingly.

### Explicitly not done yet

1. No publication to production PyPI has been executed in this milestone.
2. No business logic has been migrated yet from `src/multigit` into the new library package.
3. No CLI adaptation work has started yet; the current CLI still runs from the legacy production implementation.
4. No rename from `multigit_lib` to `multigit` has been attempted; that remains blocked by the rename gate.

### Safe resume point after this snapshot

1. TestPyPI publication and clean-virtualenv fresh-install smoke validation are already completed for `0.0.1.dev1`.
2. Stage `0.0.1.dev2` is in progress with Steps 1-5 complete (scope lock, stage-end boundary confirmation, legacy baseline capture, copy-first guardrail enforcement, and release-target update).
3. The next immediate step is Phase 1 Step 7: define only the minimal public surface needed in `lib/src/multigit_lib/__init__.py` so copied code is importable/testable without redesigning behavior.
4. CLI adaptation may start only against a published and validated library release, with dependency range and compatibility checks gated by the documented publish policy.

## Future 3-Repository Extraction Invariants

To keep a future split into three repositories low-friction, the following must remain true:

1. Library incubation happens in parallel and does not require early relocation of current production files.
2. CLI adopts library capabilities only after a published and validated library release is available.
3. During migration, CLI adaptation is done in place first; structural extraction is deferred until integration stability is proven.
4. cli depends on lib only through explicit public interfaces and declared version ranges.
5. Root orchestration does not own component business logic.
6. Component docs, tests, and packaging metadata are self-contained.
7. Cross-component assumptions are documented as contracts, not implicit imports.
8. Lifecycle concerns (stack-wide automation/governance) remain separable from cli/lib runtime behavior.

## Definition of Done for the Split

1. Installing multigit-lib does not install or expose the multigit shell command.
2. Installing multigit exposes the multigit shell command and pulls a compatible multigit-lib.
3. Library can be imported and used directly from external Python programs.
4. New library track is developed and validated in parallel without early relocation of current production files.
5. A first stable `multigit-lib` release is published after offline parity and compatibility checks.
6. CLI migration happens in place and preserves compatibility for `--run`, `--status`, `-h`, `-V`, and subrepos semantics.
7. CLI releases depending on `multigit-lib` are validated as releasable before legacy command-code extraction begins.
8. Legacy command-only internals are retired only after the legacy retirement gate is fully satisfied.
9. Final repository layout refactor is executed only after functional migration stability is proven.
10. During transition, the initial `multigit-lib` release behaves as a compatibility drop-in and may temporarily defer strict final-boundary purity.
11. After split completion, cmd and library refactors are finalized to fully satisfy the target architecture boundaries and responsibilities.
12. Root `make test`, `make build`, and `make doc` remain functional as recursive orchestration over component Makefiles.
13. Component test suites run offline by default.
14. Component Sphinx stacks build successfully through component targets and root recursive doc target.
15. Root remains publish-agnostic; publishing is performed at component level.
16. Repository keeps low-coupling boundaries that allow future extraction into cmd/lib/lifecycle repositories.

## Open Decisions to Resolve Before Implementation

1. Final wording review for dependency-transition narrative (`>=0.1,<1` to `>=1.0,<2`) and release communications.
