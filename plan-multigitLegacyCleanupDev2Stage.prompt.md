## Plan: multigit legacy cleanup + duplicate removal (0.12.0.dev2 stage)

Execute the post-C10 milestone on development branches, targeting multigit version 0.12.0.dev2. The stage is approval-gated, releaseability-first, and ends with removal of legacy/cmd-side code already validated in multigit-lib. After final parity cross-check, legacy-side unit tests must focus on command-line validation only.

After each completed checkpoint, update:
1. python-multigit-diseno-final.md in Current Refactoring Status.
2. This stage checkpoint subsection.

**Steps**
1. Phase 0 - Scope and gate lock.
2. G0 entry criteria: stage start, before any code edits.
3. G0 actions: lock objective (extract remaining command-line-only concerns and remove duplicated lib-owned legacy/cmd code by stage end), lock target version (multigit 0.12.0.dev2), lock control model (explicit human approval per main phase), and lock failure policy (one remediation pass per failing gate; if still failing, record blocker in handoff and stop).
4. G0 acceptance criteria: objective, version, control model, and failure policy are explicitly documented before edits.
5. G0 checkpoint tracker: update Stage checkpoint subsection entry for G0 with status and evidence.

6. Phase 1 - Early version alignment.
7. G1 entry criteria: G0 completed.
8. G1 actions: update relevant version-bearing files to 0.12.0.dev2, verify CLI version reporting path and -V output return 0.12.0.dev2, and synchronize changelog/status references.
9. G1 acceptance criteria: version alignment is complete with no behavior drift besides expected version-string deltas.
10. G1 checkpoint tracker: update Stage checkpoint subsection entry for G1 with status and evidence.

11. Phase 2 - Baseline freeze on 0.12.0.dev2.
12. G2 entry criteria: G1 completed.
13. G2 actions: capture command signatures and exit codes for -h, -V, --status, --run; capture negative-path signatures (missing config, malformed YAML, orchestration/domain failures); replay the baseline matrix twice.
14. G2 acceptance criteria: baseline and negative signatures are stable, and both replay runs produce identical command signatures and exit codes; if the two runs differ, treat this as a gate failure and apply the failure policy before proceeding.
15. G2 checkpoint tracker: update Stage checkpoint subsection entry for G2 with status and evidence.

16. Phase 3 - Extraction slice A.
17. G3 entry criteria: G2 completed.
18. G3 actions: extract first low-risk command-only concern (rendering/message helpers) while preserving user-visible output, order, and exit mapping.
19. G3 acceptance criteria: parity vs G2 baseline passes. Parity is defined as identical exit codes for all matrix commands and identical user-visible output text for all matrix commands, excluding version-string fields updated in Phase 1; any other difference is a parity failure.
20. G3 checkpoint tracker: update Stage checkpoint subsection entry for G3 with status and evidence.

21. Phase 4 - Extraction slice B.
22. G4 entry criteria: G3 completed.
23. G4 actions: extract status/run CLI adapter glue while preserving the multigit-lib orchestration boundary and rollback capability during migration.
24. G4 acceptance criteria: parity and offline test suites (tests executable without network access, as run via `pytest -m offline`) pass with no failures, using the parity definition from G3.
25. G4 checkpoint tracker: update Stage checkpoint subsection entry for G4 with status and evidence.

26. Phase 5 - Extraction slice C.
27. G5 entry criteria: G4 completed.
28. G5 actions: extract exception-to-message/exit translation into CLI-owned path, then re-run negative-path matrix and compare with G2.
29. G5 acceptance criteria: negative-path parity passes, using the parity definition from G3.
30. G5 checkpoint tracker: update Stage checkpoint subsection entry for G5 with status and evidence.

31. Phase 6 - Final parity cross-check and ownership map.
32. G6 entry criteria: G5 completed.
33. G6 actions: execute final command/negative parity matrix, produce explicit ownership matrix (library-owned tests vs CLI-owned tests), and require human approval before removal actions. If human approval is withheld, document the requested changes, revise the ownership matrix, and re-present for approval before proceeding. This counts as a remediation pass under the failure policy.
34. G6 acceptance criteria: parity is green per G3 definition and ownership map is accepted.
35. G6 checkpoint tracker: update Stage checkpoint subsection entry for G6 with status and evidence.

