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

from colorama import init, Fore, Back, Style
#Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: DIM, NORMAL, BRIGHT, RESET_ALL

# "local" imports
from .subrepos_file import SubreposFile, SUBREPOS_FILE
from .subrepo import Subrepo



# Main subrepos' process loop
def loop():
	# First, let's check if we are in a git sandbox at all
	working_dir = Subrepo.root(os.getcwd())
	if working_dir is None:
		# Not a git repo; fall back to current dir as "root"
		working_dir = os.getcwd()
		print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
		print("Current dir " + Style.BRIGHT + "'" + working_dir + "'", end=' ')
		print("is not within a valid git repo.")
		print("\tLooking for a " + Style.BRIGHT + "'"  + SUBREPOS_FILE + "'", end=' ')
		print("file right here instead.")
	
	# Let's find the "main" subrepos file (if any)
	my_subrepos_file = SubreposFile()
	subrepos = my_subrepos_file.load(working_dir)
	
	# Recursively work on findings
	while len(subrepos):
		# Operates (clone, update...) the first subrepo on the list
		Subrepo.process(subrepos[0])
		# See if new subrepos did appear
		new_subrepos = my_subrepos_file.load(subrepos[0]['path'])
		# done with this subrepo entry
		subrepos.remove(subrepos[0])
		
		# Now, let's add new findings to the queue (if any)
		if new_subrepos:
			subrepos.extend(new_subrepos)
	
	
# MAIN entry point
def main():
# Activates colored output
	init(autoreset=True)
	
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
		loop()
		
