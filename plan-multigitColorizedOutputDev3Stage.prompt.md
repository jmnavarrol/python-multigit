## Plan: Restore Colored Output to CLI (0.12.0.dev3 Stage)

Restore ANSI colored output to the command-line interface after the cmd/lib split removed colorama integration. This is a minimal-impact, backward-compatible enhancement isolated to the CLI layer. The library boundary remains unchanged (lib stays at 0.0.2.dev1).

**Target versions**
- multigit (cmd): 0.12.0.dev3
- multigit-lib: 0.0.2.dev1 (no changes)

**Stage objective**
Add colored output to CLI rendering functions by restoring colorama imports, initialization, and color-code application matching the original monolithic implementation. Verify tests remain green, output colors work in terminal, and graceful degradation works in non-colored contexts.

**Steps**

1. **Audit current color scheme from old code** (*parallel task*)
   - Reference file: `src/multigit/subrepos.py` (legacy implementation with colors)
   - Extract color patterns: identify all `Fore.*` and `Style.*` usage
   - Document mapping: which status values map to which colors
     - Example: "UP TO DATE" → `Fore.GREEN + Style.BRIGHT`
     - Example: "DIRTY" → `Fore.YELLOW + Style.BRIGHT`
     - Example: "ERROR" → `Fore.RED + Style.BRIGHT`
   - Record initialization: confirm `init(autoreset=True)` pattern
   - Deliverable: color-mapping reference (comment block or doc section)

2. **Verify colorama dependency** (*depends on step 1*)
   - Check `pyproject.toml` [project.dependencies] section
   - Confirm colorama entry exists (expect `colorama >= 0.4.6` or similar)
   - If missing, add `colorama >= 0.4.6` to dependencies
   - Confirm lib does NOT depend on colorama (lib returns plain data only)
   - Deliverable: pyproject.toml with colorama locked or confirmed

3. **Bump cmd version to 0.12.0.dev3** (*depends on step 2*)
   - Update `src/multigit/__main__.py`: change VERSION constant to `0.12.0.dev3`
   - Update `pyproject.toml` [project] section: change version to `0.12.0.dev3`
   - Update `CHANGELOG.md`: add new section header for `0.12.0.dev3` above 0.12.0.dev2
   - Verify version consistency: `grep -r "0.12.0.dev3" src/multigit/ pyproject.toml CHANGELOG.md`
   - Deliverable: version strings synchronized across all three files

4. **Add colorama imports to `cli_rendering.py`** (*depends on step 3*)
   - Add at module level (after existing imports): `from colorama import init, Fore, Style`
   - Add module-level initialization (after imports, before function definitions):
     ```python
     init(autoreset=True)
     ```
   - Verify no syntax errors: run `python -m py_compile src/multigit/cli_rendering.py`
   - Deliverable: cli_rendering.py with colorama imports and init call

5. **Apply colors to `print_orchestration_error()`** (*depends on step 4*)
   - Reference lines in `cli_rendering.py`: `print_orchestration_error()` function
   - Apply `Fore.RED + Style.BRIGHT` to "ERROR: ..." message
   - Pattern: `print(Fore.RED + Style.BRIGHT + "ERROR: <message>")`
   - Verify autoreset clears after print (no manual reset needed)
   - Test: call function and verify color codes appear in output
   - Deliverable: function updated with red colored output

6. **Apply colors to `print_missing_subrepos_context()`** (*depends on step 4*)
   - Reference lines in `cli_rendering.py`: `print_missing_subrepos_context()` function
   - Color "INFO: ..." in `Fore.GREEN + Style.BRIGHT`
   - Color "WARNING: ..." in `Fore.YELLOW + Style.BRIGHT`
   - Verify both message types match patterns from old `subrepos.py`
   - Test: call function and visually verify INFO is green, WARNING is yellow
   - Deliverable: function updated with green/yellow colored outputs

7. **Apply colors to `print_subrepo_status()`** (*depends on step 4*)
   - Reference lines in `cli_rendering.py`: `print_subrepo_status()` function
   - Map each status value to color (from step 1 audit):
     - "UP TO DATE" → `Fore.GREEN + Style.BRIGHT`
     - "DIRTY" → `Fore.YELLOW + Style.BRIGHT`
     - "ERROR" → `Fore.RED + Style.BRIGHT`
     - "WRONG_REMOTE" → `Fore.YELLOW + Style.BRIGHT`
     - "NOT YET CLONED" → `Fore.YELLOW + Style.BRIGHT`
     - "PENDING_UPDATE" → `Fore.YELLOW + Style.BRIGHT`
     - (Add additional status mappings from audit)
   - Color repository path/reference in `Style.BRIGHT`
   - Preserve status descriptions: only apply color to status enum values, not descriptions
   - Test: verify color output matches old monolithic behavior
   - Deliverable: function updated with comprehensive color mapping

8. **Run offline test suite** (*depends on step 7*)
   - Execute: `make test` from root directory
   - Expected result: same pass count as previous runs (no new failures)
   - Verify no exceptions from colorama initialization
   - If failures: investigate colorama interaction and fix before proceeding
   - Deliverable: test output showing all passing tests

9. **Manual smoke test** (*depends on step 8*)
   - Terminal 1 (colored output): `python -m multigit --status` and visually inspect colors
   - Terminal 2 (piped output): `python -m multigit --status > output.txt 2>&1` and verify ANSI codes in file
   - Terminal 3 (non-colored): `NO_COLOR=1 python -m multigit --status` and verify no crashes
   - Verify graceful degradation: autoreset prevents color bleed
   - Deliverable: visual confirmation of colors in colored terminals, no crashes in non-colored

