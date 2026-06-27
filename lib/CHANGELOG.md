# CHANGELOG

## Next Release
* Differences from [0.0.1.dev1 publication commit](/../../compare/8d53bf5c0e9303841a6e514ee5291d6452f92338...splitting-plan).
* Changelog policy for this stage: do not add a new version section until `0.0.1.dev2` is published; record interim updates under this `Next Release` section.
* Release target for this stage is now set to `0.0.1.dev2`.
* Version source in `lib/src/multigit_lib/__init__.py` updated to `__version__ = 0.0.1.dev2`.
* Compatibility-preservation rule for copied modules is active in this stage: preserve legacy status strings, exception handling, and printing behavior unless a packaging/test-unblocking change is strictly required.
* Boundary-purity refactors are deferred for this stage; parity work proceeds copy-first without rendering-separation or exception-model redesign changes.

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
