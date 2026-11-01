# TO-DO
Pending actions, general notes, etc. (in no particular order):
* Find the way to self-document the python dictionary that represents subrepos for easier reuse.
* Find the way for Sphinx to offer a drop-down to select git tag-tied versions of documentation.
  * https://www.codingwiththomas.com/blog/my-sphinx-best-practice-for-a-multiversion-documentation-in-different-languages
* [#10](../../issues/10): Review [vag](https://github.com/charlyoleg2/vag) and [vcstool](https://github.com/dirk-thomas/vcstool) for inspiration.
* Find the way to simplify subrepos' format allowing for *gitref* instead of *branch|tag|commit* (the code should find what kind of object *gitref* references).
* Add a `--check-version` option (or something like that) that looks for updates.
* Unit tests: full review and refactoring.
* Review https://github.com/fboender/multi-git-status for ideas on what `multigit --status` could do.

## IN PROGRESS
* Review component unit tests so they verify behavior rather than historical implementation details.
  * Library review complete: status/update tests are separated, stale YAML setup and console output removed, and branch/tag/commit update cases are covered.
  * CLI review complete: shared Git fixtures are reused, workflow assertions check results, nested-file recursion and iterator ordering are covered, and historical Dev5 test naming was removed.
* Review [main Makefile](./Makefile):
  * streamline targets pointing to lib/cli ones.
  * review publish/publish-tmp targets.
* Improve GitHub Actions with component-specific test/build gates.
