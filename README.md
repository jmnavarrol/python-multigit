# Python Multigit<a name="top"></a>

A Python version of the [multigit Bash script](https://github.com/jmnavarrol/simplest-git-subrepos).

While the multigit Bash script at [simplest-git-subrepos](https://github.com/jmnavarrol/simplest-git-subrepos) was created for illustration purposes, this one is intended to be a full-fledged implementation.

The general idea is to offer a simple way of managing *"workspaces"* integrating multiple git repos starting from a top one, and without the need of difficult *"arcanes"* like *git submodules*, *git-subtree*, etc.: you only need to declare your intended *layout* in a YAML file, and let this script (**multigit**) do its job.  See the [simplest-git-subrepos README](https://github.com/jmnavarrol/simplest-git-subrepos#readme) for a long-wired explanation.

**Contents:**<a name="contents"></a>
1. [usage](#usage)
1. [development](#development)
   1. [build](#build)
   1. [publish](#publish)
1. [license](#license)

----

## usage<a name="usage"></a>
This project [is published to the PyPI index](https://pypi.org/project/multigit/) so, in order to install it you just need to run `pip install multigit`.

*multigit* expects a YAML file named **subrepos** on the *root directory* of the current git repo (see [example](./subrepos)).  Optionally, if the current directory is not within a git sandbox, it will try to find a *subrepos* file right there.

For each defined *subrepo* within the *subrepos* file, it will clone/checkout it to the defined relative path.  Optionally, it will *checkout* the given *gitref* (either *commit*, *branch* or *tag*), provided the repo's local sandbox is *"clean"* (i.e. no pending modifications).  
  **NOTE:** pay attention to the fact that if the *gitref* you record is a specific *commit* or *tag*, the related sandbox will be in disconnected state.

*multigit* will also recursively look for new *subrepos* files on the repositories it manages.

**You should make sure** your [*.gitignore* file](./.gitignore) ignores all your *subrepos*.

This way you just need to manage your repos with `git` in the standard way, just as if they were individually checked out in isolation.

<sub>[back to top](#top).</sub>

## development<a name="development"></a>
This project uses the help of [Bash Magic Enviro](https://github.com/jmnavarrol/bash-magic-enviro) to configure its development environment.

It creates a Python 3 *virtualenv* using [the companion requirements file](./python-virtualenvs/multigit-development.requirements).

Once the *virtualenv* is (automatically) activated, you can run this code just invoking its main script, i.e.: `multigit`.

<sub>[back to top](#top).</sub>

### build<a name="build"></a>
The [included Makefile](./src/Makefile) will use Python's setup tools to build both *source* and *binary-based* Python *eggs*.  Provided everthing went OK, look for packages under the *dist/* directory.

Run `make` to see available *make targets*.

<sub>[back to top](#top).</sub>

### publish<a name="publish"></a>
Provided *Makefile* includes publication targets to both testing and live PyPi services by means of *twine*.  Make sure your ~/.pypi.rc file includes proper entries named *[testpypi]* and *[pypi]* respectively.  Remember, also, that you can't publish the same version twice to these services, so make sure you udpate the package's version before attempting an upload.

<sub>[back to top](#top).</sub>

------

## License<a name="license"></a>
Python Multigit is made available under the terms of the **GPLv3**.

See the [license file](./LICENSE) that accompanies this distribution for the full text of the license.

<sub>[back to top](#top).</sub>
