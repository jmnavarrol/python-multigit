# multigit-lib<a name="top"></a>

Reusable library component for python-multigit. It owns per-repository Git status and update operations over normalized native configuration objects.

The current development version is `multigit-lib==0.0.2.dev4`. The repository root provides shared guidance and recursive build, test, documentation, and cleanup orchestration. This component owns the library source, tests, documentation, and packaging for `multigit-lib`.

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
Install `multigit-lib` to use the library independently of the CLI distribution.

The Python import package is `multigit_lib`. The CLI distribution depends on `multigit-lib` through its installed package interface and owns subrepos file discovery, YAML parsing, validation, and recursive traversal. The library accepts normalized native repository configuration and performs per-repository Git operations.

<sub>[back to top](#top).</sub>

## development<a name="development"></a>
Library source, offline tests, documentation, and packaging are maintained in this component. The root Makefile delegates test, build, documentation, and clean operations to both components. The BME-managed development environment is defined by the repository's `python-virtualenvs/multigit-development.requirements`.

<sub>[back to top](#top).</sub>

### build<a name="build"></a>
The [included Makefile](./Makefile) builds the `multigit-lib` sdist and wheel through Hatchling after the test and documentation gates.

Run `make -C lib test`, `make -C lib doc`, or `make -C lib build` from the repository root. The root `make build` builds both CLI and library distributions.

<sub>[back to top](#top).</sub>

### tests<a name="tests"></a>
The offline unittest suite covers per-repository status/update behavior, package imports, and version exposure. Git scenarios use local fixtures and do not require network access; config-file and recursive CLI workflows are tested under `cli/tests/`.

<sub>[back to top](#top).</sub>

### code documentation<a name="sphinx"></a>
Code documentation is produced with [Sphinx](https://www.sphinx-doc.org) from the component-local [docs/](./docs/) tree.

Component HTML is written under `lib/build/sphinx-doc/html/`. The root docs workflow assembles the CLI site at the Pages root and the library site under `/lib/`.

<sub>[back to top](#top).</sub>

### publish<a name="publish"></a>
The latest published TestPyPI version is `multigit-lib==0.0.2.dev4`.

Published package page: https://test.pypi.org/project/multigit-lib/0.0.2.dev4/

For future uploads (new versions only), configure a `[testpypi]` entry in `~/.pypirc` with the credentials to be used by `twine upload --repository testpypi`, then run `make upload-tmp`.

<sub>[back to top](#top).</sub>
