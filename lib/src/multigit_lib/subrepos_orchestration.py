# -*- coding: utf-8 -*-

# Import stuff
import errno
import os

from git import Repo, exc as git_exception

# local imports
from .gitrepo import Gitrepo
from .subrepofile import Subrepofile, SubrepofileError


class SubreposOrchestrationError(Exception):
    """Library-safe orchestration error with errno compatibility."""

    def __init__(self, msg, error_no=errno.EINVAL, *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
        self.errno = error_no


class Subrepos(object):
    """Library-safe copy of legacy subrepos orchestration."""

    def process(self, base_path, subrepos_filename="subrepos", report_only=True):
        """Recursively process subrepos and return processed entries."""
        subrepos_file = self._resolve_subrepos_entrypoint(base_path, subrepos_filename)

        subrepo_loader = Subrepofile()
        try:
            subrepos = subrepo_loader.load(subrepos_file)
        except SubrepofileError as err:
            raise SubreposOrchestrationError(str(err), error_no=err.errno)

        if not subrepos:
            raise SubreposOrchestrationError(
                f"Couldn't find any '{subrepos_filename}' file... exiting.",
                error_no=errno.ENOENT,
            )

        processed = []
        while len(subrepos):
            current_subrepo = subrepos[0]

            git_subrepo = Gitrepo()
            if report_only:
                current_subrepo = git_subrepo.status(current_subrepo)
            else:
                current_subrepo = git_subrepo.update(current_subrepo)

            processed.append(current_subrepo)

            try:
                new_subrepos = subrepo_loader.load(
                    os.path.join(current_subrepo["path"], subrepos_filename)
                )
            except FileNotFoundError:
                new_subrepos = []

            if new_subrepos:
                subrepo_paths = set(path["path"] for path in subrepos)
                subrepos.extend(
                    new_subrepo
                    for new_subrepo in new_subrepos
                    if new_subrepo["path"] not in subrepo_paths
                )

            subrepos.remove(current_subrepo)

        return processed

    def _resolve_subrepos_entrypoint(self, base_path, subrepos_filename):
        candidate = os.path.join(base_path, subrepos_filename)
        if os.path.isfile(candidate):
            return os.path.realpath(candidate)

        try:
            repo = Repo(base_path, search_parent_directories=True)
            root_dir = repo.working_tree_dir
        except git_exception.InvalidGitRepositoryError:
            root_dir = None

        if root_dir:
            candidate = os.path.join(root_dir, subrepos_filename)
            if os.path.isfile(candidate):
                return os.path.realpath(candidate)

        raise SubreposOrchestrationError(
            f"Couldn't find any '{subrepos_filename}' file... exiting.",
            error_no=errno.ENOENT,
        )


def process_subrepos(base_path, subrepos_filename="subrepos", report_only=True):
    """Function wrapper for class-based orchestration."""
    return Subrepos().process(base_path, subrepos_filename, report_only)
