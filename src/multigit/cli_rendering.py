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


def print_subrepo_status(subrepo):
    """Render per-subrepo status in CLI-owned layer."""
    print("'%s':" % subrepo['path'])
    print("\trepository: '%s'" % subrepo['repo'])
    if subrepo['gitref_type']:
        gitref_type = subrepo['gitref_type']
        print("\trequested %s: '%s'" % (gitref_type, subrepo[gitref_type]))
    else:
        print("\tno gitref requested (working on default repo branch)")

    if subrepo['status'] == 'ERROR':
        print("\tstatus: ERROR")
        if 'extra_info' in subrepo:
            print("\textra info: %s" % subrepo['extra_info'].replace('\n', '\n\t\t'))
    elif subrepo['status'] == 'WRONG_REMOTE':
        print("\tstatus: REPO POINTS TO A WRONG REMOTE")
        if 'extra_info' in subrepo:
            print("\textra info: %s" % subrepo['extra_info'].replace('\n', '\n\t\t'))
    elif subrepo['status'] == 'NOT_CLONED':
        print("\tstatus: NOT YET CLONED")
    elif subrepo['status'] == 'CLONED':
        print("\tstatus: CLONED")
    elif subrepo['status'] == 'EMPTY':
        print("\tstatus: REMOTE REPO NOT YET INITIALIZED")
    elif subrepo['status'] == 'UP_TO_DATE':
        print("\tstatus: UP TO DATE")
    elif subrepo['status'] == 'PENDING_UPDATE':
        print("\tstatus: PENDING UPDATES")
        print("\tpending updates: '%s' -> '%s'" % (subrepo['from'], subrepo['to']))
    elif subrepo['status'] == 'UPDATED':
        print("\tupdated from '%s' -> '%s'" % (subrepo['from'], subrepo['to']))
    elif subrepo['status'] == 'DIRTY':
        print("\tstatus: DIRTY (won't try to update)")
    else:
        print("\tstatus: %s" % subrepo['status'])
