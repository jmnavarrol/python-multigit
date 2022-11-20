# -*- coding: utf-8 -*-

# Import stuff
import errno, os, sys
import importlib.resources as pkg_resources
import yaml
from cerberus import Validator, schema

from colorama import init, Fore, Back, Style
#Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: DIM, NORMAL, BRIGHT, RESET_ALL


class Subrepofile(object):
	'''Process a subrepo file into a "valid" dictionary'''
	
	def __init__(self):
		'''Loads the YAML schema validator'''
		
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
	
	
	def load(self, subrepos_file):
		'''
		Loads a subrepos file at path.
		
		:param str subrepos_file: absolute path to subrepos file
		:return list of dicts: list of dictionaries similar to the SUBREPOS_FILE one, or *None* if couldn't find it.
		
			* subrepo:
				* **subrepo['path']:** will be translated to an absolute path.
				* **subrepo['gitref_type']:** will be one of *'branch'*, *'tag'*, *'commit'*, or *None*.
				* **subrepo[gitref_type]:** (they will be named after the contents of *subrepo['gitref_type']*): the specific *gitref* value (a commit, branch or tag).
			* subrepo: (...)
		'''
		
		try:
			with open(subrepos_file, 'r') as f_config:
				try:
					configMap = yaml.safe_load(f_config)
				except yaml.parser.ParserError as e:
					print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
					print(Style.BRIGHT + "Malformed YAML file", end=' - ')
					print(e)
					sys.exit(errno.EINVAL)
		except PermissionError as e:
			print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
			print('trying to load', end=' ')
			print(Style.BRIGHT + "'" + subrepos_file + "'", end=':\n')
			print("\t" + str(e))
			sys.exit(errno.EPERM)
				
		# Operates on the subrepos found
		if configMap:
			# Validate the subrepos file's contents
			if self.yaml_validator.validate(configMap):
				subrepo_list = configMap['subrepos']
				# "Normalize" the validated contents
				for subrepo in subrepo_list:
					# Let's set the repo's local path to its absolute location for easy tracking
					subrepo['path'] = os.path.join(
						os.path.dirname(os.path.realpath(subrepos_file)),
						subrepo['path']
					)
					
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
	
	
if __name__ == '__main__':
	# execute only if run as a script
	main()
