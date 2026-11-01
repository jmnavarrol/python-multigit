# Dev7 Stage Plan: Recursive Subrepos Discovery
**Overall status:** Stage 0 finished; Stage 1 not started, awaiting explicit instruction.

## Objective
Keep the [CLI/lib split](python-multigit-diseno-final.md) as the main project goal and limit this stage to checking the CLI's recursive discovery behavior: are deeper `subrepos` files found and processed, and are new nested configs exposed by updating a parent detected and added to the processing queue? Make only the smallest behavior changes needed to correct a demonstrated discovery or queueing defect.

<sub>[back to top](plan-multigitRecursiveSubreposDev7Stage.prompt.md).</sub>

## Scope
- CLI-owned traversal and offline tests.
- Finding and processing deeper `subrepos` files.
- Detecting and queueing nested configs that appear or change after a parent repository is updated.
- Explicitly test and preserve a self-target when the declared path, after normalization, resolves to the currently managed repository's worktree root.
- Preserving relative-to-config path resolution and existing CLI/library boundaries.

Out of scope: library redesign; broad behavior cleanup; cycle detection or general infinite-loop prevention; path-direction restrictions; changing error handling or exit codes; whole-tree polling passes; production release; and TestPyPI publication. Preserve, but do not otherwise redesign, existing self-update semantics. If an unrelated issue is exposed while working on the targeted behavior, record the evidence and stop for review. Do not fix it unless separately requested.

<sub>[back to top](plan-multigitRecursiveSubreposDev7Stage.prompt.md).</sub>

## Stage Lifecycle and Status Tracking
Work on the active stage through its stated completion criteria, pausing earlier only for an unexpected finding that needs clarification. At stage completion, update this document's status to `Waiting for user review`, report the evidence, and stop.

- If the review requests changes, return that stage to `In progress`, make the requested changes, revalidate, and submit it for review again.
- If the review is positive, mark the stage `Finished` in this document and stop. Do not start the next stage until the user explicitly instructs that it may begin.
- Keep each stage's status current as work proceeds; at minimum, update it when the stage is submitted for review and when the review is accepted.

<sub>[back to top](plan-multigitRecursiveSubreposDev7Stage.prompt.md).</sub>

## Current Evidence
- `Subrepos.iter_process()` updates or statuses a repository before loading that repository's nested `subrepos` file. A nested config introduced by the update should therefore be discoverable during the same traversal; this needs a regression test.
- `test_process_discovers_nested_subrepos_file` covers a parent cloned from a remote that already contains nested configuration, but not an existing checkout whose remote gains that configuration later.
- Nested paths are canonicalised by `Subrepofile.load()` relative to the declaring file.
- A self-update is identified by the normalized target resolving to the currently managed repository's worktree root, not by the raw path spelling. The test must ensure the CLI updates that repository rather than rejecting or skipping it.
- Queue deduplication currently checks paths still waiting, but not paths already processed. This may permit repeated processing or an infinite loop for cyclic declarations; that is an incidental finding, not a Dev7 requirement. If relevant evidence appears, document it as a separate follow-up and do not change it in this stage without explicit approval.

Relevant implementation and tests: [subrepos_orchestration.py](cli/src/multigit_cli/subrepos_orchestration.py), [subrepofile.py](cli/src/multigit_cli/subrepofile.py), [test_subrepos_orchestration.py](cli/tests/test_subrepos_orchestration.py), and [git_scaffold.py](cli/tests/git_scaffold.py).

<sub>[back to top](plan-multigitRecursiveSubreposDev7Stage.prompt.md).</sub>

## Stage 0: Plan Review
**Status:** Finished.

Plan reviewed and accepted. No source, test, version, or changelog changes were made in this stage. Stage 1 remains not started until the user explicitly instructs that work may begin.

<sub>[back to top](plan-multigitRecursiveSubreposDev7Stage.prompt.md).</sub>

## Stage 1: Red Tests
**Status:** Not started; requires explicit instruction after Stage 0 is finished.

Before editing tests or working code, bump only the CLI distribution from `0.12.0.dev6` to `0.12.0.dev7` and record it in the root `CHANGELOG.md`. The library version remains unchanged unless evidence shows a library defect.

