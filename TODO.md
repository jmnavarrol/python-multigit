# TO-DO
Pending actions, general notes, etc. (in no particular order):
* Refactor code related to presentation/logging.
* Find the way to self-document the python dictionary that represents subrepos for easier reuse.
* Find the way for Sphinx to offer a drop-down to select git tag-tied versions of documentation.
  * https://www.codingwiththomas.com/blog/my-sphinx-best-practice-for-a-multiversion-documentation-in-different-languages
* [#10](../../issues/10): Review [vag](https://github.com/charlyoleg2/vag) and [vcstool](https://github.com/dirk-thomas/vcstool) for inspiration.
* Find the way to simplify subrepos' format allowing for *gitref* instead of *branch|tag|commit* (the code should find what kind of object *gitref* references).
* Add a `--check-version` option (or something like that) that looks for updates.

## IN PROGRESS
* Refactor multigit so it can be used in library mode by other applications.
