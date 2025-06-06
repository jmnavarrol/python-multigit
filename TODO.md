# TO-DO
Pending actions, general notes, etc. (in no particular order):
* Find the way to self-document the python dictionary that represents subrepos for easier reuse.
* Find the way for Sphinx to offer a drop-down to select git tag-tied versions of documentation.
  * https://www.codingwiththomas.com/blog/my-sphinx-best-practice-for-a-multiversion-documentation-in-different-languages
* [#10](../../issues/10): Review [vag](https://github.com/charlyoleg2/vag) and [vcstool](https://github.com/dirk-thomas/vcstool) for inspiration.
* Find the way to simplify subrepos' format allowing for *gitref* instead of *branch|tag|commit* (the code should find what kind of object *gitref* references).
* Add a `--check-version` option (or something like that) that looks for updates.
* Unit tests: full review and refactoring.
* Refactor multigit into library plus cmd in different package distributions:
  * Review https://github.com/effigies/hatch-monorepo for a single repo / multiple packages example.
  * https://packaging.python.org/en/latest/guides/packaging-namespace-packages/
* Review https://github.com/fboender/multi-git-status for ideas on what `multigit --status` could do.

## IN PROGRESS
* Refactoring multigit so it can be used in library mode by other applications.
  * Refactoring code related to presentation/logging.