Add offline `unittest` cases in the CLI orchestration suite, using local Git remotes and extending `git_scaffold.py` only as needed:
1. A deeply nested `subrepos` file that is already available in a managed repository is found and its entries are processed at paths relative to that file.
2. An existing parent checkout is updated from a local remote that adds or changes its nested `subrepos`; newly declared repositories are detected, queued, and processed in the same `--run`.
3. If needed to prove recursive discovery, an intermediate repository update exposes another deeper config and its declared repository is then processed.
4. A local Git fixture declares a non-dot relative path that normalizes to the currently managed repository's worktree root; `--run` performs the self-update successfully. This verifies self-target behavior by resolved path rather than by a particular spelling.

Do not add general cycle, branch-oscillation, error-model, or path-validation tests as part of this stage. The self-target test is solely a preservation check, not authorization for broader loop handling. Run the focused orchestration tests and establish that failures are the expected red results, not fixture or environment errors. When the red-test criteria are complete, change this stage's status to `Waiting for user review`, present the evidence, and stop. After positive review, mark Stage 1 `Finished` and wait for an explicit instruction before starting Stage 2.

<sub>[back to top](plan-multigitRecursiveSubreposDev7Stage.prompt.md).</sub>

## Stage 2: Focused Implementation
**Status:** Not started; requires Stage 1 to be marked `Finished` and an explicit instruction to begin.

If post-update discovery passes the new tests, do not add redundant polling or reprocessing. If a targeted test fails, fix only the discovery or queueing behavior needed to make that test pass, preserving FIFO/declaration order, streaming results, YAML semantics, existing error behavior, and the tested self-target behavior based on the normalized worktree path. Do not add general cycle handling, path restrictions, other self-update changes, or exit-code redesign. If an unrelated loop or side-effect issue becomes apparent, capture the reproducing evidence and stop for explicit direction rather than expanding the fix.

Run the focused tests to green and report the change and evidence. When the implementation criteria are complete, change this stage's status to `Waiting for user review` and stop. After positive review, mark Stage 2 `Finished` and wait for an explicit instruction before starting Stage 3.

<sub>[back to top](plan-multigitRecursiveSubreposDev7Stage.prompt.md).</sub>

## Stage 3: Acceptance and Closeout
**Status:** Not started; requires Stage 2 to be marked `Finished` and an explicit instruction to begin.

1. Run the focused orchestration tests and `make -C cli test`; keep tests offline.
2. Run root `make test` if the focused change passes, to verify the split repository's required test gate.
3. Run the relevant CLI acceptance checks for recursive `--run` behavior. Broader build/docs checks are needed only if the change affects those deliverables.
4. Confirm the test suite's `cli/tests/scenarios` cleanup target is absent or disposable before running, because test teardown recursively removes it.
5. Report the behavior proven, any minimal fix, and incidental findings separately. Do not publish either distribution. When acceptance is complete, change this stage's status to `Waiting for user review` and stop. After positive review, mark Stage 3 `Finished` and stop the Dev7 stage.

<sub>[back to top](plan-multigitRecursiveSubreposDev7Stage.prompt.md).</sub>

## Decisions and Invariants
- The documented contract is authoritative; matching historical v0.11.9 implementation details is not a goal.
- The stage's acceptance criteria concern discovery and queueing of deeper/newly exposed configs, not exactly-once processing or termination for cyclic declarations.
- Self-update is a known required behavior whenever the normalized target resolves to the current worktree root; cover and preserve it regardless of the declaration's spelling. This does not broaden the stage into general cycle/oscillation handling.
- Do not prohibit self-mounting, impose path-direction rules, or add cycle handling in this stage.
- CLI owns parsing and traversal; library ownership and API remain unchanged.
- Preserve existing error and exit-code behavior; this stage does not define a future global-versus-local error taxonomy.
- Development versioning is CLI-only (`0.12.0.dev7`); no package publication is part of this stage.
- User review and explicit start instructions are separate gates: a positive review finishes the current stage but does not itself authorize starting the next one.

<sub>[back to top](plan-multigitRecursiveSubreposDev7Stage.prompt.md).</sub>
