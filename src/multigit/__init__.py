# -*- coding: utf-8 -*-
"""
This script is a Python implementation of `simplest-git-subrepos <https://github.com/jmnavarrol/simplest-git-subrepos>`_.

:package: multigit |release|
:author: `Jesús M. Navarro <mailto:jesusmnavarrolopez@gmail.com>`_
:license: `GNU General Public License v3.0 <https://github.com/jmnavarrol/python-multigit/blob/main/LICENSE>`_
:source: https://github.com/jmnavarrol/python-multigit
"""

__version__ = '0.10.5'

# Import stuff
import os, sys
import argparse

# "local" imports
from .subrepos import Subrepos, SUBREPOS_FILE



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
			print("%s (%s)\n" % (parser.prog, __version__))
			parser.print_help()
		elif args.version:
			print("%s %s" % (parser.prog, __version__))
		else:
			my_subrepos = Subrepos()
			my_subrepos.process(os.getcwd(), report_only=args.status)
	else:
	# Program called with no arguments (shows help)
		print("%s (%s): arguments required.\n" % (parser.prog, __version__))
		parser.print_help()
		
		
if __name__ == '__main__':
	# execute only if run as a script
	main()
