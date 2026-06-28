# CHANGELOG

## Next Release
* Differences from [0.0.2.dev1 publication commit](/../../compare/8d53bf5c0e9303841a6e514ee5291d6452f92338...splitting-plan).

## Next Release
* Differences from [0.0.1.dev1 publication commit](/../../compare/8d53bf5c0e9303841a6e514ee5291d6452f92338...8d53bf5c0e9303841a6e514ee5291d6452f92338).
* Library functional parity with legacy behavior is now achieved for the stage scope, including representative status/update/error scenarios validated by copied ownership tests plus explicit legacy-vs-lib parity tests.
* Release-readiness gates are green in `lib`: expanded offline tests (including parity suite), documentation build, packaging build, and clean local artifact install validation.
* Migration-start declaration gate is closed: root legacy test lane still passes unchanged, and legacy trees under `src/multigit` and `src/tests` remain intact.
* TestPyPI publication bundle/checklist for `0.0.1.dev2` is prepared in `lib/docs/testpypi_release_checklist_dev2.rst`.

## 0.0.1.dev1 (2026-JUN-27)
* Publication reference commit: [8d53bf5c0e93](/../../commit/8d53bf5c0e9303841a6e514ee5291d6452f92338) (tip of `splitting-plan` at publication time).
* Initial pre-release PoC track published to TestPyPI for the future library split.
* Transitional import package name is `multigit_lib` to avoid collision with the current `multigit` runtime package.
* Minimal `multigit-lib` PoC scaffold added under `lib/`.
* Packaging metadata uses hatchling with version sourced from `src/multigit_lib/__init__.py`.
* Offline unittest smoke checks added for import and version validation.
* Component-local Sphinx docs and recursive Makefile doc target added.
* Build and doc/test workflows validated locally.
* Isolated installability checks confirmed no `multigit` shell command is exposed by the library package.
* Coexistence checks confirmed `multigit_lib` does not shadow the production `multigit` package.
* Clean virtualenv install smoke validation from TestPyPI confirmed import and `__version__ = 0.0.1.dev1`.
* No business logic has been migrated from `src/multigit` in this milestone yet.
