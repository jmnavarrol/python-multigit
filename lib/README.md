# multigit-lib PoC<a name="top"></a>

Minimal packaging PoC for the future reusable library split of python-multigit.

This component currently exists to validate package layout, local build/test/doc workflows, and installability without changing the production runtime under `src/multigit`.

**Contents:**<a name="contents"></a>
1. [usage](#usage)
1. [development](#development)
	1. [build](#build)
	1. [tests](#tests)
	1. [code documentation](#sphinx)
	1. [publish](#publish)
	1. [CHANGELOG](./CHANGELOG.md)

----

## usage<a name="usage"></a>
This PoC package is not intended yet as the production runtime implementation of `python-multigit`.

The transitional import package name is `multigit_lib`, intentionally separated from `multigit` so the PoC can coexist with the current production package without import shadowing.

<sub>[back to top](#top).</sub>

## development<a name="development"></a>
Development at this stage is focused on validating component-local packaging, tests, documentation, and installability for a future `multigit-lib` release line.

<sub>[back to top](#top).</sub>

### build<a name="build"></a>
The [included Makefile](./Makefile) builds source and wheel artifacts for the PoC package through Hatch/Hatchling.

Run `make` to see the available component targets.

<sub>[back to top](#top).</sub>

### tests<a name="tests"></a>
The current test scope is intentionally minimal and offline-only, focused on smoke validation for package import and version exposure.

<sub>[back to top](#top).</sub>

### code documentation<a name="sphinx"></a>
Code documentation is produced with [Sphinx](https://www.sphinx-doc.org) from the component-local [docs/](./docs/) tree.

Generated HTML documentation is written under `build/sphinx-doc/html/`.

<sub>[back to top](#top).</sub>

### publish<a name="publish"></a>
The current TestPyPI publication is `multigit-lib==0.0.2.dev2`.

Published package page: https://test.pypi.org/project/multigit-lib/0.0.2.dev2/

For future uploads (new versions only), configure a `[testpypi]` entry in `~/.pypirc` with the credentials to be used by `twine upload --repository testpypi`, then run `make upload-tmp`.

<sub>[back to top](#top).</sub>
