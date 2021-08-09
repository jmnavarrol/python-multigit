# -*- coding: utf-8 -*-
"""
Processes a single "subrepos" definition file
"""

# Import stuff
import errno, sys
import yaml

from colorama import init, Fore, Back, Style
#Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: DIM, NORMAL, BRIGHT, RESET_ALL


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
	
	@staticmethod
	def load(subrepos_path):
		'''
		Loads a 'subrepos' file at 'subrepos_path'
		'''
		
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
		
		# 'subrepos' file found: validate and load its contents
		subrepo_list = []
		if configMap:
			try:
				subrepo_list = configMap['subrepos']
			except KeyError as e:
				print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
				print(Style.BRIGHT + "'" + subrepos_file + "'", end='\n')
				print('\tMandatory key ' + Style.BRIGHT + "'subrepos'", end=' ')
				print("couldn't be found!")
				sys.exit(errno.ENOENT)
				
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
				subrepo['path'] = subrepos_path + '/' + subrepo['path']
				
		return subrepo_list
	
