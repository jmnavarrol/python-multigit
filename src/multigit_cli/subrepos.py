# -*- coding: utf-8 -*-

"""
Subrepos orchestration for multigit CLI.

Handles recursive discovery and processing of subrepos files, coordinating between
CLI layer and library layer.
"""

import errno, os, sys
from git import Repo, exc as git_exception

# Library imports
from multigit import Gitrepo, SubrepofileError

# Local imports
from .subrepofile import Subrepofile
from . import console

class Subrepos(object):
	'''Recursively reads subrepos files and runs git commands as per its findings'''
	
	def __init__(self):
		'''Activates coloured output'''
		console.init_console()
		
		
	def process(
		self,
		base_path,
		subrepos_filename='subrepos',
		report_only=True
	):
		'''
		Recursively finds and processes subrepos files.
		
		If there's a 'subrepos' file right a `base_path`, it will be processed.
		
		If there is **not** a 'subrepos' file at `base_path` **and** `base_path` is within a git repo, it will try to find one at its root.
		
		:param str base_path: the absolute path to the directory where subrepos file will be searched for and processed.
		:param str subrepos_filename: 'subrepos'. Name of file holding subrepos' definitions.
		:param bool report_only: `True`, just shows dirtree status; `False`, updates dirtree.
		'''
		
		if os.path.isfile(os.path.join(base_path, subrepos_filename)):
			subrepos_file = os.path.realpath(
				os.path.join(base_path, subrepos_filename)
			)
		else:
			print("INFO: no valid '" + subrepos_filename + "' found at '" + base_path + "'.")
			# No subrepos file found at current path. Let's check if we are within a git sandbox
			try:
				repo = Repo(base_path, search_parent_directories=True)
				# we are in a git sandbox: get its "root"
				root_dir = repo.working_tree_dir
				print("INFO: processing git repository rooted at '" + root_dir + "':")
				
				if os.path.isfile(os.path.join(root_dir, subrepos_filename)):
					subrepos_file = os.path.realpath(
						os.path.join(root_dir, subrepos_filename)
					)
			except git_exception.InvalidGitRepositoryError as e:
				# Not a git repo: no more options left
				print("WARNING: Current dir '" + base_path + "' is not within a valid git sandbox.")
			
		# Let's see if we found a valid subrepos 'entry point'
		try:
			subrepos_file
		except NameError:
			print("ERROR: Couldn't find any '" + subrepos_filename + "' file... exiting.")
			sys.exit(errno.ENOENT)
		
		subrepo = Subrepofile()
		try:
			subrepos = subrepo.load(subrepos_file)
		except SubrepofileError as e:
			err_msg = f"ERROR: ({os.strerror(e.errno)}) {e}"
			print(err_msg)
			sys.exit(e.errno)
				
		if not subrepos:
			print("WARNING: Couldn't find any '" + subrepos_filename + "' file... exiting.")
			sys.exit(errno.ENOENT)
			
		# Recursively work on subrepos' contents
		while len(subrepos):
			current_subrepo = subrepos[0]
			
			# Operates on the current subrepo as requested
			git_subrepo = Gitrepo()
			if report_only:
				current_subrepo = git_subrepo.status(current_subrepo)
			else:
				current_subrepo = git_subrepo.update(current_subrepo)
				
			# Prints subrepo status
			console.print_subrepo_status(current_subrepo)
			
			# Let's see if new subrepos appeared and (eventually) append them to the queue
			try:
				new_subrepos = subrepo.load(
					os.path.join(current_subrepo['path'], subrepos_filename)
				)
			except FileNotFoundError as e:
				# It's acceptable not to find new subrepos at this location
				new_subrepos = []
				
			if new_subrepos:
				# add NEW subrepos to the list (already defined subrepos take precedence)
				subrepo_paths = set(
					path['path'] for path in subrepos
				)
				subrepos.extend(
					new_subrepo for new_subrepo in new_subrepos
					if new_subrepo['path'] not in subrepo_paths
				)
				del new_subrepos
			
			# done with this subrepo entry
			subrepos.remove(current_subrepo)


if __name__ == '__main__':
	# execute only if run as a script
	sys.exit(0)
