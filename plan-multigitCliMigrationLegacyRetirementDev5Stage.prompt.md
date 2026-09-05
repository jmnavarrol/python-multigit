# CLI Migration and Legacy-Retirement Preparation: Dev5 Stage<a name="top"></a>

## Stage Status

**Status:** Planned

**Stage:** Dev5

**Scope:** Prepare the command-line distribution for migration to the design-prescribed `cli/` component and establish the gates required before legacy command and duplicate domain code can be retired.

**Baseline:** `multigit==0.12.0.dev4`; `multigit-lib==0.0.2.dev2`; transitional library import namespace `multigit_lib`.

**Execution rule:** This stage plan is the execution authority for Dev5. Implementation must preserve root legacy releaseability until installed-library CLI integration and replacement coverage have passed their gates.

**Development rule:** Before any working code is modified, bump the version of the distribution being changed. Every behaviour change follows a red/green sequence and stops for human review after the expected red tests fail.

[back to top](#top)

## Objectives

1. Introduce a self-contained `cli/` component with independent packaging, tests, documentation, and Makefile ownership.
2. Migrate command-owned code to `cli/src/multigit_cli/` while preserving `multigit` command behaviour.
3. Make the CLI consume `multigit-lib` through its declared dependency rather than repository-relative source-path fallback.
4. Add offline real-process compatibility coverage for help, version, status, run, no-argument behaviour, and relative subrepos semantics.
5. Prepare legacy retirement by classifying references, preserving replacement coverage, and defining zero-reference checks.
6. Keep the `multigit_lib` transitional namespace; the namespace rename is outside this stage.

[back to top](#top)

## Non-Goals

1. Do not rename `multigit_lib` to `multigit`.
2. Do not publish either distribution to production PyPI.
3. Do not remove the root legacy package before the CLI integration and releaseability gates pass.
4. Do not perform final architecture-purity refactors unrelated to migration and retirement preparation.
5. Do not introduce network-dependent default tests or a new test framework.

[back to top](#top)

## Checkpoints

### C0: Red design and human-review gate

**Status:** Not started

- Review existing tests for the planned change.
- Add tests for the intended future behaviour without changing implementation code.
- Run the focused tests and record the expected failures.
- Decide which distribution version must be bumped before implementation; bump the CLI, library, or both independently as applicable.
- Stop and request human review of the red tests and version decision.

**Gate:** Red tests fail for the intended reasons, the version bump is prepared or approved, and no working implementation code has changed. No later checkpoint may begin until human review approves continuation.

[back to top](#top)

### C1: Baseline and stage setup

**Status:** Not started

- Record the current branch, versions, and clean/dirty working-tree state.
- Confirm the existing offline baseline: library tests and CLI tests pass.
- Identify all current CLI-owned modules, legacy shims, duplicate implementations, packaging paths, and documentation references.
- Keep the root package buildable and publishable.

**Gate:** Baseline evidence is recorded and no unrelated changes are included.

[back to top](#top)

### C2: CLI component structure

**Status:** Not started

Create the design-prescribed component structure:

- `cli/pyproject.toml`
- `cli/Makefile`
- `cli/README.md`
- `cli/src/multigit_cli/`
- `cli/tests/`
- `cli/docs/`

Configure Hatchling, independent CLI versioning, the `multigit` console command, and dependency range `multigit-lib>=0.0.2.dev2,<1`.

**Gate:** The CLI component builds from its own metadata and owns its command implementation and tests.

[back to top](#top)

### C3: Command implementation migration

**Status:** Not started

Move or copy command-owned behaviour from the legacy package into `multigit_cli`:

- entry point and argument parsing;
- status/run adapter;
- console rendering;
- orchestration-error to exit-code translation.

Preserve `-h`, `--help`, `-V`, `--version`, `-s`, `--status`, `-r`, `--run`, no-argument behaviour, output semantics, and exit codes.

**Gate:** Component-level unit tests cover migrated parser, rendering, adapter, and exit-code behaviour.

[back to top](#top)

### C4: Installed-library boundary

**Status:** Not started

- Remove repository-relative `lib/src` `sys.path` fallback from the migrated CLI adapter.
- Use the declared `multigit_lib` dependency as the only library resolution path.
- Build a local library artifact and install it into an isolated validation environment.
- Install and run the CLI without `PYTHONPATH` source injection.

**Gate:** The installed CLI imports the selected local `multigit-lib` artifact and fails clearly when that dependency is unavailable.

[back to top](#top)

### C5: Offline CLI acceptance

**Status:** Not started

Add real subprocess coverage using local Git scaffolding for:

- short and long help;
- short and long version;
- no arguments;
- successful status;
- successful run;
- relative subrepos paths;
- recursive subrepos processing;
- repository-level error reporting and continuation.

Run the example lifecycle gate using `example/subrepos`: execute help, version, status, and run before and after `--run`, then remove generated content and verify restoration.

**Gate:** All required CLI modes pass against the installed local artifacts and the example directory is restored exactly.

[back to top](#top)

### C6: Component quality gates

**Status:** Not started

- Run library tests and CLI tests offline.
- Build library and CLI distributions from tracked inputs.
- Build component Sphinx documentation and link checks.
- Verify library-only installation does not expose the `multigit` command.
- Verify CLI installation exposes `multigit` and resolves a compatible library.
- Update root orchestration only as needed to delegate to component targets.

**Gate:** Component and root test/build/doc workflows remain functional without production-network access.

[back to top](#top)

### C7: Legacy-retirement preparation

**Status:** Not started

Classify every remaining `src/multigit` reference as one of:

- root compatibility code;
- parity-test support;
- stale duplicate implementation;
- documentation;
- packaging configuration.

Replace or re-scope parity tests that directly import legacy domain modules only after equivalent library and installed-CLI coverage exists. Treat `src/multigit/subrepos.py` as duplicated legacy logic, not as the migration source of truth.

**Gate:** Each proposed deletion has replacement coverage, a releaseability assessment, and an owner component.

[back to top](#top)

### C8: Zero-reference and closeout review

**Status:** Not started

Search for and review remaining references to:

- retired legacy modules;
- repository-relative library imports;
- `sys.path` injection for component code;
- obsolete console entry points;
- retired environment toggles;
- stale `0.0.2.dev1` current-release documentation.

Update component READMEs, Sphinx indexes, release notes, and the design snapshot. Record durable outcomes in `CHANGELOG.md`; delete this tracker only after the stage is complete and its conclusions have been promoted.

**Gate:** No unreviewed legacy references remain, and the rename gate status is explicitly recorded.

[back to top](#top)

## Acceptance Matrix

| Area | Required result | Evidence |
| --- | --- | --- |
| Library parity | Offline library suite passes | Command output recorded in checkpoint evidence |
| CLI compatibility | Required short/long modes and no-argument behaviour pass | CLI subprocess results |
| Example lifecycle | Before/after run lifecycle passes and fixture is restored | Acceptance checklist |
| Packaging | Local library and CLI artifacts install in isolation | Artifact and environment checks |
| Boundary | No repository-source fallback in migrated CLI | Search and installed run |
| Documentation | Component docs and link checks pass | Sphinx output |
| Legacy retirement | Replacement coverage and zero-reference review pass | Review record |
| Releaseability | Root legacy distribution remains buildable until gate completion | Root build output |

[back to top](#top)

## Risks and Decisions

1. The component layout decision is resolved in favour of creating `cli/` during Dev5, rather than introducing a temporary root `src/multigit_cli` package.
2. The root legacy package remains during migration so urgent compatibility releases are not blocked.
3. The transitional `multigit_lib` namespace remains unchanged until a separate rename gate.
4. The `python -m multigit` runpy warning must not be accepted as proof of console-script compatibility; the installed `multigit` console script is the required surface.
5. Ignored `build/` evidence is temporary. Permanent conclusions belong in tracked documentation and release records.

[back to top](#top)

## Completion Criteria

Dev5 is complete only when C1-C8 pass, the installed CLI acceptance gate is recorded, component packaging and documentation gates pass, replacement coverage is reviewed, and the design snapshot records the remaining blockers before namespace rename. Production publication remains out of scope.

[back to top](#top)
