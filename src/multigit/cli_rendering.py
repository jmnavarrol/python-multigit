# -*- coding: utf-8 -*-

import errno
import os

from git import Repo, exc as git_exception


def print_orchestration_error(error, subrepos_filename):
    """Render orchestration errors with legacy-compatible CLI semantics."""
    if getattr(error, 'errno', errno.EINVAL) == errno.ENOENT:
        print("ERROR: Couldn't find any '%s' file... exiting." % subrepos_filename)
    else:
        err_no = getattr(error, 'errno', errno.EINVAL)
        print("ERROR: (%s) %s" % (os.strerror(err_no), error))


def print_missing_subrepos_context(base_path, subrepos_filename):
    """Emit legacy context lines when no subrepos entrypoint can be resolved."""
    print("INFO: no valid  '%s' found at '%s'." % (subrepos_filename, base_path))
    try:
        repo = Repo(base_path, search_parent_directories=True)
        root_dir = repo.working_tree_dir
        print("INFO: processing git repository rooted at '%s':" % root_dir)
    except git_exception.InvalidGitRepositoryError:
        print("WARNING: Current dir '%s' is not within a valid git sandbox." % base_path)
