## Plan: multigit-lib 0.0.1.dev2 parity stage

Evolve multigit-lib from PoC packaging-only status to offline feature parity for library-owned behavior using a copy-first strategy, ending at a pre-publish release-candidate state where CLI migration can begin safely. The recommended path is to copy domain modules first with minimal behavioral changes, copy tests by ownership, complete library docs, and pass explicit parity/release gates for 0.0.1.dev2 without publishing in this stage. After each completed step, update the "Current Refactoring status" and "Completed in the current milestone" sections in python-multigit-diseno-final.md.

**Steps**
1. Phase 0 - Scope lock and baseline references.
2. Confirmed: this stage ends at "ready to start main-code migration to consume library" and excludes CLI entrypoint migration itself.
3. Completed: baseline legacy behavior from src/multigit as parity source, especially Gitrepo.status, Gitrepo.update, Subrepofile.load, and current status/error semantics. Baseline captured: Gitrepo.status statuses are NOT_CLONED, ERROR, WRONG_REMOTE, EMPTY, DIRTY, PENDING_UPDATE, UP_TO_DATE; Gitrepo.update outcomes are CLONED, UPDATED, or passthrough terminal/error states; Subrepofile.load returns normalized absolute paths plus gitref_type in {branch, tag, commit, None} and raises SubrepofileError for YAML/schema/permission issues.
4. Completed: copy-first guardrail is enforced for this stage: do not move or delete legacy code/tests/docs; keep current root build/test/release workflows operational so urgent bugfix publication remains possible outside this stage, while this stage does not execute publication.
5. Completed: lib release target is updated to 0.0.1.dev2 in lib/src/multigit_lib/__init__.py and changelog draft for this stage. Depends on 2.
6. Phase 1 - Compatibility-first copy preparation (before large copy operations).
7. Define only the minimal public surface needed for this stage in lib/src/multigit_lib/__init__.py so copied code is importable/testable without redesigning behavior. Depends on 3.
8. Preserve legacy status strings, exception handling, and printing behavior in copied code unless a change is strictly required for packaging/tests in this stage. Depends on 7.
9. Defer cmd/lib boundary-purity refactors (rendering separation, exception-model redesign, strict data-contract cleanup) to post-split phases. Depends on 7.
10. Phase 2 - Core module copy into lib.
11. Copy domain modules from src/multigit into lib/src/multigit_lib in this order: gitrepo.py, subrepofile.py, subrepos_schema.yaml, then controlled parts of subrepos orchestration that contain no direct stdout/stderr writes, no sys.exit calls, and no colorama imports. Depends on 8.
12. Keep mixed responsibilities in copied subrepos logic as close as possible to legacy behavior for parity; only adjustments required to resolve import errors or packaging failures; do not change function signatures, return values, exception types, or output strings. Depends on 11.
13. Update lib/pyproject.toml runtime dependencies to match copied domain code requirements (GitPython, PyYAML, Cerberus; keep colorama out of lib unless strictly unavoidable). Depends on 11.
14. Phase 3 - Test copy and parity safety net.
15. Expand lib/tests from smoke-only to ownership-based coverage: copy gitrepo tests and fixtures from src/tests first, then subrepos domain tests.
16. Add explicit parity tests comparing legacy module outputs vs new library outputs for representative scenarios (status matrix, updates, error/edge cases) using offline fixtures. If a parity test reveals a behavioral difference that cannot be resolved without a non-minimal change, document the delta in lib/CHANGELOG.md under a "Known Parity Deltas" section and escalate to a decision before proceeding to Phase 4.
17. Keep root/legacy tests runnable during transition; avoid deleting legacy tests until parity evidence is complete. Parallel with 15-16 where feasible.
18. Phase 4 - Documentation parity for library consumers.
19. Upgrade lib/docs/api.rst from placeholder to real API coverage for copied modules and exceptions.
20. Update lib/docs/index.rst from PoC language to parity-stage language and include current boundaries (what is in lib vs still in CLI/legacy).
21. Add/extend transitional notes in lib/docs (or existing docs) to state that current stage prioritizes split ease and behavior parity, while target architecture refactors are deferred. Depends on 12.
22. Keep top-level design/status docs updated after each completed step, specifically "Current Refactoring status" and "Completed in the current milestone" in python-multigit-diseno-final.md, and reflect dev2 progress plus remaining blocker list for CLI migration start gate. Depends on 16 and 20.
23. Phase 5 - Release-readiness and migration-start gate.
24. Run component gates in lib: make test, make doc, make build, then clean virtualenv installation smoke from locally built artifacts.
25. Validate parity gate checklist is green: offline tests passing, behavior parity confirmed for required operations, docs updated, changelog updated, dependencies complete.
26. Prepare TestPyPI publication bundle/checklist for 0.0.1.dev2 (credentials, command, rollback notes) but do not execute publication in this stage, including urgent bugfix publication.
27. Declare "ready to start main code migration to use library" only when 25-26 pass, no legacy files under src/multigit/ or src/tests/ have been deleted or moved, root-level make test still passes without modification, and unresolved blockers are documented with owners.

