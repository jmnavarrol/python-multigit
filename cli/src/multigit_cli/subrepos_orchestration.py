import errno
import os

from git import Repo, exc as git_exception

from multigit_lib import Gitrepo

from .subrepofile import Subrepofile, SubrepofileError


class SubreposOrchestrationError(Exception):
    """CLI workflow error with an errno-compatible exit code."""

    def __init__(self, message, error_no=errno.EINVAL):
        super().__init__(message)
        self.errno = error_no


class Subrepos:
    """Discover subrepos files and run their normalized entries through the library."""

    def process(self, base_path, subrepos_filename='subrepos', report_only=True):
        """Process a full tree and return all repository results."""
        return list(self.iter_process(base_path, subrepos_filename, report_only))

    def iter_process(self, base_path, subrepos_filename='subrepos', report_only=True):
        """Yield each result as its repository operation completes."""
        subrepo_loader = Subrepofile()
        subrepos_file = self._resolve_subrepos_entrypoint(base_path, subrepos_filename)
        try:
            subrepos = subrepo_loader.load(subrepos_file)
        except SubrepofileError as error:
            raise SubreposOrchestrationError(str(error), error_no=error.errno) from error

        if not subrepos:
            raise SubreposOrchestrationError(
                f"Couldn't find any '{subrepos_filename}' file... exiting.",
                error_no=errno.ENOENT,
            )

        while subrepos:
            current_subrepo = subrepos[0]
            try:
                if report_only:
                    current_subrepo = Gitrepo().status(current_subrepo)
                else:
                    current_subrepo = Gitrepo().update(current_subrepo)
            except Exception as error:
                current_subrepo['status'] = 'ERROR'
                current_subrepo['extra_info'] = str(error)

            yield current_subrepo

            try:
                nested_subrepos = subrepo_loader.load(
                    os.path.join(current_subrepo['path'], subrepos_filename)
                )
            except FileNotFoundError:
                nested_subrepos = []
            except SubrepofileError as error:
                raise SubreposOrchestrationError(str(error), error_no=error.errno) from error

            if nested_subrepos:
                known_paths = {entry['path'] for entry in subrepos}
                subrepos.extend(
                    entry for entry in nested_subrepos if entry['path'] not in known_paths
                )

            subrepos.remove(current_subrepo)

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


def process_subrepos(base_path, subrepos_filename='subrepos', report_only=True):
    """Process subrepos files from the given CLI working directory."""
    return Subrepos().process(base_path, subrepos_filename, report_only)


def iter_process_subrepos(base_path, subrepos_filename='subrepos', report_only=True):
    """Yield processed repository results from the given CLI working directory."""
    return Subrepos().iter_process(base_path, subrepos_filename, report_only)