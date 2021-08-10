# -*- coding: utf-8 -*-
"""
Processes a single "subrepos" definition file
"""

# Import stuff
import errno, sys
import importlib.resources as pkg_resources
import yaml
from cerberus import Validator, schema

from colorama import init, Fore, Back, Style
#Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: DIM, NORMAL, BRIGHT, RESET_ALL

# "local" imports

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


class SubreposFile(object):
	
	def __init__(self):
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
				or type(e) is TypeError):
				print("\t" + str(e))
				sys.exit(errno.EINVAL)
			else:
				raise
		
		
	def load(self, subrepos_path):
		'''
		Loads a 'subrepos' file at 'subrepos_path'
		'''
		
		subrepo_list = []
		subrepos_file = subrepos_path + "/" + SUBREPOS_FILE
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
		
		# Operate on the subrepos found
		if configMap:
			# Validate the subrepos file's contents
			if self.yaml_validator.validate(configMap):
				subrepo_list = configMap['subrepos']
				# Process the validated contents
				for subrepo in subrepo_list:
					# Let's set the repo's local path to its absolute location for easier tracking
					subrepo['path'] = subrepos_path + '/' + subrepo['path']
			else:
				print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
				print("Malformed YAML file at " + Style.BRIGHT + "'" + subrepos_file + "'", end='.\n')
				print("\t" + str(self.yaml_validator.errors))
				sys.exit(errno.EINVAL)
				
		return subrepo_list
	
