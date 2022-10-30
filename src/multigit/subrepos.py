# -*- coding: utf-8 -*-

# Import stuff
import errno, os, sys
import importlib.resources as pkg_resources
import yaml
from cerberus import Validator, schema
from git import Repo, exc as git_exception

from colorama import init, Fore, Back, Style
#Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: DIM, NORMAL, BRIGHT, RESET_ALL


# Globals
SUBREPOS_FILE = 'subrepos'
'''
The *"fixed"* name of the YAML file with subrepo definitions.

This file will first be loaded from current dir.

Otherwise, if within a git sandbox, it will be looked for at the git sandbox' root.
'''  # pylint: disable=W0105

class Subrepos(object):
	'''Recursively reads subrepos files and runs git commands as per its findings'''
	
	def __init__(self):
		'''Activates colored output'''
		init(autoreset=True)
		
		# Loads the YAML schema validator
		try:
			with pkg_resources.path(__package__, 'subrepos_schema.yaml') as validator_resource:
				with open(validator_resource, 'r') as f_yaml_rules:
					try:
						yaml_rules = yaml.safe_load(f_yaml_rules)
					except yaml.parser.ParserError as e:
						print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
						print(Style.BRIGHT + "Malformed YAML file", end=' - ')
						print(e)
						sys.exit(errno.EINVAL)
		except FileNotFoundError as e:
			print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
			print(e)
			sys.exit(errno.ENOENT)
			
		try:
			self.yaml_validator = Validator(yaml_rules)
		except Exception as e:
			print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
			print("In YAML schema validator at ", end=' ')
			print(Style.BRIGHT + "'" + str(validator_resource) + "'", end='.\n')
			if (
				type(e) is schema.SchemaError
				or type(e) is TypeError
			):
				print("\t" + str(e))
				sys.exit(errno.EINVAL)
			else:
				raise
		
		
	def process(self, base_path, report_only=True):
		'''
		Recursively finds and processes subrepos files.
		
		If there's a 'subrepos' file right a `base_path`, it will be processed.
		
		If there is **not** a 'subrepos' file at `base_path` **and** `base_path` is within a git repo, it will try to find one at its root.
		
		:param str base_path: the absolute path to the directory where subrepos file will be searched and processed.
		:param bool report_only: `True`, just shows dirtree status; `False`, updates dirtree.
		'''
		
		subrepos_file = base_path + "/" + SUBREPOS_FILE
		if os.path.isfile(subrepos_file) and os.access(subrepos_file, os.R_OK):
			# found and readable: let's use it
			root_dir = base_path
			print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
			print("processing '" + SUBREPOS_FILE + "' file rooted at", end=' ')
			print(Style.BRIGHT + "'" + base_path + "'", end=':\n')
		else:
			print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
			print("no valid '" + SUBREPOS_FILE + "' file found at", end=' ')
			print(Style.BRIGHT + "'" + base_path + "'", end=':\n')
			# Let's check if within a git sandbox
			try:
				repo = Repo(base_path, search_parent_directories=True)
				# we are in a git sandbox: get its "root"
				root_dir = repo.working_tree_dir
				print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
				print("processing git repository rooted at", end=' ')
				print(Style.BRIGHT + "'" + root_dir + "'", end=':\n')
			except git_exception.InvalidGitRepositoryError as e:
				# Not a git repo: no more options left
				print(Style.BRIGHT + Fore.YELLOW + "WARNING:", end=' ')
				print("Current dir " + Style.BRIGHT + "'" + base_path + "'", end=' ')
				print("is not within a valid git sandbox.")
				sys.exit(errno.ENOENT)
				
		# Load the "root" subrepos file (if any)
		subrepos = self.__load_subrepos_file(root_dir)
		if not subrepos:
			print(Style.BRIGHT + Fore.YELLOW + "WARNING:", end=' ')
			print("Couldn't find any", end=' ')
			print(Style.BRIGHT + "'" + SUBREPOS_FILE + "'", end=' ')
			print("file... exiting.")
			sys.exit(errno.ENOENT)
			
		# Recursively work on subrepos' contents
		while len(subrepos):
			current_subrepo = subrepos[0]
			current_subrepo['relpath'] = current_subrepo['path'].replace(root_dir + '/', '')
			
			# Operates on the current subrepo as requested
			current_subrepo = self.__process_subrepo(current_subrepo, report_only)
			
			# Prints subrepo status
			self.__print_subrepo_status(current_subrepo)
			
			# Let's see if new subrepos appeared and (eventually) append them to the queue
			new_subrepos = self.__load_subrepos_file(current_subrepo['path'])
			if new_subrepos:
				subrepos.extend(new_subrepos)
			
			# done with this subrepo entry
			subrepos.remove(current_subrepo)
		
		
	def __load_subrepos_file(self, path):
		"""
		Loads a 'subrepos' file at path.
		
		:param str path: the absolute path in which load a SUBREPOS_FILE (if any).
		:return list of dicts: list of dictionaries similar to the SUBREPOS_FILE one, or *None* if couldn't find it.
		
			* subrepo:
				* **subrepo['path']:** will be translated to an absolute path.
				* **subrepo['gitref_type']:** will be one of *'branch'*, *'tag'*, *'commit'*, or *None*.
				* **subrepo[gitref_type]:** (they will be named after the contents of *subrepo['gitref_type']*): the specific *gitref* value (a commit, branch or tag).
			* subrepo: (...)
		"""
		
		subrepos_file = path + "/" + SUBREPOS_FILE
		# Check if we can find here a 'subrepos' definition file
		try:
			with open(subrepos_file, 'r') as f_config:
				try:
					configMap = yaml.safe_load(f_config)
				except yaml.parser.ParserError as e:
					print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
					print(Style.BRIGHT + "Malformed YAML file", end=' - ')
					print(e)
					sys.exit(errno.EINVAL)
		except IOError as e:
			# it's acceptable not to find the requested 'subrepos' file.
			# we'll just return a null subrepo list as a result
			if e.errno==errno.ENOENT:
				configMap = None
			else: raise
		
		# Operate on the subrepos found
		if configMap:
			# Validate the subrepos file's contents
			if self.yaml_validator.validate(configMap):
				subrepo_list = configMap['subrepos']
				# "Normalize" the validated contents
				for subrepo in subrepo_list:
					# Let's set the repo's local path to its absolute location for easy tracking
					subrepo['path'] = path + '/' + subrepo['path']
					
					# Sets the type of the requested gitref to ease processing
					# Based on nice trick found at:
					# https://stackoverflow.com/questions/29201260/a-fast-way-to-find-the-number-of-elements-in-list-intersection-python
					# NOTE: the subrepos syntax insures that only one of ['branch', 'tag', 'commit'] will be found at most
					gitref_type = set(['branch', 'tag', 'commit']).intersection(subrepo)
					if gitref_type:
						subrepo['gitref_type'] = list(gitref_type)[0]
					else:
						subrepo['gitref_type'] = None
			else:
				print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
				print("Malformed YAML file at " + Style.BRIGHT + "'" + subrepos_file + "'", end='.\n')
				print("\t" + str(self.yaml_validator.errors))
				sys.exit(errno.EINVAL)
		else:
			subrepo_list = None
			
		return subrepo_list
		
		
	# TODO: Refactor this method, most possibly "breaking it" into steps:
	# 1. clone
	# 2. fetch (if no previous error)
	# 3. update (if no previous error and gitref mismatch)
	def __process_subrepo(self, subrepo, report_only=True):
		'''
		Operates the requested subrepo.
		
		:param dict subrepo:  a dictionary in the form returned by __load_subrepos_file()
		:param bool report_only: when True, only reviews subrepo's current status.  When False, tries to honor the requested values of *subrepo*.
		:return dict: an "enhanced" subrepo dict reporting its status.  It will add the following keys:
		
			* **subrepo['status']:** one of *'ERROR'*, *'NOT_CLONED'*, *'CLONED'*, *'EMPTY'*, *'UPDATED'*, *'PENDING_UPDATE'*, *'DIRTY'* or *'UP_TO_DATE'*.
		'''
		
		# find or clone given subrepo
		try:
			repo = Repo(subrepo['path'])
		except git_exception.NoSuchPathError as e:
			# repo not yet cloned
			if report_only:
				subrepo['status'] = 'NOT_CLONED'
			else:
				try:
					if subrepo['gitref_type']:
						gitref_type = subrepo['gitref_type']
						repo = Repo.clone_from(subrepo['repo'], subrepo['path'], branch=subrepo[gitref_type])
					else:
						repo = Repo.clone_from(subrepo['repo'], subrepo['path'])
				except git_exception.GitCommandError as e:
					if (
						e.status == 128
						and 'Could not read from remote repository' in e.stderr
					):
						subrepo['status'] = 'ERROR'
						subrepo['extra_info'] = e.stderr.replace('stderr: ','').strip('\n').strip()
					else:
						print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
						print(Style.BRIGHT + e.stderr.strip(' \t\n\r'))
						sys.exit(errno.EBADE)
				else:
					subrepo['status'] = 'CLONED'
		except git_exception.InvalidGitRepositoryError as e:
			# directory exists but, for whatever reason, is not a valid repo
			my_error_msg =  "directory '" + subrepo['path'] + "' exists, but it's not a valid git sandbox."
			my_error_msg += "\n\tPlease, review its contents."
			subrepo['status'] = 'ERROR'
			subrepo['extra_info'] = my_error_msg
				
		# Update sandbox if requested, needed and possible
		if (
			not report_only
			and (
				not 'status' in subrepo
				or subrepo['status'] != 'ERROR'
			)
		):
			# "names I'm using here:
			# local_commit: the current local commit on the sandbox
			# desired_gitref: what's requested? a tag, a branch, a commit...
			# desired_commit: the "topmost" commit on the desired_gitref
			# since I "converted" the desired_gitref into a commit,
			# I can just compare sandbox' current commit with the desired one to know if there're pending updates
			try:
				local_commit = repo.commit().hexsha
			except ValueError as e:
				if (
					"Reference at 'refs/heads/master' does not exist" in str(e)
					or "Reference at 'refs/heads/main' does not exist" in str(e)
				):
					# Remote repo exists, but it's still "un-intialized" (lacks its first commit)
					subrepo['status'] = 'EMPTY'
				else:
					raise e
				
			# grab details about remote updates (if any)
			try:
				repo.remotes.origin.fetch()
			except git_exception.GitCommandError as e:
				if (
					e.status == 128
					and 'Could not read from remote repository' in e.stderr
				):
					subrepo['status'] = 'ERROR'
					subrepo['extra_info'] = e.stderr.replace('stderr: ','').strip('\n').strip()
				else:
					print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
					print(Style.BRIGHT + e.stderr.strip('\n'))
					sys.exit(errno.EBADE)
					
			# Find the "new" topmost commit
			if (
				not 'status' in subrepo
				or (
					subrepo['status'] != 'ERROR'
					and subrepo['status'] != 'EMPTY'
				)
			):
				if subrepo['gitref_type']:
					gitref_type = subrepo['gitref_type']
					
					desired_gitref = subrepo[gitref_type]
					
					if gitref_type == 'branch':
						remote_ref = str('origin/' + subrepo[gitref_type])
					else:
						remote_ref = str(subrepo[gitref_type])
					
					try:
						desired_commit = str(repo.commit(remote_ref))
					except git_exception.BadName as e:
						print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
						print("Repo " + Style.BRIGHT + "'" + subrepo['repo'] + "'")
						print("\tCloned at: " + Style.BRIGHT + "'" + subrepo['path'] + "'")
						print("\tNo such " + gitref_type + ": " + Style.BRIGHT + "'" + subrepo[gitref_type] + "'", end=': ')
						print(e)
						sys.exit(errno.ENOENT)
				else:
					desired_commit = repo.remotes.origin.refs.HEAD.commit.hexsha
					desired_gitref = repo.git.symbolic_ref('refs/remotes/origin/HEAD').replace('refs/remotes/origin/','')
					
				# The sandbox update itself
				if local_commit != desired_commit:
					subrepo['from'] = local_commit
					subrepo['to'] = desired_commit
					
					if not repo.is_dirty():
						if not report_only:
							try:
								repo.git.checkout(desired_gitref)
							except git_exception.GitCommandError as e:
								print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
								print(Style.BRIGHT + "'" + subrepo['repo'] + "'")
								print("\tat " + Style.BRIGHT + "'" + subrepo['path'] + "'")
								print(Style.BRIGHT + "\t" + e.stderr.strip())
								sys.exit(errno.EBADE)
								
							if not repo.head.is_detached:
								repo.git.pull()
								
							subrepo['status'] = 'UPDATED'
						else:
							subrepo['status'] = 'PENDING_UPDATE'
					else:
						subrepo['status'] = 'DIRTY'
				else:
					subrepo['status'] = 'UP_TO_DATE'
					
		return subrepo
		
		
	def __print_subrepo_status(self, subrepo):
		'''prints a report on the repo info provided as param.
		
		:param dict subrepo: a dictionary in the enhanced form returned by __process_subrepo()
		'''
		
		# Header
		print(Style.BRIGHT + "'" + subrepo['relpath'] + "/'")
		print("\trepository:", end=' ')
		print(Style.BRIGHT + "'" + subrepo['repo'] + "'")
		if subrepo['gitref_type']:
			gitref_type = subrepo['gitref_type']
			print("\trequested " + gitref_type + ":", end=' ')
			print(Style.BRIGHT + "'" + subrepo[gitref_type] + "'")
		else:
			print("\tno gitref requested (working on default repo branch)")
			
		# Details depending on refered status
		if subrepo['status'] == 'ERROR':
			print("\tstatus:", end=' ')
			print(Style.BRIGHT + Fore.RED + "ERROR")
			if 'extra_info' in subrepo:
				print("\textra info:", end=' ')
				print(Style.BRIGHT + subrepo['extra_info'].replace('\n','\n\t\t'))
			
		elif subrepo['status'] == 'NOT_CLONED':
			print("\tstatus: " + Style.BRIGHT + Fore.YELLOW + "NOT YET CLONED")
			
		elif subrepo['status'] == 'CLONED':
			print("\tstatus:", end=' ')
			print(Style.BRIGHT + Fore.GREEN + "CLONED")
			
		elif subrepo['status'] == 'EMPTY':
			print("\tstatus:", end=' ')
			print(Style.BRIGHT + Fore.YELLOW + "REMOTE REPO NOT YET INITIALIZED")
			
		elif subrepo['status'] == 'UP_TO_DATE':
			print("\tstatus:", end=' ')
			print(Style.BRIGHT + Fore.GREEN + "UP TO DATE")
			
		elif subrepo['status'] == 'PENDING_UPDATE':
			print("\tpending updates:", end=' ')
			print(Style.BRIGHT + "'" + subrepo['from'] + "'", end=' -> ')
			print(Style.BRIGHT + "'" + subrepo['to'] + "'")
			
		elif subrepo['status'] == 'UPDATED':
			print("\tupdated from", end=' ')
			print(Style.BRIGHT + "'" + subrepo['from'] + "'", end=' -> ')
			print(Style.BRIGHT + "'" + subrepo['to'] + "'")
			
		elif subrepo['status'] == 'DIRTY':
			print("\tstatus:", end=' ')
			print(Style.BRIGHT + Fore.YELLOW + "DIRTY", end=' ')
			print("(won't try to update)")
			
		else:
			print("\tstatus: " + Style.BRIGHT + subrepo['status'])
		
		
if __name__ == '__main__':
	# execute only if run as a script
	main()
