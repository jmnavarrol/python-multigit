# Python Multigit<a name="top"></a>

A Python version of the [multigit Bash script](https://github.com/jmnavarrol/simplest-git-subrepos).

While the multigit Bash script at [simplest-git-subrepos](https://github.com/jmnavarrol/simplest-git-subrepos) was created for illustration purposes, this one is intended to be a full-fledged implementation.

The general idea is to offer a simple way of managing *"workspaces"* integrating multiple git repos starting from a top one, and without the need of difficult *"arcanes"* like *git submodules*, *git-subtree*, etc.: you only need to declare your intended *layout* in a YAML file, and let this script (**multigit**) do its job.  See the [simplest-git-subrepos README](https://github.com/jmnavarrol/simplest-git-subrepos#readme) for a long-wired explanation.

**Contents:**<a name="contents"></a>
1. [usage](#usage)
   * [subrepos' file format](#subrepos-file-format)
1. [development](#development)
   * [transitional package layout](#transitional-package-layout)
   * [tests](#tests)
   * [code documentation](#code-documentation)
   * [build](#build)
   * [publish](#publish)
1. [License](#license)

----

## usage<a name="usage"></a>
This project [is published to the PyPI index](https://pypi.org/project/multigit/) so, in order to install it you just need to run `pip install multigit`.

*multigit* expects a YAML file named **subrepos** in the current dir (see [example](./example/subrepos)).  Optionally, if there's no *subrepos* file in the current dir **and** the current directory is within a git sandbox, *multigit* will try to find a *subrepos* file at the git sandbox's root.

For each defined *subrepo* within the *subrepos* file, it will clone/checkout it to the defined relative path.  Optionally, it will *checkout* the given *gitref* (either *commit*, *branch* or *tag*), provided the repo's local sandbox is *"clean"* (i.e. no pending modifications).  
  **NOTE:** pay attention to the fact that if the *gitref* you record is a specific *commit* or *tag*, the related sandbox will be in disconnected state.

*multigit* will also recursively look for new *subrepos* files on the root directory of the repositories it manages.

When working within a git repository, **you should make sure** your [*.gitignore* file](./.gitignore) ignores all your *subrepos*.

This way you just need to manage your repos with `git` in the standard way, just as if they were individually checked out in isolation.

Run `multigit` with no options or `multigit --help` for usage.

<sub>[back to top](#top).</sub>

### subrepos' file format<a name="subrepos-format"></a>
The *'subrepos'* file holds a yaml dictionary describing the desired lay-out.

It starts with a **subrepos** key with a list of entries underneath, each of them describing a repository entry point (see ['subrepos' example](./example/subrepos) for further details).  Some detailed explanations follow:
* **general description:**
  ```yml
  ---
  # High-level structure
  subrepos: # main key
  - [first entry]   # first repository description
  - [second entry]  # second repository description
  - [third entry]   # third repository description
  - [...]           # (more repositories)
  ```
* **each repository entry:** Each repository definition requires two mandatory keys and an optional one:
  * **repository:** (mandatory) the [URI](https://en.wikipedia.org/wiki/Uniform_Resource_Identifier "Uniform Resource Identifier") to operate the remote repository.  
  Its format is just the one you'd use to `git clone` the repository with same effect, i.e. if you need to pass a username/password for an https site, or a password to decrypt you ssh key, etc. here you'll be requested to do it too.
  * **path:** (mandatory) the path the repository sandbox will the deployed to, relative to the subrepos file itself.
  * **[commit|branch|tag]:** (optional) the *gitref* you want your sandbox to be *pinned* to.  
    * You can provide **one** of either *'commit'*, *'branch'* or *'tag'*.
    * Note that if you provide either a *commit* or a *tag* the resulting sandbox will be in a [*detached head state*](https://git-scm.com/docs/gitglossary#Documentation/gitglossary.txt-aiddefdetachedHEADadetachedHEAD).
    * If you don't provide this key, your sandbox will track the remote's default branch.
  
**A full (conceptual) example:**
```yml
---
# Don't forget including your subrepos' roots to .gitignore!
subrepos:
- repo: 'git@github.com:jmnavarrol/python-multigit.git'  # the remote using git+ssh protocol.  It may request your ssh key's password
  path: 'a-subdir'  # it will be cloned to 'subdir/' relative to 'subrepos' file
  # no gitref, so this will track the remote's default branch
- repo: 'https://github.com/jmnavarrol/python-multigit.git'  # the remote using https protocol.  It may request user/password
  path: 'a-subdir/another-subdir'  # it will be cloned to 'a-subdir/subdir/' relative to 'subrepos' file
  branch: 'a-branch'  # the sandbox will track the 'a-branch' branch.
```

**NOTE:** Since repositories are listed in an array, order matters: first repository is processed before the second one and so on.  This means that you can declare first a repository to be deployed to a subdirectory and then another repository to be deployed to a subdirectory of that first subdirectory and things will behave as expected.  
It's usually better that you declare the *"deeper"* subdirectory within its own 'subrepos' file in the intermediate repository, though.

<sub>[back to top](#top).</sub>

## development<a name="development"></a>
This project uses the help of [Bash Magic Enviro](https://github.com/jmnavarrol/bash-magic-enviro) to configure its development environment.

It creates a Python 3 *virtualenv* using [the companion requirements file](./python-virtualenvs/multigit-development.requirements).

Once the *virtualenv* is (automatically) activated, you can run the code via the project entry points or through the package-specific local workflows.

The repository is currently in a transitional packaging split:

* the legacy root package under [src/multigit/](./src/multigit/) is still kept as compatibility and retirement coverage;
* the library package lives under [lib/](./lib/);
* the CLI package lives under [cli/](./cli/);
* the root [Makefile](./Makefile) remains available for the old workflow and also exposes the new delegated component targets.

This means the project is intentionally supporting both the historical root layout and the new split distribution layout while the migration is still in progress.

> Warning: while the repository is being migrated, the root workflow is still kept alive for compatibility, but the canonical development and release work happens in the component-specific directories under [lib](./lib/) and [cli](./cli/). The old root package remains a compatibility layer until the retirement stage is complete.

<sub>[back to top](#top).</sub>

### transitional package layout<a name="poc-incubation"></a>

The root [Makefile](./Makefile) keeps the older command set working for backwards compatibility, while the component workflows are owned by their local Makefiles:

* `cd lib && make test`, `make build`, `make doc`, `make upload-tmp`
* `cd cli && make test`, `make build`, `make doc`, `make upload-tmp`
* `make targets` at the repository root shows both the legacy commands and the delegated `lib-*` and `cli-*` targets

The root `src/` tree is not the canonical runtime surface for the split packages. It remains part of the migration bridge, compatibility layer, and retirement preparation path until the old single-package layout is fully retired.

<sub>[back to top](#top).</sub>

### tests<a name="tests"></a>
When adding or modifying tests, preserve these rules:
* keep the local development workflows runnable offline;
* prefer local scaffolding over external remotes;
* use mocks only when a condition cannot be reproduced reliably with local Git state;
* preserve the legacy root workflow while validating the library and CLI package boundaries.

Typical component-level validation is still performed directly within each package subtree.

<sub>[back to top](#top).</sub>

### code documentation<a name="sphinx"></a>
Code documentation is produced with the help of [Sphinx](https://www.sphinx-doc.org). The legacy package still has its documentation configuration under [src/sphinx/](./src/sphinx/), while the split packages keep their own local Sphinx configuration under [lib/docs/](./lib/docs/) and [cli/docs/](./cli/docs/).

The root [Makefile](./Makefile) still offers the legacy build route, and the component directories expose their own documentation targets, which are the preferred entry points for the split phase.

You can browse the public project documentation online at https://jmnavarrol.github.io/python-multigit.

<sub>[back to top](#top).</sub>

### build<a name="build"></a>
The project currently supports both the historical root build flow and the split package flow:

* root flow: `make targets`, `make test`, `make build`, `make doc`, `make clean`
* library flow: `cd lib && make test`, `make build`, `make doc`, `make upload-tmp`
* CLI flow: `cd cli && make test`, `make build`, `make doc`, `make upload-tmp`

The accepted packaging backend for both package splits is [Hatchling](https://hatch.pypa.io), and the build frontend is invoked through the component Makefiles rather than assuming the old root package is still the only canonical source tree.

<sub>[back to top](#top).</sub>

### publish<a name="publish"></a>
The component Makefiles provide TestPyPI upload targets through *twine*. Production PyPI upload targets are intentionally commented out during this transitional phase; do not re-enable them until the full design scope and split-completion gates are satisfied. The root Makefile does not orchestrate publishing.

Configure the `[testpypi]` entry in `~/.pypirc` before uploading a development release. A published version cannot be uploaded again, so bump the relevant component version before its next upload.

<sub>[back to top](#top).</sub>

------

## License<a name="license"></a>
Python Multigit is made available under the terms of the **GPLv3**.

See the [license file](./LICENSE) that accompanies this distribution for the full text of the license.

<sub>[back to top](#top).</sub>
