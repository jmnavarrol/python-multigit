# CLI Migration and Legacy-Retirement Preparation: Dev6 Stage<a name="top"></a>

## Stage Status

**Status:** Documentation review approved; implementation authorised to begin at D1

**Stage:** Dev6

**Scope:** Retire the legacy root Python module and complete the final `cli/` + `lib/` split, with all root `src/` content dispositioned and the entire root `src/` directory removed after the specified ownership, compatibility, and zero-reference gates pass.

**Baseline:** Dev5 is complete and the repository is already operating in the transitional split state: the authoritative implementation lives under `lib/` and `cli/`, while the root `src/` tree remains as compatibility and retirement coverage.

**Execution rule:** This document is the authoritative plan for Dev6. The project owner approved the documentation-review gate on 2026-OCT-10. Implementation may begin at D1; later destructive changes remain gated by their specified evidence and acceptance criteria.

**Development rule:** Work in the documented checkpoint order. Preserve the compatibility baseline until the relevant retirement gate passes, and do not remove root `src/` contents before their ownership, replacements, and references have been verified.

[back to top](#top)

## Objectives

1. Define the exact development path for retiring the legacy root Python package and shifting the repository to the final split architecture.
2. Preserve the root repository as the control surface while making `lib/` and `cli/` the only authoritative implementation and packaging homes.
3. Create an explicit migration sequence for the remaining legacy code, tests, docs, and package metadata.
4. Define the zero-reference, compatibility, and rollback gates that must pass before any root package removal is accepted.
5. Begin implementation only after the documentation review gate is approved; that approval is now recorded below.

[back to top](#top)

## Current State and Target State

### Current state

The project is in the transitional split state:

- `lib/` is the source of truth for the reusable library distribution.
- `cli/` is the source of truth for the command-line distribution.
- The root `src/` tree still exists as a compatibility layer and as the migration bridge for legacy behaviour.
- The root `Makefile` and compatible packaging surfaces remain available so the project can continue working while the split is being completed.
- Dev5 has validated the split packaging, installed-library integration, and TestPyPI publication flows.

### Target state

The final architecture is:

- `lib/` owns the library domain logic and all library-specific tests and docs.
- `cli/` owns argument parsing, config resolution, rendering, exit-code behavior, and CLI tests/docs.
- The legacy root package is fully retired, including legacy runtime shims, compatibility-only code paths, and root-level package metadata where appropriate.
- The repository-root `src/` directory is completely removed after every code, test, and documentation responsibility it contains has been migrated to `lib/` or `cli/`, superseded by root-level project documentation where appropriate, or otherwise explicitly dispositioned. This refers only to root `src/`; component-owned `lib/src/` and `cli/src/` remain.
- The repository root remains a project control plane, not a Python runtime distribution.
- Root-level orchestration remains limited to coordination and documentation, not package ownership.

[back to top](#top)

## Development Plan for the Final Root Retirement and Split Completion

### Phase 1: Freeze the current transitional baseline

**Purpose:** Ensure the repository is in a known-good split state before removing legacy compatibility surfaces.

Actions:

- Confirm `lib/` and `cli/` are the active packaging sources.
- Confirm the root package still builds and the root compatibility flow remains available.
- Record all remaining direct references to the legacy root package and classify them as one of:
  - required compatibility shim;
  - parity support or migration bridge;
  - stale duplicate implementation;
  - packaging metadata;
  - documentation-only reference.
- Capture the current build, test, and docs status as a baseline to allow safe rollback.

Gate:

- No root package deletion is allowed until the baseline is recorded and reviewed.

[back to top](#top)

### Phase 2: Inventory and classify legacy root ownership

**Purpose:** Separate the legacy root modules into categories before any deletion or move occurs.

Targets to be reviewed:

- every item under repository-root `src/`, including `src/multigit/`, `src/multigit_cli/`, `src/tests/`, `src/sphinx/`, `src/README.md`, and `src/LICENSE`;
- root `pyproject.toml` metadata and entry-point declarations;
- root `Makefile` targets that still represent compatibility flows;
- tests that still exercise the root package directly;
- docs and examples that still advertise the old single-package layout;
- any root-level import or backend assumptions that still behave as if the legacy package is the active runtime.

Decision rule:

- Keep only documented compatibility code until a replacement path exists.
- Move domain logic and package-owned behaviour to `lib/` or `cli/`.
- Assign a final disposition to every root `src/` item: migrate it to the owning component, move shared repository guidance to the root, preserve legal material at the appropriate repository/component level, or remove it as obsolete. Do not leave unclassified files behind.
- Remove any duplicate implementation only after equivalent tests exist in the proper component.

Gate:

- Every legacy reference must have an owner and a migration reason before removal is considered.

[back to top](#top)

### Phase 3: Move remaining root-owned behavior into the correct split component

**Purpose:** Make the final ownership explicit and remove ambiguity about where logic lives.

Implementation rules:

- Library logic must live in `lib/` and not in the root compatibility package.
- CLI parsing, rendering, exit-code mapping, and command adapters must live in `cli/`.
- Migrate or supersede all required code, tests, and Sphinx documentation from repository-root `src/` into the owning component; component-owned `lib/src/` and `cli/src/` are not migration targets for deletion.
- Legacy code under `src/` may remain only as temporary compatibility glue while the migration is still in progress.
- Any direct access to root package internals from outside the compatibility layer must be removed or re-routed.

Expected outcomes:

- `lib/` holds the reusable domain workflow and repository operations.
- `cli/` holds the command-facing boundary and output decisions.
- The root package is no longer a functional implementation source of truth.

Gate:

- Component ownership must be evident in both code layout and tests before the root package can be retired.

[back to top](#top)

### Phase 4: Retire compatibility-only root entry points and reduce the root surface

**Purpose:** Remove the root package from active operation without breaking the repo during transition.

Actions:

- Replace root-only logic with component-owned equivalents.
- Remove repository-relative path fallbacks from CLI logic once the installed `cli` package is the only required runtime path.
- Remove or deprecate legacy root console entry points after the component installation path is validated.
- Sync root `Makefile` targets with the final desired behaviour: orchestrate components, not the retired root package.
- Remove root packaging metadata that is no longer used by the final distribution split.

Rules:

- The root package is retired only after both component packages are proven to cover the actual runtime behaviour.
- Any user-facing CLI command must still be available through the installed `multigit` entry point.

Gate:

- The compatibility path is still functional while removal is staged, and rollback is still possible.

[back to top](#top)

### Phase 5: Run the zero-reference and removal gate

**Purpose:** Prevent accidental deletion of still-needed behaviour.

Required checks:

- Search for remaining references to retired legacy modules and compatibility shims.
- Verify every former root `src/` item has been migrated, superseded, or explicitly removed, and that no required code, tests, documentation, or legal material exists only under that directory.
- Confirm there are no runtime references to the root package from the active CLI or library code paths.
- Confirm all tests covering the former root workflow have been migrated into the correct component suite.
- Confirm that the final CLI and library packages both pass their offline acceptance gates.
- Confirm that the repo-level orchestration still works without the root package as the primary runtime.

Removal rule:

- Delete the entire repository-root `src/` directory only after its contents have been dispositioned, replacements are validated, and no active runtime, test, documentation, packaging, or workflow reference depends on it. Do not delete the component source trees `lib/src/` or `cli/src/`.

Gate:

- Zero-reference verification passes, all required content has an owner outside root `src/`, and removal of the complete root `src/` directory leaves component tests, docs, builds, and root orchestration passing. Any retained reference must be an intentional historical note, not a dependency on files in the deleted directory.

[back to top](#top)

### Phase 6: Final split hardening and docs cleanup

**Purpose:** Complete the repository-wide transition to the final package split.

Actions:

- Update the project documentation, examples, and design snapshots to reflect the final split architecture.
- Remove obsolete root-only instructions and update all packaging guidance to point to `lib/` and `cli/`.
- Finalise the CI and release story so component-owned gates are the authoritative path.
- Validate the final repository layout against the design snapshot and the release policy.

Gate:

- Final documentation and repository structure must match the intended root-retirement design before release approval.

[back to top](#top)

## Documentation Review Gate (Approved)

The project owner approved this plan on 2026-OCT-10. The review-only hold is complete; implementation is authorised to begin at D1. Approval does not waive the migration, compatibility, zero-reference, or validation gates later in this plan.

The gate was placed before implementation because root-package retirement is structural and compatibility-sensitive. The compatibility bridge remains until replacement coverage and the retirement gates prove it is safe to remove. Approval does not authorise skipping those later gates or production publication.

[back to top](#top)

## Checkpoints

### D0: Documentation review gate

**Status:** Complete; approved 2026-OCT-10

- Confirm the full Dev6 implementation plan is complete and reflects the actual retirement path.
- Confirm the migration strategy is explicit about ownership, zero-reference checks, and rollback.
- Record that implementation is authorised now that the plan has been reviewed and approved.

**Gate:** Human approval of the design and migration sequence was required before implementation; approval is recorded above.

**Evidence:** The project owner approved the Dev6 plan on 2026-OCT-10 and authorised implementation to begin at D1.

[back to top](#top)

### D1: Baseline freeze and migration inventory

**Status:** Active; next work checkpoint

- Freeze the current transitional baseline.
- Inventory all root package references.
- Group them by compatibility, migration bridge, duplicate implementation, or stale documentation.

**Gate:** Baseline and root ownership map are recorded and approved.

[back to top](#top)

### D2: Ownership transfer and component hardening

**Status:** Pending implementation

- Move root-owned logic into `lib/` or `cli/`.
- Remove repo-relative library fallback paths from the CLI boundary.
- Ensure tests and docs match the new ownership boundaries.

**Gate:** The final source-of-truth locations are clear and verified.

[back to top](#top)

### D3: Legacy retirement and zero-reference check

**Status:** Pending implementation

- Remove or archive obsolete compatibility code.
- Migrate or supersede all required content under repository-root `src/` and delete that entire directory once its contents and references pass the removal gate.
- Confirm there are no remaining active references to the retired root package.
- Validate the CLI and library flows against the final split architecture.

**Gate:** Zero-reference pass and compatibility validation complete.

[back to top](#top)

### D4: Final split completion

**Status:** Pending implementation

- Remove stale root metadata and clean docs.
- Finalise the repository layout and the release path.
- Confirm repository-root `src/` is absent while `lib/src/` and `cli/src/` remain as component package sources.
- Confirm the root is not the package source of truth anymore.

**Gate:** Final design snapshot matches the actual repository state.

[back to top](#top)

## Acceptance Matrix

| Area | Required result | Status |
| --- | --- | --- |
| Development plan | Full root-retirement and split-completion sequence recorded | Complete |
| Documentation gate | Plan reviewed and approved before code changes | Complete |
| Root compatibility | Preserved until the retirement gates pass | Preserved |
| Ownership clarity | `lib/` and `cli/` defined as final source of truth | Documented |
| Root `src/` retirement | Entire root `src/` removed after all contents are dispositioned and gates pass | Required |
| Zero-reference gate | Required before deletion is allowed | Documented |
| Real implementation | Authorised from D1, subject to checkpoint gates | Active |

[back to top](#top)

## Risks and Decisions

1. The root package retirement is a structural change and therefore must not be implemented without a documented plan and review gate.
2. The compatibility bridge is deliberately kept in place during the split so urgent rollback is possible.
3. The final architecture must be explicit before any deletion starts; otherwise root code may be removed while a still-needed compatibility path remains.
4. Implementation is authorised after documentation approval, but root-package and root-`src/` deletion remain blocked until their specific gates pass.
5. Production publication remains out of scope until the final split state is accepted and the full release gate is satisfied.

[back to top](#top)

## Next Session Handoff

Start implementation at D1; the documentation-review hold is complete. Read this plan, the current `AGENTS.md`, and the current design snapshot. Inspect `git status` and establish the baseline without overwriting existing changes. Inventory and classify every repository-root `src/` item before moving or deleting anything. Follow D1's gate and the repository's incremental review instructions; do not jump ahead to root `src/` deletion.

[back to top](#top)

## Completion Criteria

Dev6 is complete only when the legacy root package is retired, every required root `src/` responsibility has an owned replacement or documented disposition, the entire repository-root `src/` directory is deleted, `lib/src/` and `cli/src/` remain intact, and the final split validation gates pass.

[back to top](#top)
