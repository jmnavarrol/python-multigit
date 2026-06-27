## Plan: Minimal Library PoC 0.0.1.dev1

Create a very small, non-functional library-only PoC release track to validate filesystem layout, packaging, tests, docs, and publish flow to TestPyPI without moving or refactoring existing production code paths.

**Steps**
1. Phase 0: Guardrails and scope lock
2. Confirm this PoC does not modify or relocate existing runtime implementation under src/multigit and does not reuse the same Python import namespace.
3. Use multigit_lib as the import package name throughout this PoC. This is the transitional name required to avoid shadowing the currently installed multigit namespace while the library is developed in parallel. The rename to multigit is deferred until the rename gate defined in the design doc (offline parity achieved, CLI migration started, legacy src/multigit retired).
4. Treat this milestone as packaging/process validation only, including installability and runtime coexistence checks (not feature completeness). Runtime coexistence checks (isolated venv, import shadowing) are explicitly in scope as they validate packaging correctness, not feature parity.
5. Phase 1: Create isolated library PoC skeleton
6. Add a new library workspace subtree (lib/) with minimal package structure:
7. lib/pyproject.toml with project.name = multigit-lib and project.version = 0.0.1.dev1.
8. lib/src/multigit_lib/ with exactly one module: lib/src/multigit_lib/__init__.py exposing only __version__ = "0.0.1.dev1".
9. lib/tests/ with basic unittest-based smoke tests (import and version assertions), fully offline.
10. lib/docs/ with minimal Sphinx setup: conf.py with extensions = ["sphinx.ext.autodoc"], docs/index.rst with a toctree and at least one automodule:: multigit_lib directive, and a docs/Makefile so that make -C lib doc invokes sphinx-build -b html and exits 0.
11. lib/Makefile with minimal targets: test, build, doc, upload-tmp, clean.
12. Phase 2: Packaging and release process PoC
13. Build sdist/wheel for lib only.
14. Validate artifact installability in isolated venv, verify no multigit shell command is installed by the library package, and confirm coexistence with production multigit without import shadowing or breakage.
15. Publish 0.0.1.dev1 to TestPyPI from lib workflow.
16. Validate TestPyPI install of multigit-lib==0.0.1.dev1.
17. Phase 3: Minimal integration alignment (no code migration)
18. Keep root and current CLI behavior unchanged.
19. Add a clearly marked WARNING block to the root README.md under a new ## PoC Incubation heading, stating that lib/ is a packaging PoC and not the production runtime source.
20. Append an ## Outcome and Known Gaps section to lib/docs/index.rst (or a new lib/CHANGELOG.md) documenting what was validated and any unresolved issues before proceeding to the next migration phase.

**Relevant files**
- /Users/e047072/PERSONAL/IDE/projects/python/python-multigit/src/multigit - must remain unchanged in this PoC step.
- /Users/e047072/PERSONAL/IDE/projects/python/python-multigit/AGENTS.md - keep hatchling and offline unittest conventions.
- /Users/e047072/PERSONAL/IDE/projects/python/python-multigit/lib/pyproject.toml - new PoC package metadata and version 0.0.1.dev1.
- /Users/e047072/PERSONAL/IDE/projects/python/python-multigit/lib/Makefile - new component-level test/build/doc/upload orchestration.
- /Users/e047072/PERSONAL/IDE/projects/python/python-multigit/lib/src/multigit_lib/__init__.py - minimal import surface for PoC artifact.
- /Users/e047072/PERSONAL/IDE/projects/python/python-multigit/lib/tests/ - offline unittest smoke checks for package import and version.
- /Users/e047072/PERSONAL/IDE/projects/python/python-multigit/lib/docs/ - minimal Sphinx stack proving doc build flow.

**Verification**

Phase A — local, offline:
1. make -C lib test passes offline.
2. make -C lib build produces sdist and wheel.
3. make -C lib doc builds Sphinx output successfully.
8. Existing root make test for current project remains unaffected.

Phase B — isolated venv, no network required (steps 4–5 require a fresh venv):
4. Installing the built lib artifact does not install or expose the multigit command.
5. Installing the lib artifact alongside production multigit does not shadow or break imports of production multigit.

Phase C — network, TestPyPI credentials required (steps 6–7 require TWINE_USERNAME and TWINE_PASSWORD):
6. make -C lib upload-tmp publishes 0.0.1.dev1 to TestPyPI successfully. The upload-tmp Makefile target must use twine upload --repository testpypi. Document in lib/Makefile or lib/README that TWINE_USERNAME and TWINE_PASSWORD (or a [testpypi] entry in ~/.pypirc) must be set before invoking this target. The upload-tmp target must include a Makefile guard: check that TWINE_USERNAME and TWINE_PASSWORD are non-empty shell variables and, if not, print "Error: TWINE_USERNAME and TWINE_PASSWORD must be set before running upload-tmp" and exit 1 before invoking twine.
7. Fresh install from TestPyPI resolves and imports multigit-lib==0.0.1.dev1.

**Decisions**
- Included: a strictly minimal, hello-world-like library package to validate pipeline and structure.
- Included: unittest and hatchling continuity.
- Included: no filesystem moves from existing src/multigit path.
- Included: transitional import package name multigit_lib (not multigit) to avoid collision with the currently published multigit package; rename to multigit is deferred to the rename gate in the design doc.
- Excluded: business-logic extraction into lib in this first milestone.
- Excluded: CLI migration to consume lib in this first milestone.
- Excluded: final cmd/lib boundary purity in this first milestone.

**Further Considerations**
1. Versioning note: this PoC uses 0.0.1.dev1 intentionally as a pre-release process checkpoint before any stable compatibility-drop-in release.
2. Dependency note: CLI dependency constraints should remain unchanged until a later migration milestone actually consumes published lib.
3. Tagging note: Create a Git tag named v0.0.1.dev1 on the commit that produced the published artifact, immediately after successful TestPyPI publication, using: git tag v0.0.1.dev1 && git push origin v0.0.1.dev1.
