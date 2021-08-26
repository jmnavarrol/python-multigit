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
		
		
	def process(self, base_path, report_only=False):
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
			working_dir = repo.working_tree_dir
			print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
			print("processing a git repository rooted at", end=' ')
			print(Style.BRIGHT + "'" + working_dir + "'", end='.\n')
		except git_exception.InvalidGitRepositoryError as e:
			# Not a git repo (acceptable, we'll just process the requested dir as-is)
			working_dir = base_path
			print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
			print("Current dir " + Style.BRIGHT + "'" + working_dir + "'", end=' ')
			print("is not within a valid git sandbox.")
			
		subrepos = self.__load_subrepos_file(working_dir)
		
		if not len(subrepos):
			print(Style.BRIGHT + Fore.YELLOW + "WARNING:", end=' ')
			print("Couldn't find any", end=' ')
			print(Style.BRIGHT + "'" + SUBREPOS_FILE + "'", end=' file.\n')
		else:
		# Recursively work on findings
			while len(subrepos):
				if not report_only:
					# Operates (clone, update...) the first subrepo on the list
					self.__process_subrepo(subrepos[0])
				else:
					relpath = subrepos[0]['path'].replace(working_dir + '/', '')
					print(Style.BRIGHT + "'" + relpath + "/'")
					print("\trepository:", end=' ')
					print(Style.BRIGHT + "'" + subrepos[0]['repo'] + "'")
				
					# Based on nice trick found at:
					# https://stackoverflow.com/questions/29201260/a-fast-way-to-find-the-number-of-elements-in-list-intersection-python
					# NOTE: the subrepos syntax insures only one of ['branch', 'tag', 'commit'] will be found
					gitref_type = set(['branch', 'tag', 'commit']).intersection(subrepos[0])
					if gitref_type:
						gitref_type = list(gitref_type)[0]
						print("\trequested " + gitref_type + ":", end=' ')
						print(Style.BRIGHT + "'" + subrepos[0][gitref_type] + "'")
					else:
						print("\tno gitref requested (working on default repo branch)")
					
				# See if new subrepos did appear
				new_subrepos = self.__load_subrepos_file(subrepos[0]['path'])
				# done with this subrepo entry
				subrepos.remove(subrepos[0])
				
				# Now, let's add new findings to the queue (if any)
				if new_subrepos:
					subrepos.extend(new_subrepos)
		
		
	def __load_subrepos_file(self, path):
		'''
		Loads a 'subrepos' file at path
		'''
		
		subrepo_list = []
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
			if e.errno==errno.ENOENT:
				configMap = None
			else: raise
		
		# Operate on the subrepos found
		if configMap:
			# Validate the subrepos file's contents
			if self.yaml_validator.validate(configMap):
				subrepo_list = configMap['subrepos']
				# Process the validated contents
				for subrepo in subrepo_list:
					# Let's set the repo's local path to its absolute location for easier tracking
					subrepo['path'] = path + '/' + subrepo['path']
			else:
				print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
				print("Malformed YAML file at " + Style.BRIGHT + "'" + subrepos_file + "'", end='.\n')
				print("\t" + str(self.yaml_validator.errors))
				sys.exit(errno.EINVAL)
				
		return subrepo_list
		
		
	def __process_subrepo(self, subrepo):
		# find or clone given subrepo
		try:
			repo = Repo(subrepo['path'])
		except git_exception.NoSuchPathError as e:
			# repo not yet cloned
			# Based on nice trick found at:
			# https://stackoverflow.com/questions/29201260/a-fast-way-to-find-the-number-of-elements-in-list-intersection-python
			# NOTE: the subrepos syntax insures only one of ['branch', 'tag'] will be found
			gitref_type = set(['branch', 'tag']).intersection(subrepo)
			try:
				if gitref_type:
					gitref_type = list(gitref_type)[0]
					repo = Repo.clone_from(subrepo['repo'], subrepo['path'], branch=subrepo[gitref_type])
				else:
					repo = Repo.clone_from(subrepo['repo'], subrepo['path'])
			except git_exception.GitCommandError as e:
				print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
				print(Style.BRIGHT + e.stderr.strip('\n'))
				sys.exit(errno.EBADE)
				
			print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
			print("Repo " + Style.BRIGHT + "'" + subrepo['repo'] + "'")
			print("\tCloned at " + Style.BRIGHT + "'" + subrepo['path'] + "'")
			
		# Update sandbox if needed and possible
		current_commit = repo.commit().hexsha
		repo.remotes.origin.fetch()
		
		# Find the "new" topmost commit
		if 'branch' in subrepo:
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
		elif 'tag' in subrepo:
			desired_commit = str(repo.commit(subrepo['tag']))
			gitref = subrepo['tag']
		elif 'commit' in subrepo:
			desired_commit = str(subrepo['commit'])
			gitref = subrepo['commit']
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
		
		
