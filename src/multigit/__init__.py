# -*- coding: utf-8 -*-

"""
This script is a Python implementation of multigit.
(see https://github.com/jmnavarrol/simplest-git-subrepos)

:author: jesusmnavarrolopez@gmail.com
:version: Beta
:package: multigit
:copyright: Jesús M. Navarro
"""
__version__ = '0.4.0'

# Import stuff
import os, errno, sys
import argparse
import yaml
from git import Repo, exc as git_exception

from colorama import init, Fore, Back, Style
#Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: DIM, NORMAL, BRIGHT, RESET_ALL

# Globals
SUBREPOS_FILE = 'subrepos'
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


def load_subrepos_file(current_dir):
	subrepos_file = current_dir + "/" + SUBREPOS_FILE
	
	# Check if we can find here a 'subrepos' definition file
	try:
		f_config = open(subrepos_file, 'r')
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
	
	# 'subrepos' file found: validate and load its contents
	if configMap:
		try:
			subrepo_list = configMap['subrepos']
			for index, subrepo in enumerate(subrepo_list):
			# Validate subrepo configuration
				# mandatory keys
				for key in SUBREPO_FORMAT['MANDATORY']:
					if not key in subrepo:
						print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
						print(Style.BRIGHT + "'" + subrepos_file + "'", end='\n')
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
						print(Style.BRIGHT + "'" + subrepos_file + "'", end='\n')
						print("\tSubrepo entry " + Style.BRIGHT + "[" + str(index) + "]", end=': ')
						print("invalid key " + Style.BRIGHT + "'" + key + "'", end='!\n')
						sys.exit(errno.EINVAL)
				# tests 'gitrefs' (only one of 'commit','tag','branch' is allowed)
				if(sum(x in optional_keys for x in SUBREPO_FORMAT['GITREF']) > 1):
					print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
					print(Style.BRIGHT + "'" + subrepos_file + "'", end='\n')
					print("\tSubrepo entry " + Style.BRIGHT + "[" + str(index) + "]", end=': ')
					print("incompatible keys.  Only one of " + Style.BRIGHT + str(SUBREPO_FORMAT['GITREF']), end=' ')
					print("allowed!")
					sys.exit(errno.EINVAL)
					
			# Let's set the repo's local path to its absolute location for easier tracking
				subrepo['path'] = current_dir + '/' + subrepo['path']
		except KeyError as e:
			print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
			print(Style.BRIGHT + "'" + subrepos_file + "'", end='\n')
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
		# repo not yet cloned
		branch_like = None
		if 'branch' in subrepo:
			branch_like = branch=subrepo['branch']
		elif 'tag' in subrepo:
			branch_like = branch=subrepo['tag']
			
		try:
			if branch_like:
				repo = Repo.clone_from(subrepo['repo'], subrepo['path'], branch=branch_like)
			else:
				repo = Repo.clone_from(subrepo['repo'], subrepo['path'])
		except git_exception.GitCommandError as e:
			print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
			print(Style.BRIGHT + e.stderr)
			sys.exit(errno.EBADE)
			
		print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
		print("Repo " + Style.BRIGHT + "'" + subrepo['repo'] + "'")
		print("\tCloned at " + Style.BRIGHT + "'" + subrepo['path'] + "'")
		
	# Update sandbox if needed and possible
	current_commit = repo.commit().hexsha
	repo.remotes.origin.fetch()
	
	if any(gitref in subrepo for gitref in SUBREPO_FORMAT['GITREF']):
		if 'branch' in subrepo:
			desired_commit = str(repo.commit('origin/' + subrepo['branch']))
			gitref = subrepo['branch']
		elif 'tag' in subrepo:
			desired_commit = str(repo.commit(subrepo['tag']))
			gitref = subrepo['tag']
		elif 'commit' in subrepo:
			desired_commit = str(subrepo['commit'])
			gitref = subrepo['commit']
		else:
			error_line = str(sys._getframe().f_lineno - 1)
			print(Style.BRIGHT + Fore.RED + "INTERNAL ERROR:", end=' ')
			print("wrong gitref type at " + Style.BRIGHT + "'" + os.path.abspath(__file__) + Style.BRIGHT + "'", end=', ')
			print("line number " + Style.BRIGHT + "'" + error_line + "'", end='.\n')
			sys.exit(errno.EINVAL)
	else:
		desired_commit = repo.remotes.origin.refs.HEAD.commit.hexsha
		gitref = repo.git.symbolic_ref('refs/remotes/origin/HEAD').replace('refs/remotes/origin/','')
		
	# The sandbox update itself
	if current_commit != desired_commit:
		if not repo.is_dirty():
			try:
				repo.git.checkout(gitref)
			except git_exception.GitCommandError as e:
				print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
				print(Style.BRIGHT + e.stderr)
				sys.exit(errno.EBADE)
				
			if not repo.head.is_detached:
				repo.git.pull()
				
			print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
			print("Repo at " + Style.BRIGHT + "'" + subrepo['path'] + "'")
			print("\tUpdated: " + Style.BRIGHT + "'" + current_commit + "'", end=' -> ')
			print(Style.BRIGHT + "'" + desired_commit + "'")
		else:
			print(Style.BRIGHT + Fore.YELLOW + "WARNING:", end=' ')
			print("at " + Style.BRIGHT + "'" + subrepo['path'] + "'")
			print(Style.BRIGHT + "\tSubrepo is dirty:", end=' ')
			print("won't try to update.")



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
		# First, let's check if we are in a git sandbox at all
		try:
			repo = Repo(os.getcwd(), search_parent_directories=True)
			# we are: let's go to its "root" to look for a subrepos file
			working_dir = repo.working_tree_dir
		except git_exception.InvalidGitRepositoryError as e:
			# Not a git repo; fall back to current dir as "root"
			working_dir = os.getcwd()
			print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
			print("Current dir " + Style.BRIGHT + "'" + working_dir + "'", end=' ')
			print("is not within a valid git repo.")
			print("\tLooking for a " + Style.BRIGHT + "'"  + SUBREPOS_FILE + "'", end=' ')
			print("file right here instead.")
		
		# Let's find the "main" subrepos file (if any)
		subrepos = load_subrepos_file(working_dir)
		
		# Recursively work on findings
		while len(subrepos):
			# Operates (clone, update...) the first subrepo on the list
			manage_subrepo(subrepos[0])
			# See if new subrepos files have appeared
			new_subrepos = load_subrepos_file(subrepos[0]['path'])
			# done with this subrepo
			subrepos.remove(subrepos[0])
			# Now, let's add new additions to the queue (if any)
			if new_subrepos:
				subrepos.extend(new_subrepos)
				
