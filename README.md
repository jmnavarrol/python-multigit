# Python Multigit

A Python version of the [multigit Bash script](https://github.com/jmnavarrol/simplest-git-subrepos).

While the multigit Bash script at [simplest-git-subrepos](https://github.com/jmnavarrol/simplest-git-subrepos) was created for illustration purposes, this one is intended to be a full-fledged implementation.

The general idea is to offer a simple way of managing *"workspaces"* integrating multiple git repos starting from a top one, and without the need of difficult *"arcanes"* like *git submodules*, *git-subtree*, etc.: you only need to declare your intended *layout* in a YAML file, and let this script do its job.  See the [simplest-git-subrepos README](https://github.com/jmnavarrol/simplest-git-subrepos) for a long-wired explanation.

## usage
*multigit* expects a YAML file named **subrepos** on the *root directory* of the current repo (see [example](./subrepos)).

For each defined *subrepo*, it will clone/checkout it to the defined relative path.  Optionally, it will *checkout* the given *gitref*, provided the repo's local sandbox is *"clean"* (i.e. no pending modifications).  
  **NOTE:** pay attention to the fact that if the *gitref* you record is a specific *commit*, the related sandbox will be in disconnected state.

*multigit* will also recursively look for new *subrepos* files on the repositories it manages.

**You should make sure** your [*.gitignore* file](./.gitignore) ignores all your *subrepos*.

This way you just need to manage your repos with `git` in the standard way, just as if they were individually checked out in isolation.

## development
For development purposes, you should create a Python 3 *virtualenv* using [the companion requirements file](./requirements.txt), i.e. (I'm using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io) here): `mkvirtualenv --python=$(which python3) -r requirements.txt python-multigit`.

Then, you can run this code by means of [the helper cmd script](./python-multigit-cmd.py), i.e.: `./python-multigit-cmd.py`.

------

### License
Python Multigit is made available under the terms of the **GPLv3**.

See the [license file](./LICENSE) that accompanies this distribution for the full text of the license.
