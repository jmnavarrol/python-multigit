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
		
		
	def process(self, base_path):
		# First, let's check if we are in a git sandbox at all
		working_dir = self.__find_root(base_path)
		subrepos = self.__load_subrepos(working_dir)
		
		# Recursively work on findings
		while len(subrepos):
			# Operates (clone, update...) the first subrepo on the list
			self.__process_subrepo(subrepos[0])
			# See if new subrepos did appear
			new_subrepos = self.__load_subrepos(subrepos[0]['path'])
			# done with this subrepo entry
			subrepos.remove(subrepos[0])
			
			# Now, let's add new findings to the queue (if any)
			if new_subrepos:
				subrepos.extend(new_subrepos)
		 
		
	def __find_root(self, base_path):
		'''
		Returns the root path or the current git repo, or itself, if 'path' is not within a git sandbox
		'''
		
		try:
			repo = Repo(base_path, search_parent_directories=True)
			# we are in a git sandbox: return its "root"
			base_path = repo.working_tree_dir
		except git_exception.InvalidGitRepositoryError as e:
			# Not a git repo
			print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
			print("Current dir " + Style.BRIGHT + "'" + base_path + "'", end=' ')
			print("is not within a valid git sandbox.")
			print("\tLooking for a " + Style.BRIGHT + "'"  + SUBREPOS_FILE + "'", end=' ')
			print("file right here instead.")
		
		return base_path
	
	
	def __load_subrepos(self, path):
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
		
		# Find the "new" topmost commit
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
		
		
