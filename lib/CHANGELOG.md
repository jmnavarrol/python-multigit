# CHANGELOG

## Next Release
* Initial pre-release PoC track being prepared for the future library split.
* Transitional import package name is `multigit_lib` to avoid collision with the current `multigit` runtime package.
* Minimal `multigit-lib` PoC scaffold added under `lib/`.
* Packaging metadata uses hatchling with version sourced from `src/multigit_lib/__init__.py`.
* Offline unittest smoke checks added for import and version validation.
* Component-local Sphinx docs and recursive Makefile doc target added.
* Build and doc/test workflows validated locally without publishing.
* Isolated installability checks confirmed no `multigit` shell command is exposed by the library package.
* Coexistence checks confirmed `multigit_lib` does not shadow the production `multigit` package.
* No business logic has been migrated from `src/multigit` in this milestone yet.
