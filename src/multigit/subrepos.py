# -*- coding: utf-8 -*-
"""
Processes subrepos files
"""

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

class Subrepos(object):
	
	def __init__(self):
		# Activates colored output
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
		Processes on information from subrepos
		'''
		'''
		Loops over the requested subrepos, operating them as needed
		report_only=False: processes the requirements; True, just shows status
		'''
		
		# First, let's check if we are in a git sandbox at all
		try:
			repo = Repo(base_path, search_parent_directories=True)
			# we are in a git sandbox: get its "root"
			root_dir = repo.working_tree_dir
			print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
			print("processing git repository rooted at", end=' ')
			print(Style.BRIGHT + "'" + root_dir + "'", end=':\n')
		except git_exception.InvalidGitRepositoryError as e:
			# Not a git repo (acceptable, we'll just process the requested dir as-is)
			root_dir = base_path
			print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
			print("Current dir " + Style.BRIGHT + "'" + root_dir + "'", end=' ')
			print("is not within a valid git sandbox.")
			
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
		'''
		Loads a 'subrepos' file at path
		'''
		
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
		
		
	def __process_subrepo(self, subrepo, report_only=True):
		'''
		Operates the requested subrepo
		It returns and "enhanced" subrepo dict reporting its status
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
					print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
					print(Style.BRIGHT + e.stderr.strip('\n'))
					sys.exit(errno.EBADE)
					
				subrepo['status'] = 'CLONED'
				
		# Update sandbox if requested, needed and possible
		if not 'status' in subrepo:
			current_commit = repo.commit().hexsha
			repo.remotes.origin.fetch()
		
			# Find the "new" topmost commit
			if subrepo['gitref_type']:
				gitref_type = subrepo['gitref_type']
				if gitref_type == 'branch':
					try:
						desired_commit = str(repo.commit('origin/' + subrepo['branch']))
					except git_exception.BadName as e:
						print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
						print("Repo " + Style.BRIGHT + "'" + subrepo['repo'] + "'")
						print("\tCloned at: " + Style.BRIGHT + "'" + subrepo['path'] + "'")
						print("\tNo such branch: " + Style.BRIGHT + "'" + subrepo['branch'] + "'", end=': ')
						print(e)
						sys.exit(errno.ENOENT)
						
					gitref = subrepo['branch']
				elif gitref_type == 'tag':
					try:
						desired_commit = str(repo.commit(subrepo['tag']))
					except git_exception.BadName as e:
						print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
						print("Repo " + Style.BRIGHT + "'" + subrepo['repo'] + "'")
						print("\tCloned at: " + Style.BRIGHT + "'" + subrepo['path'] + "'")
						print("\tNo such tag: " + Style.BRIGHT + "'" + subrepo['tag'] + "'", end=': ')
						print(e)
						sys.exit(errno.ENOENT)
						
					gitref = subrepo['tag']
				elif gitref_type == 'commit':
					desired_commit = str(subrepo['commit'])
					gitref = subrepo['commit']
			else:
				desired_commit = repo.remotes.origin.refs.HEAD.commit.hexsha
				gitref = repo.git.symbolic_ref('refs/remotes/origin/HEAD').replace('refs/remotes/origin/','')
				
			# The sandbox update itself
			if current_commit != desired_commit:
				subrepo['from'] = current_commit
				subrepo['to'] = desired_commit
				if not repo.is_dirty():
					if not report_only:
						try:
							repo.git.checkout(gitref)
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
		'''
		prints a report on the repo info provided as param
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
		if subrepo['status'] == 'NOT_CLONED':
			print("\tstatus: " + Style.BRIGHT + "not yet cloned")
			
		elif subrepo['status'] == 'CLONED':
			print("\tstatus:", end=' ')
			print(Style.BRIGHT + Fore.GREEN + "CLONED")
			
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
		
		