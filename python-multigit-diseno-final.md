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
19. Production-publication policy: do not publish either distribution to production PyPI until the full scope of this design snapshot has been reached and the split-completion gates are satisfied. TestPyPI publication may be used for development validation.

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

1. Transitional phase (dev2, dev3, dev4, and through rename gate): multigit depends on multigit-lib>=0.0.2.dev2,<1
2. Post-split-finalization phase (after rename gate): multigit depends on multigit-lib>=1.0,<2

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

## Current Refactoring Status (2026-SEP-05)

This snapshot records the currently completed point of the split effort so later sessions can resume safely without reconstructing the PoC milestone from scratch. The transition through the 0.0.2.dev2 library stage is summarized here, and this section is updated after each completed step.

### Completed in the current milestone

1. **Dev2 Stage Complete (0.12.0.dev2)**: Legacy cleanup and boundary hardening (G0–G13) finished; duplicate lib-owned code removed; CLI tests re-scoped to command-line validation only; library-domain assertions in lib/tests.
2. **Dev3 Stage Complete (0.12.0.dev3)**: Colorized output restored to CLI via colorama integration (8 status values mapped: ERROR→RED, success→GREEN, warning→YELLOW); **Regression 1 resolved**.
3. **Dev4 Stage Complete (0.12.0.dev4 / multigit-lib 0.0.2.dev2)**: Real-time per-repository output restored through a synchronous library iterator; repository-level failures yield structured `ERROR` results and processing continues. **Regression 2 resolved**.
4. **Current State**: `multigit==0.12.0.dev4` and `multigit-lib==0.0.2.dev2` are published to TestPyPI and externally verified on another machine. Local tests, packaging, documentation, reliable library test-target execution, and the example CLI lifecycle gate are complete. Production PyPI publication is intentionally blocked until the full scope of this design snapshot is reached.
5. **Dev5 Stage Planned (CLI Migration and Legacy-Retirement Preparation)**: The next stage is tracked in `plan-multigitCliMigrationLegacyRetirementDev5Stage.prompt.md`. It will introduce the design-prescribed `cli/` component, validate the CLI against an installed `multigit-lib` artifact, and prepare legacy retirement without changing the transitional `multigit_lib` namespace.

### Explicitly not done yet

1. Production PyPI publication is intentionally deferred until the full design scope and split-completion gates are reached.
2. No rename from `multigit_lib` to `multigit` has been attempted; that remains blocked by the rename gate.
3. CLI migration and legacy-retirement preparation have not started; the Dev5 tracker is the execution authority for that work.

### Safe resume point after this snapshot

1. Dev4/dev2 is complete and published to TestPyPI; use `multigit==0.12.0.dev4` and `multigit-lib==0.0.2.dev2` as the current development releases.
2. Next session candidate: begin Dev5 using `plan-multigitCliMigrationLegacyRetirementDev5Stage.prompt.md`; do not begin the namespace rename or schedule production publication yet.
3. Production publication becomes eligible only after the full scope of this design snapshot and its Definition of Done are satisfied.

### Development Stage Strategy

Each development stage is managed with the following lifecycle:

1. **Stage plan file created**: Dedicated working document `plan-multigit{Feature}Dev{N}Stage.prompt.md` (e.g., `plan-multigitColorizedOutputDev3Stage.prompt.md`) defines gates, checkpoint criteria, acceptance rules, and parity definitions.
2. **Execution authority**: The stage plan contains the complete checkpoint-by-checkpoint execution model, not this design document. Checkpoints are numbered (C1–C10, G0–G13, etc.) and tracked with status and evidence.
3. **Red/green development**: Before working code is modified, the related distribution version is bumped. Each behaviour change begins with reviewed tests for the intended future behaviour; those tests must fail for the expected reason, and implementation pauses for human review before the green step.
4. **Build evidence**: Session-temporary artifacts (gate outputs, parity matrices, test logs) captured in `build/evidence/{checkpoint}/` during active work. Ephemeral—deleted by `make clean`.
5. **Completion and promotion**: Stage outcomes recorded in "Current Refactoring Status" section (this document). CHANGELOG updated with feature summary. Source code changes committed to git.
6. **Plan file deletion**: Once stage is complete and status promoted to this design document, the stage plan file is deleted (working document, not long-term artifact).
7. **Permanent record**: Design doc (this file), CHANGELOG, source code, and git history remain. Build evidence is session-temporary.

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
2. **Resolved for Dev5:** create the design-prescribed `cli/` component now; do not introduce a temporary root `src/multigit_cli` layout.