36. Phase 7 - End-of-stage duplicate removal.
37. G7 entry criteria: G6 completed and ownership map approved.
38. G7 actions: remove from legacy/cmd-side only code that (a) has equivalent coverage confirmed in lib/tests/ and (b) is listed as library-owned in the ownership matrix approved at G6; keep CLI-only behavior code in CLI ownership; remove or rewrite legacy tests that duplicate library-domain assertions.
39. G7 acceptance criteria: removals are green and rollback traceability is documented.
40. G7 checkpoint tracker: update Stage checkpoint subsection entry for G7 with status and evidence.

41. Phase 8 - Legacy test-suite re-scope.
42. G8 entry criteria: G7 completed.
43. G8 actions: ensure legacy/CLI tests focus on command-line validation only (argument parsing, routing, rendering, exit codes); ensure library-domain assertions run in library test suite only; run full offline suites and lane parity checks.
44. G8 acceptance criteria: ownership split is verified.
45. G8 checkpoint tracker: update Stage checkpoint subsection entry for G8 with status and evidence.

46. Phase 9 - Closeout and handoff.
47. G9 entry criteria: G8 completed.
48. G9 actions: update status docs/changelog/evidence index, confirm final stage references remain at 0.12.0.dev2, and publish handoff packet with completed gates, blockers, rollback point, and next stage candidate.
49. G9 acceptance criteria: all gates are green and documented.
50. G9 checkpoint tracker: update Stage checkpoint subsection entry for G9 with status and evidence.

If any gate fails validation:
1. Do not proceed to next phase.
2. Document failure and evidence in checkpoint subsection.
3. Attempt one remediation pass limited to the current phase.
4. If still failing, record blocker in handoff and stop.

**Stage checkpoint subsection**
- G0 (PENDING): scope/version/gate/failure policies locked for 0.12.0.dev2 stage.
- G1 (PENDING): early version alignment completed and verified.
- G2 (PENDING): baseline/negative matrices captured and reproducible.
- G3 (PENDING): extraction slice A parity green.
- G4 (PENDING): extraction slice B parity green.
- G5 (PENDING): extraction slice C negative-path parity green.
- G6 (PENDING): final parity cross-check green + ownership map approved.
- G7 (PENDING): duplicate legacy/cmd code removed where lib-owned coverage exists.
- G8 (PENDING): legacy/CLI tests re-scoped to command-line validation only.
- G9 (PENDING): closeout synchronized, handoff packet complete.

**Relevant files**
- python-multigit-diseno-final.md - authoritative split governance/status.
- plan-multigitCliConsumesLibDev1Stage.prompt.md - checkpoint style reference.
- src/multigit/__main__.py - CLI routing/version reporting/seams.
- src/multigit/subrepos.py - legacy/mixed zone for duplicate removal.
- src/tests/ - CLI validation ownership after re-scope.
- lib/tests/ - library-domain ownership and parity proof.
- pyproject.toml - CLI metadata/dependency declarations.
- CHANGELOG.md - stage/version history sync.

**Verification**
1. Gate acceptance criteria are defined inside each G0-G9 block in Steps and are authoritative.
2. At each gate: run root offline tests plus command matrix evidence collection.
3. At G1: validate 0.12.0.dev2 alignment in metadata and runtime output.
4. At G3-G6: enforce parity definition from G3 for output and exit-code comparisons vs G2 baseline.
5. At G7-G8: verify removed legacy/cmd lib-owned code remains covered by lib tests and CLI tests assert CLI behavior only.
6. At G9: verify docs, evidence, and gate records are synchronized.

**Decisions**
- Included: staged extraction + end-of-stage duplicate removal for lib-owned logic.
- Included: legacy test-suite re-scope to CLI-only validation after final parity gate.
- Included: early version alignment to 0.12.0.dev2 before functional work.
- Excluded: production publication execution, rename gate execution, final architecture-purity refactor.
- Priority: releaseability and parity first, architecture ideal-state second.
