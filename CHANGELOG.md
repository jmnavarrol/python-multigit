# CHANGELOG

## Next Release
* Differences from [previous tag](/../../compare/v0.11.8…main).
* Build system refactored so it's hatch-only now.
* Subrepofile class doesn't print to STDOUT anymore; it rises exceptions instead.

## 0.11.8 (2024-MAY-25)
* Differences from [previous tag](/../../compare/v0.11.7…main).
* **BUGS:**
  * [#13](/../../issues/13): multigit properly checks out commits.

## 0.11.7 (2024-MAY-24)
* Differences from [previous tag](/../../compare/v0.11.6…main).
* Code and metadata refactoring for an easier *"libraryzing"* in the future.
  * Subrepos file's default name is now defined at main() so it can be overwritten when using this code in library mode.
* Refactoring so Makefile, pyproject.toml are at the repository's root.
* Tests refactored so they go into subdirectories by "main" feature.
* Makefile: added 'date' target (shows date in CHANGELOG-compatible format).
* Sphinx docs: GitHub action refactored so documentation is only published on tags.
* Added the ability to process the "root" repository without enter an infinite loop.

## 0.11.6 (2024-MAR-10)
* Differences from [previous tag](/../../compare/v0.11.5…v0.11.6).
* [#11](/../../issues/11) BUG CORRECTED: multigit tracks commit instead of branch.
* All build config moved to [pyproject.toml](./src/pyproject.toml)
* Build system moved from setuptools to hatchling.
* Dependencies fully relaxed (no versions defined).
* Preliminary support for a demonstration/development docker container.

## 0.11.5 (2023-OCT-21)
* Differences from [previous tag](/../../compare/v0.11.4-2…v0.11.5).
* Found the way for KDevelop to show '.github' dir on project view.
* BME files added to .gitattributes (as BASH type).
* setup.py deleted as it's needed no more along setuptools.
* setup.cfg declared UTF-8.
* Development dependencies relaxed.
* [#9](https://github.com/jmnavarrol/python-multigit/issues/9) BUG CORRECTED: uncontrolled error when requested a branch which exists locally but not on remote.

## 0.11.4-2
* A github action now [publishes Sphinx-based code documentation to GitHub Pages](https://jmnavarrol.github.io/python-multigit/).
* Build environment refactoring to support this new feature.

## 0.11.4-1
* [#8](https://github.com/jmnavarrol/python-multigit/issues/8): [setup.cfg](./src/setup.cfg) updated so it can manage different dependencies depending on running Python version.
