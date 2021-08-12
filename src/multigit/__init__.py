# -*- coding: utf-8 -*-

"""
This script is a Python implementation of multigit.
(see https://github.com/jmnavarrol/simplest-git-subrepos)

:author: jesusmnavarrolopez@gmail.com
:version: Beta
:package: multigit
:copyright: Jesús M. Navarro
"""
__version__ = '0.6.0'

# Import stuff
import os, sys
import argparse

# "local" imports
from .subrepos import Subrepos, SUBREPOS_FILE



# MAIN entry point
def main():
# Processes command line parameters
	parser = argparse.ArgumentParser(
		description="Manages git repos within git repos.",
		add_help=False,  # this way I can force help to be an exclusion option along the others
	)
	
# Main options
	main_parser = parser.add_mutually_exclusive_group()
	main_parser.add_argument('-h', '--help', action='store_true', help="shows this help.")
	main_parser.add_argument('-V', '--version', action='store_true', help="shows " + parser.prog + " version and exit.")
	main_parser.add_argument('-r', '--run', action='store_true', help="recursively processes '" + SUBREPOS_FILE + "' files found.")
	
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
		elif args.run:
			my_subrepos = Subrepos()
			my_subrepos.process(os.getcwd())
	else:
	# Program called with no arguments (shows help)
		print("%s (%s): arguments required.\n" % (parser.prog, __version__))
		parser.print_help()
		