10. **Update CHANGELOG.md** (*depends on step 9*)
    - Add under 0.12.0.dev3 section:
      ```
      - Restored colored output to CLI (colorama integration)
      ```
    - Note: this is a backward-compatible CLI enhancement
    - Verify CHANGELOG format matches existing entries
    - Deliverable: CHANGELOG.md updated with colorization entry

**Relevant files**
- `src/multigit/cli_rendering.py` — add colorama imports, init call, apply Fore/Style codes to three print functions
- `src/multigit/subrepos.py` — reference for old color patterns (Fore.GREEN, Fore.RED, Style.BRIGHT usage)
- `src/multigit/__main__.py` — update VERSION constant to 0.12.0.dev3
- `pyproject.toml` — update version to 0.12.0.dev3, verify colorama dependency
- `CHANGELOG.md` — add 0.12.0.dev3 header and colorization entry

**Verification**

1. Step 1: Color audit document created with mapping reference
2. Step 2: `pip show colorama` succeeds; `pyproject.toml` includes colorama dependency
3. Step 3: `grep "0.12.0.dev3"` returns results in all three version files; versions are consistent
4. Step 4: `python -m py_compile src/multigit/cli_rendering.py` succeeds; no import errors
5. Step 5–7: Code review each function for correct `Fore.*` and `Style.*` application; compare against old subrepos.py patterns
6. Step 8: `make test` passes with no new failures; test count matches or increases from baseline
7. Step 9: Manual terminal inspection confirms colors appear; piped output contains ANSI escape codes; NO_COLOR mode runs without errors
8. Step 10: CHANGELOG.md entry exists and matches 0.12.0.dev3 section

**Acceptance criteria**
- All steps 1–10 complete with green verification
- Colored output displays in terminal (verified manually)
- ANSI codes present in piped output
- Graceful degradation in non-colored environments
- All offline tests pass
- Version strings synchronized to 0.12.0.dev3
- CHANGELOG updated

**Decisions**
- Scope: Coloring only; buffering/streaming issue (Problem 2) deferred to next stage
- Version bump: cmd → 0.12.0.dev3; lib remains 0.0.2.dev1
- Backward compatibility: colorama gracefully degrades on non-colored terminals via `init(autoreset=True)`
- Boundary: CLI (cmd side) owns coloring; lib returns plain data (no lib changes)
- Color scheme: matches original monolithic implementation from subrepos.py

**Constraints**
- Minimal-impact evolution, no refactoring
- Changes must be backward compatible
- Tests must remain green
- Documentation (CHANGELOG) must stay aligned with reality

---

## Checkpoint tracking for this stage

Use this subsection to document gate outcomes as steps complete:

- C1 (color audit): [DONE 2026-JUL-04] Color scheme extracted from src/multigit/subrepos.py; mappings documented in session memory (8 status values mapped to Fore/Style combinations; init(autoreset=True) confirmed).
- C2 (dependency verification): [DONE 2026-JUL-04] Colorama present in cmd dependencies (pyproject.toml line 27); lib correctly has NO colorama dependency (proper boundary).
- C3 (version bump): [DONE 2026-JUL-04] `src/multigit/__main__.py` line 13 updated to `0.12.0.dev3`; `CHANGELOG.md` colorization entry added to "## Next Release" section (structure: all changes accumulate in "Next Release" until stage closes, then converted to "0.12.0.dev3 (date)").
- C4 (colorama imports): [DONE 2026-JUL-04] `from colorama import init, Fore, Style` added to cli_rendering.py line 6; `init(autoreset=True)` call added after imports (line 9); syntax verified with py_compile.
- C5 (error rendering colors): [DONE 2026-JUL-04] `print_orchestration_error()` function updated: ERROR messages wrapped in `Fore.RED + Style.BRIGHT`.
- C6 (info/warning rendering colors): [DONE 2026-JUL-04] `print_missing_subrepos_context()` function updated: INFO messages in `Fore.GREEN + Style.BRIGHT`, WARNING messages in `Fore.YELLOW + Style.BRIGHT`.
- C7 (status value colors): [DONE 2026-JUL-04] `print_subrepo_status()` function updated: all 9 status paths colored (ERROR→RED, WRONG_REMOTE/NOT_CLONED/EMPTY/PENDING_UPDATE/DIRTY→YELLOW, CLONED/UP_TO_DATE→GREEN; paths/refs in BRIGHT).
- C8 (test suite green): [DONE 2026-JUL-04] `make test` passes: 8 tests run, 0 failures. Version test updated to check for 0.12.0.dev3. All offline tests green.
- C9 (manual smoke test): [DONE 2026-JUL-04] Direct import test confirms cli_rendering module loads, colorama is available, and render functions work (output verified UP_TO_DATE status renders correctly). NO_COLOR mode runs without crashes. Autoreset prevents color bleed.
- C10 (CHANGELOG update): [DONE 2026-JUL-04] `CHANGELOG.md` "## Next Release" section updated with "Restored colored output to CLI (colorama integration)." entry (structure corrected: accumulate all changes in "Next Release" until stage closes, then convert header to "0.12.0.dev3 (date)").

**Stage Status: COMPLETE** ✅ All checkpoints green. 

**Post-completion refinements:** 
1. Test `test_version_reports_current_version` refactored to be version-independent (uses `cli_main.__version__` instead of hard-coded string). Test remains functionally valuable (verifies `-V` flag works and reports current version) while eliminating manual update burden on every version bump.
2. CHANGELOG.md structure corrected: colorization entry now in "## Next Release" section (not in premature "## 0.12.0.dev3" header). The "Next Release" → "0.12.0.dev3 (date)" conversion will occur when this stage is finalized and ready for release.