**Relevant files**
All paths in this section are relative to the git repository root (`python-multigit/`).

- src/multigit/gitrepo.py - parity source for repository status/update logic.
- src/multigit/subrepofile.py - parity source for YAML/schema validation behavior.
- src/multigit/subrepos.py - mixed module to split into library-safe orchestration vs CLI rendering concerns.
- src/multigit/subrepos_schema.yaml - schema asset to migrate into library package data.
- lib/src/multigit_lib/__init__.py - version and public API exports for dev2.
- lib/pyproject.toml - library package metadata and runtime dependencies.
- lib/tests/test_smoke.py - current baseline tests to expand.
- src/tests/git_scaffold.py - offline fixture utilities to reuse/adapt in lib tests.
- src/tests/gitrepo/test_gitrepo.py - primary behavior regression coverage to migrate.
- src/tests/gitrepo/test_other.py - edge-case coverage to migrate.
- src/tests/gitrepo/test_remote_operations.py - remote-operation parity checks.
- lib/docs/index.rst - parity-stage narrative and boundary updates.
- lib/docs/api.rst - concrete API documentation for migrated library symbols.
- lib/CHANGELOG.md - 0.0.1.dev2 milestone and release notes tracking.
- python-multigit-diseno-final.md - authoritative split-stage status and migration gate tracking.

**Verification**
1. Execute component library tests offline in lib and confirm migrated + parity tests pass consistently.
2. Build library docs in lib and verify API sections reflect real migrated modules and symbols.
3. Build sdist/wheel in lib and verify artifact names/version align with 0.0.1.dev2.
4. Perform clean virtualenv install validation from locally built artifacts only (no index publication in this stage).
5. Confirm install does not expose multigit CLI command.
6. Confirm behavior parity checklist against legacy implementation for status/update flows and key error scenarios.
7. Confirm design/status documents and lib changelog are synchronized with completed gates and remaining blockers.

**Decisions**
- Included scope: library parity work via copy-first additions with minimal behavior changes, tests/docs/dependency completion, pre-publish release readiness for TestPyPI, and explicit readiness gate for starting CLI migration.
- Excluded scope: actual CLI migration to consume multigit-lib, import-namespace rename gate (multigit_lib to multigit), TestPyPI publication execution, and production PyPI publication.
- Excluded scope: final architecture-purity refactors (printing/rendering separation, exception-model redesign, strict boundary cleanup) until split completion.
- Comparison/reference policy during WIP: no tags required for this stage; branch/commit references from splitting-plan are acceptable.

**Further Considerations**
1. Parity strictness recommendation: Option A exact status/error text parity for dev2; Option B semantic parity only with documented deltas. Recommendation: Option A for safer CLI migration start.
2. Subrepos strategy for this stage: Option A keep legacy behavior (including current rendering flow) with minimal edits; Option B split responsibilities now. Recommendation: Option A for fastest, lowest-risk split progression.
3. Test migration strategy: Option A copy tests then adapt imports incrementally; Option B rewrite tests from scratch around public API. Recommendation: Option A for faster coverage and lower regression risk.
