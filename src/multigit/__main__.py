# -*- coding: utf-8 -*-

"""
**multigit** script is a Python implementation of `simplest-git-subrepos <https://github.com/jmnavarrol/simplest-git-subrepos>`_.

:package: multigit |release|
:author: `Jesús M. Navarro <mailto:jesusmnavarrolopez@gmail.com>`_
:license: `GNU General Public License v3.0 <https://github.com/jmnavarrol/python-multigit/blob/main/LICENSE>`_
:source: https://github.com/jmnavarrol/python-multigit
"""

# Globals
__version__ = '0.12.0.dev3'
SUBREPOS_FILE = 'subrepos'
'''
The *"fixed"* name of the YAML file with subrepo definitions.
'''  # pylint: disable=W0105

# Import stuff
import os
import sys
import argparse

# "local" imports
from .status_run_adapter import process_subrepos_with_adapter


def _process_subrepos(base_path, report_only):
	"""Run CLI status/run flow through the canonical adapter path."""
	return process_subrepos_with_adapter(
		base_path=base_path,
		report_only=report_only,
		subrepos_filename=SUBREPOS_FILE,
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
