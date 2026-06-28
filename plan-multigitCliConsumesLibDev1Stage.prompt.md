## Plan: multigit CLI consumes multigit-lib (0.12.0.dev1 stage)

Migrate the current CLI implementation to consume published `multigit-lib==0.0.1.dev2` with minimal behavioral impact, preserving command compatibility and rollback safety. This stage is readiness-only (no CLI publication execution), checkpoint-driven, and portable across separate environments/sessions.

After each completed step, update:

1. `python-multigit-diseno-final.md` in the `Current Refactoring Status` section.
2. The stage checkpoint subsection in this file.

**Steps**
1. Phase 0 - Scope lock and baseline references.
2. Lock stage boundary: readiness-only; do not execute CLI publication in this stage.
3. Lock CLI target version: `0.12.0.dev1` (`-V` output and metadata must align).
4. Lock dependency mode: hybrid (`editable local lib` as default execution lane for Phases 0-4 + dedicated `TestPyPI verification lane` in Phase 5).
5. Lock rollback guardrail: no legacy deletions in `src/multigit` or `src/tests` in this stage.
6. Gate checkpoint C0: all above constraints explicitly documented before code edits.
If any lock constraint conflicts with a migration step, the lock constraint takes precedence and the step must be scoped to avoid the violation. Document the constraint application in checkpoint evidence. Additions to `src/tests/` are permitted; only deletions are prohibited.

7. Phase 1 - Baseline capture and reproducibility.
8. Capture baseline command signatures and exit codes for `-h`, `-V`, `--status`, `--run` using representative fixtures.
9. Capture baseline negative paths (missing file, malformed YAML, schema errors, git failure) with expected exit behavior.
10. Re-run baseline matrix twice to ensure reproducibility and detect flakiness.
11. Gate checkpoint C1/C2: baseline signatures and negative-path matrix are stable.

12. Phase 2 - Adapter seam with no behavior drift.
13. Introduce migration seam in CLI flow (adapter/wrapper boundary) while keeping default behavior unchanged.
14. Validate no output/exit drift after seam insertion.
15. Gate checkpoint C3: baseline signatures remain unchanged.

16. Phase 3 - Incremental command-path migration.
17. Migrate version path first (metadata/version retrieval path only).
18. Validate `-V == 0.12.0.dev1` and unchanged help output.
19. Gate checkpoint C4: version and help checks pass.
20. Migrate `--status` domain/orchestration calls to `multigit_lib`, preserving rendering and exit mapping.
21. Validate status golden scenarios (labels, order, semantics).
22. Gate checkpoint C5: status parity passes.
23. Migrate `--run` domain/orchestration calls to `multigit_lib`, preserving rendering and exit mapping.
24. Validate run-flow fixtures (transitions, side effects, terminal statuses).
25. Gate checkpoint C6: run parity passes.

26. Phase 4 - Exception and dependency hardening.
27. Finalize exception translation contract (`multigit_lib` errors to CLI-facing messages + exit codes).
28. Validate negative-path matrix against baseline.
29. Gate checkpoint C7: exception compatibility passes.
30. Apply CLI/runtime dependency declaration for `multigit-lib` compatibility range.
31. Validate full offline suite in editable-local lane.
32. Gate checkpoint C8: editable-local full suite passes.

33. Phase 5 - External verification lane and closeout.
34. Switch to the dedicated TestPyPI verification lane: create a clean virtualenv and install `multigit-lib==0.0.1.dev2` from TestPyPI.
35. Run CLI smoke/integration matrix under TestPyPI-installed lane.
36. Compare key outcomes and exit codes with editable-local lane.
37. Gate checkpoint C9: lane parity passes.
38. Synchronize stage docs/changelog/evidence index.
39. Confirm no legacy retirement occurred.
40. Produce handoff packet with last completed checkpoint, next checkpoint, blockers, and rollback point.
41. Gate checkpoint C10: all checkpoints green and documented.
If any gate checkpoint fails validation: (1) Do not proceed to the next step. (2) Document the failure and its evidence in the checkpoint subsection. (3) Attempt one remediation pass limited to the current phase. (4) If the checkpoint still fails after remediation, record it as a blocker in the Session Handoff Template and stop. Do not skip checkpoints.

**Relevant files**
All paths are relative to repository root (`python-multigit/`).

- `python-multigit-diseno-final.md` - authoritative split-stage governance and status tracking.
- `plan-multigitLibDev2ParityStage.prompt.md` - style/reference for phase/step planning format.
- `src/multigit/__main__.py` - CLI entrypoint and command routing behavior.
- `src/multigit/subrepos.py` - legacy orchestration/rendering coupling baseline.
- `src/multigit/gitrepo.py` - legacy domain behavior baseline.
- `src/multigit/subrepofile.py` - legacy load/validation baseline.
- `src/tests/` - CLI-facing compatibility regression tests.
- `lib/src/multigit_lib/__init__.py` - published API surface and version.
- `lib/src/multigit_lib/subrepos_orchestration.py` - library-safe orchestration consumed by CLI.
- `lib/tests/` - domain parity tests owned by library component.
- `pyproject.toml` - CLI metadata/version/dependency declarations.
- `Makefile` - root smoke lane policy.
- `lib/Makefile` - component lane policy and docs gates.

**Verification**
1. Checkpoint cadence is enforced: each integration step is followed by immediate validation.
2. Baseline and negative-path evidence are captured before migration changes.
3. Version gate passes: CLI reports `0.12.0.dev1` via `-V`.
4. Status and run parity gates pass against baseline signatures.
5. Exception mapping gate passes for negative-path matrix.
6. Editable-local lane passes full offline suite.
7. TestPyPI lane parity passes against editable-local outcomes.
8. No legacy retirements are performed in this stage.
9. Stage docs and evidence are synchronized at closeout.

**Decisions**
- Included scope: minimal-impact CLI migration to consume `multigit_lib` with strict checkpoint gates.
- Excluded scope: CLI publication execution, rename gate (`multigit_lib` -> `multigit`), legacy deletions, and final architecture-purity refactors.
- Target CLI version for this stage: `0.12.0.dev1`.
- Dependency execution mode: hybrid (`editable local` + `TestPyPI verification`).

**Session Handoff Template**
Use this block at the end of each work session:

- Last completed checkpoint: `Cx`
- Last successful command matrix run: `<timestamp + lane>`
- Next checkpoint to execute: `Cy`
- Open blockers: `<none | list>`
- Rollback point: `<commit/tag/patch reference>`
- Evidence artifacts updated: `<files/paths>`

**Further Considerations**
1. Set the `multigit-lib` dependency range in `pyproject.toml` to `>=0.0.1.dev2,<1` for this stage. This range must also appear verbatim in the stage governance doc and changelog.
2. Before starting Phase 4, document the chosen evidence storage format (text snapshots or structured assertions) in `python-multigit-diseno-final.md` under a new `Evidence Format Decision` section. Default to text snapshots if no decision is reached by checkpoint C7.
3. Reassess root recursive orchestration policy only after this stage is complete.
