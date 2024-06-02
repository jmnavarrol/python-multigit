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
						raise SubrepofileError(
							f"Malformed schema file 'subrepos_schema.yaml' - {e}",
							errno = errno.EINVAL,
						)
		except FileNotFoundError as e:
			raise SubrepofileError(
				f"trying to access subrepos file '{subrepos_file}':\n{e}",
				errno = errno.ENOENT,
			)
			
		try:
			self.yaml_validator = Validator(yaml_rules)
		except (schema.SchemaError, TypeError) as e:
			raise SubrepofileError(
				f"in YAML schema validator at '{validator_resource}'.\n\t{e}",
				errno = errno.EINVAL
			)
	
	
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
				except (
					yaml.scanner.ScannerError,
					yaml.parser.ParserError,
				) as e:
					raise SubrepofileError(
						f"malformed YAML in subrepos file '{subrepos_file}':\n{e}",
						errno = errno.EINVAL,
					)
		except PermissionError as e:
			raise SubrepofileError(
				f"trying to load '{subrepos_file}'\n\t{e}",
				errno = errno.EPERM
			)
				
		# Operates on the subrepos found
		if configMap:
			# Validate the subrepos file's contents
			if self.yaml_validator.validate(configMap):
				subrepo_list = configMap['subrepos']
				# "Normalize" the validated contents
				for subrepo in subrepo_list:
					# Let's set the repo's local path to its absolute location for easy tracking
					subrepo['path'] = os.path.realpath(
						os.path.join(
							os.path.dirname(subrepos_file),
							subrepo['path']
						)
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
				err_msg = f"malformed YAML in subrepos file '{subrepos_file}':\n"
				err_msg += f"\t{self.yaml_validator.errors}"
				raise SubrepofileError(
					err_msg,
					errno = errno.EINVAL,
				)
		else:
			subrepo_list = None
			
		return subrepo_list
	
	
class SubrepofileError(Exception):
	'''
	Custom Subrepofile Error Exception
	
	:param str msg: absolute path to subrepos file
	:param errno errno: suggested sys.exit errno
	'''
	
	def __init__(self, msg='error while operating subrepo file', errno=errno.EINVAL, *args, **kwargs):
		super().__init__(msg, *args, **kwargs)
		self.errno = errno
		

if __name__ == '__main__':
	# execute only if run as a script
	main()
