# -*- coding: utf-8 -*-

"""
**multigit** script is a Python implementation of `simplest-git-subrepos <https://github.com/jmnavarrol/simplest-git-subrepos>`_.

:package: multigit |release|
:author: `Jesús M. Navarro <mailto:jesusmnavarrolopez@gmail.com>`_
:license: `GNU General Public License v3.0 <https://github.com/jmnavarrol/python-multigit/blob/main/LICENSE>`_
:source: https://github.com/jmnavarrol/python-multigit
"""

# Globals
__version__ = '0.12.0.dev1'
SUBREPOS_FILE = 'subrepos'
'''
The *"fixed"* name of the YAML file with subrepo definitions.
'''  # pylint: disable=W0105

# Import stuff
import errno
import os, sys
import argparse
from git import Repo, exc as git_exception

# "local" imports
from .subrepos import Subrepos


def _process_subrepos_legacy(base_path, report_only):
	"""Legacy execution path kept as default during migration stages."""
	my_subrepos = Subrepos()
	return my_subrepos.process(
		base_path=base_path,
		subrepos_filename=SUBREPOS_FILE,
		report_only=report_only,
	)


def _process_subrepos_adapter(base_path, report_only):
	"""Adapter seam for progressive migration to library-backed orchestration."""
	return _process_subrepos_multigit_lib_adapter(
		base_path=base_path,
		report_only=report_only,
	)


def _process_subrepos(base_path, report_only):
	"""Boundary for selecting execution path without changing CLI semantics."""
	# Keep legacy lane as the default execution path for Phases 0-4.
	return _process_subrepos_adapter(
		base_path=base_path,
		report_only=report_only,
	)


def _get_cli_version_legacy():
	"""Legacy version source used by the current CLI packaging metadata."""
	return __version__


def _get_cli_version_adapter():
	"""Adapter seam for future metadata source migration without UX drift."""
	return _get_cli_version_legacy()


def _get_cli_version():
	"""Boundary for CLI-visible version retrieval."""
	return _get_cli_version_adapter()


def _load_multigit_lib_status_orchestrator():
	"""Resolve multigit_lib status orchestration function and error class."""
	try:
		from multigit_lib.subrepos_orchestration import (  # type: ignore
			process_subrepos,
			SubreposOrchestrationError,
		)
		return process_subrepos, SubreposOrchestrationError
	except ModuleNotFoundError:
		repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
		lib_src = os.path.join(repo_root, 'lib', 'src')
		if os.path.isdir(lib_src) and lib_src not in sys.path:
			sys.path.insert(0, lib_src)
		from multigit_lib.subrepos_orchestration import (  # type: ignore
			process_subrepos,
			SubreposOrchestrationError,
		)
		return process_subrepos, SubreposOrchestrationError


def _print_orchestration_error(error):
	"""Render orchestration errors with legacy-compatible CLI semantics."""
	if getattr(error, 'errno', errno.EINVAL) == errno.ENOENT:
		print("ERROR: Couldn't find any 'subrepos' file... exiting.")
	else:
		err_no = getattr(error, 'errno', errno.EINVAL)
		print("ERROR: (%s) %s" % (os.strerror(err_no), error))


def _print_missing_subrepos_context(base_path):
	"""Emit legacy context lines when no subrepos entrypoint can be resolved."""
	print("INFO: no valid  '%s' found at '%s'." % (SUBREPOS_FILE, base_path))
	try:
		repo = Repo(base_path, search_parent_directories=True)
		root_dir = repo.working_tree_dir
		print("INFO: processing git repository rooted at '%s':" % root_dir)
	except git_exception.InvalidGitRepositoryError:
		print("WARNING: Current dir '%s' is not within a valid git sandbox." % base_path)


def _process_subrepos_multigit_lib_adapter(base_path, report_only):
	"""Run/status paths migrated to multigit_lib with CLI rendering parity."""
	process_subrepos, orchestration_error = _load_multigit_lib_status_orchestrator()
	try:
		processed_subrepos = process_subrepos(
			base_path=base_path,
			subrepos_filename=SUBREPOS_FILE,
			report_only=report_only,
		)
	except orchestration_error as error:
		if getattr(error, 'errno', errno.EINVAL) == errno.ENOENT:
			_print_missing_subrepos_context(base_path)
		_print_orchestration_error(error)
		sys.exit(getattr(error, 'errno', errno.EINVAL))

	legacy_renderer = Subrepos()
	for current_subrepo in processed_subrepos:
		legacy_renderer._Subrepos__print_subrepo_status(current_subrepo)

	return None

# MAIN entry point
def main():
	'''Processes command line parameters'''
	parser = argparse.ArgumentParser(
		description="Manages git repos within git repos.",
		add_help=False,  # this way I can force help to be an exclusion option along the others
	)

# Main options
	main_parser = parser.add_mutually_exclusive_group()
	main_parser.add_argument('-h', '--help', action='store_true', help="Shows this help.")
	main_parser.add_argument('-V', '--version', action='store_true', help="Shows " + parser.prog + " version and quits.")
	main_parser.add_argument('-r', '--run', action='store_true', help="Recursively processes '" + SUBREPOS_FILE + "' files found.")
	main_parser.add_argument('-s', '--status', action='store_true', help="Shows repositories' current status.")

# Ready to parse args
	args = parser.parse_args()
	#print(args)

# Run on the options
	if len(sys.argv) > 1:
		if args.help:
			print("%s (%s)\n" % (parser.prog, _get_cli_version()))
			parser.print_help()
		elif args.version:
			print("%s %s" % (parser.prog, _get_cli_version()))
		else:
			_process_subrepos(
				base_path=os.getcwd(),
				report_only=args.status,
			)
	else:
	# Program called with no arguments (shows help)
		print("%s (%s): arguments required.\n" % (parser.prog, _get_cli_version()))
		parser.print_help()


if __name__ == '__main__':
	sys.exit(
		main()
	)
