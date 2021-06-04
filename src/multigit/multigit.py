#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is a Python implementation of multigit.
(see https://github.com/jmnavarrol/simplest-git-subrepos)

:author: jesusmnavarrolopez@gmail.com
:version: prototype
:package: <null>
:copyright: Jesús M. Navarro
"""
__version__ = "0.1.0"

# Import stuff
import os, errno, sys
import yaml
from git import Repo, exc as git_exception

from colorama import init, Fore, Back, Style
#Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: DIM, NORMAL, BRIGHT, RESET_ALL

# Globals
SUBREPO_FILE = 'subrepos'


def find_current_tree_dir(current_dir):
	# First, check if we are in a git sandbox at all
	try:
		repo = Repo('.', search_parent_directories=True)
	except git_exception.InvalidGitRepositoryError as e:
		print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
		print("Current dir " + Style.BRIGHT + "'" + current_dir + "'", end=' ')
		print("is not within a valid git repo!")
		sys.exit(errno.EINVAL)
		
	# We are in a git sandbox: return is "root dir"
	return repo.working_tree_dir


def find_subrepos(current_dir):
	subrepo_file = current_dir + "/" + SUBREPO_FILE
	
	# Check if we can find here a 'subrepos' definition file
	try:
		f_config = open(subrepo_file, 'r')
		try:
			configMap = yaml.safe_load(f_config)
		except yaml.parser.ParserError as e:
			print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
			print(Style.BRIGHT + "Malformed YAML file", end=' - ')
			print(e)
			sys.exit(errno.EINVAL)
		f_config.close()
	except IOError as e:
		if e.errno==errno.ENOENT:
			configMap = None
		else: raise
	
	if configMap:
		try:
			subrepo_list = configMap['subrepos']
			for subrepo in subrepo_list:
				# Let's set the repo's local path to its absolute location for easier tracking
				subrepo['path'] = current_dir + '/' + subrepo['path']
		except KeyError as e:
			print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
			print('Mandatory key ' + Style.BRIGHT + "'subrepos'", end=' ')
			print("couldn't be found in file " + Style.BRIGHT + "'" + SUBREPO_FILE + "'" + "!\n")
			sys.exit(errno.ENOENT)
	else:
		subrepo_list = []
		
	return subrepo_list


def manage_subrepo(subrepo):
	# find or clone given subrepo
	try:
		repo = Repo(subrepo['path'])
	except git_exception.NoSuchPathError as e:
		# repo not yet downloaded
		repo = Repo.clone_from(subrepo['repo'], subrepo['path'])
		
	# checkout gitref if requested and possible
	if 'gitref' in subrepo:
		# specific 'gitref' requested
		if not repo.is_dirty():
			try:
				repo.git.checkout(subrepo['gitref'])
			except git_exception.GitCommandError as e:
				print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
				print(Style.BRIGHT + e.stderr)



# MAIN entry point
def main():
	# Activates colored output
	init(autoreset=True)
	
	# Fist load
	current_dir = find_current_tree_dir(os.getcwd())
	subrepos = find_subrepos(current_dir)
	
	# Recursively work on findings
	while len(subrepos):
		manage_subrepo(subrepos[0])
		new_subrepos = find_subrepos(subrepos[0]['path'])
		# done with this subrepo
		subrepos.remove(subrepos[0])
		# Now, let's add new additions to the queue
		if new_subrepos:
			subrepos.extend(new_subrepos)
