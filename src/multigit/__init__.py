# -*- coding: utf-8 -*-

"""
This script is a Python implementation of multigit.
(see https://github.com/jmnavarrol/simplest-git-subrepos)

:author: jesusmnavarrolopez@gmail.com
:version: Beta
:package: multigit
:copyright: Jesús M. Navarro
"""
__version__ = '0.5.0'

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
		epilog="With no options: finds and processes '" + SUBREPOS_FILE + "' files.",
	)
	
# Main options
	parser.add_argument('-V', '--version', action='store_true', help="show " + parser.prog + " version and exit")
	
# Ready to parse args
	args = parser.parse_args()
	#print(args)
	
	if len(sys.argv) > 1:
		if args.version:
			print("%s %s" % (parser.prog, __version__))
	else:
	# Program called with no arguments (runs default action)
		my_subrepos = Subrepos()
		my_subrepos.process(os.getcwd())
		
