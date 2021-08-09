# -*- coding: utf-8 -*-
"""
Processes a subrepo
"""

# Import stuff
import os, errno, sys
from git import Repo, exc as git_exception

from colorama import init, Fore, Back, Style
#Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: DIM, NORMAL, BRIGHT, RESET_ALL

# "local" imports
from .subrepos_file import SUBREPO_FORMAT

class Subrepo(object):
	
	@staticmethod
	def root(dir):
		'''
		Returns the root path or the current git repo, or None, if 'dir' is not within a git sandbox
		'''
		try:
			repo = Repo(dir, search_parent_directories=True)
			# we are: let's go to its "root" to look for a subrepos file
			working_dir = repo.working_tree_dir
		except git_exception.InvalidGitRepositoryError as e:
			# Not a git repo
			working_dir = None
			
		return working_dir
		
		
	@staticmethod
	def process(subrepo):
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
				
