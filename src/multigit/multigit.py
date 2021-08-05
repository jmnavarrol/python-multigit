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
__version__ = "0.2.1"

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
SUBREPO_FORMAT = {
	'MANDATORY': [
		'path',
		'repo',
	],
	# only one gitref entry allowed
	'GITREF': [
		'branch',
		'tag',
		'commit',
	]
}


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
			for index, subrepo in enumerate(subrepo_list):
			# Validate subrepo configuration
				# mandatory keys
				for key in SUBREPO_FORMAT['MANDATORY']:
					if not key in subrepo:
						print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
						print(Style.BRIGHT + "'" + subrepo_file + "'", end='\n')
						print("\tSubrepo entry " + Style.BRIGHT + "[" + str(index) + "]", end=': ')
						print('mandatory key ' + Style.BRIGHT + "'" + key + "'", end=' ')
						print("couldn't be found!")
						sys.exit(errno.EINVAL)
				# optional keys
				optional_keys=list(set(subrepo.keys()) - set(SUBREPO_FORMAT['MANDATORY']))
				# tests for invalid keys
				for key in optional_keys:
					if not key in SUBREPO_FORMAT['GITREF']:
						print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
						print(Style.BRIGHT + "'" + subrepo_file + "'", end='\n')
						print("\tSubrepo entry " + Style.BRIGHT + "[" + str(index) + "]", end=': ')
						print("invalid key " + Style.BRIGHT + "'" + key + "'", end='!\n')
						sys.exit(errno.EINVAL)
				# tests 'gitrefs' (only one of 'commit','tag','branch' is allowed)
				if(sum(x in optional_keys for x in SUBREPO_FORMAT['GITREF']) > 1):
					print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
					print(Style.BRIGHT + "'" + subrepo_file + "'", end='\n')
					print("\tSubrepo entry " + Style.BRIGHT + "[" + str(index) + "]", end=': ')
					print("incompatible keys.  Only one of " + Style.BRIGHT + str(SUBREPO_FORMAT['GITREF']), end=' ')
					print("allowed!")
					sys.exit(errno.EINVAL)
					
			# Let's set the repo's local path to its absolute location for easier tracking
				subrepo['path'] = current_dir + '/' + subrepo['path']
		except KeyError as e:
			print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
			print(Style.BRIGHT + "'" + subrepo_file + "'", end='\n')
			print('\tMandatory key ' + Style.BRIGHT + "'subrepos'", end=' ')
			print("couldn't be found!")
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
		try:
			if 'branch' in subrepo:
				try:
					repo = Repo.clone_from(subrepo['repo'], subrepo['path'], branch=subrepo['branch'])
				except git_exception.GitCommandError as e:
					print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
					print(Style.BRIGHT + e.stderr)
					sys.exit(errno.EBADE)
			elif 'tag' in subrepo:
				try:
					repo = Repo.clone_from(subrepo['repo'], subrepo['path'], branch=subrepo['tag'])
				except git_exception.GitCommandError as e:
					print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
					print(Style.BRIGHT + e.stderr)
					sys.exit(errno.EBADE)
			elif 'commit' in subrepo:
				try:
					repo = Repo.clone_from(subrepo['repo'], subrepo['path'])
				except git_exception.GitCommandError as e:
					print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
					print(Style.BRIGHT + e.stderr)
					sys.exit(errno.EBADE)
			else:
				try:
					repo = Repo.clone_from(subrepo['repo'], subrepo['path'])
				except git_exception.GitCommandError as e:
					print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
					print(Style.BRIGHT + e.stderr)
					sys.exit(errno.EBADE)
		except git_exception.GitCommandError as e:
			print(e.stderr)
			sys.exit(errno.ENOENT)
			
		print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
		print("Repo " + Style.BRIGHT + "'" + subrepo['repo'] + "'", end=' ')
		print("cloned at " + Style.BRIGHT + "'" + subrepo['path'] + "'", end='.\n')
		
	# checkout gitref if requested and possible
	if any(gitref in subrepo for gitref in SUBREPO_FORMAT['GITREF']):
		if not repo.is_dirty():
			current_commit = str(repo.head.commit)
			repo.remotes.origin.fetch()
			if 'branch' in subrepo:
				desired_commit = str(repo.commit('origin/' + subrepo['branch']))
				if current_commit != desired_commit:
					try:
						repo.git.checkout(subrepo['branch'])
					except git_exception.GitCommandError as e:
						print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
						print(Style.BRIGHT + e.stderr)
						sys.exit(errno.EBADE)
					print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
					print("Repo at " + Style.BRIGHT + "'" + subrepo['path'] + "'", end='.\n')
					print("\tupdated: " + Style.BRIGHT + "'" + current_commit + "'", end=' -> ')
					print(Style.BRIGHT + "'" + desired_commit + "'")
			elif 'tag' in subrepo:
				desired_commit = str(repo.commit(subrepo['tag']))
				if current_commit != desired_commit:
					try:
						repo.git.checkout(subrepo['tag'])
					except git_exception.GitCommandError as e:
						print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
						print(Style.BRIGHT + e.stderr)
						sys.exit(errno.EBADE)
					print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
					print("Repo at " + Style.BRIGHT + "'" + subrepo['path'] + "'", end='.\n')
					print("\tupdated: " + Style.BRIGHT + "'" + current_commit + "'", end=' -> ')
					print(Style.BRIGHT + "'" + desired_commit + "'")
			elif 'commit' in subrepo:
				desired_commit = str(subrepo['commit'])
				if current_commit != desired_commit:
					try:
						repo.git.checkout(subrepo['commit'])
					except git_exception.GitCommandError as e:
						print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
						print(Style.BRIGHT + e.stderr)
						sys.exit(errno.EBADE)
					print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
					print("Repo at " + Style.BRIGHT + "'" + subrepo['path'] + "'", end='.\n')
					print("\tupdated: " + Style.BRIGHT + "'" + current_commit + "'", end=' -> ')
					print(Style.BRIGHT + "'" + desired_commit + "'")
			else:
				error_line = str(sys._getframe().f_lineno - 1)
				print(Style.BRIGHT + Fore.RED + "INTERNAL ERROR:", end=' ')
				print("wrong gitref type at " + Style.BRIGHT + "'" + os.path.abspath(__file__) + Style.BRIGHT + "'", end=', ')
				print("line number " + Style.BRIGHT + "'" + error_line + "'", end='.\n')
				sys.exit(errno.EINVAL)



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
