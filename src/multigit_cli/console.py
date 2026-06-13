# -*- coding: utf-8 -*-

"""Console rendering module for multigit CLI.

Provides formatted console output using colorama for terminal colours.
"""

from colorama import init, Fore, Back, Style
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL


def init_console():
	'''Activates coloured output'''
	init(autoreset=True)


def print_subrepo_status(subrepo):
	'''Prints a report on the repo info provided as param.
	
	:param dict subrepo: a dictionary with status information for a repository
	'''
	
	# Header
	print(Style.BRIGHT + "'" + subrepo['path'] + "':")
	print("\trepository:", end=' ')
	print(Style.BRIGHT + "'" + subrepo['repo'] + "'")
	if subrepo.get('gitref_type'):
		gitref_type = subrepo['gitref_type']
		print("\trequested " + gitref_type + ":", end=' ')
		print(Style.BRIGHT + "'" + subrepo[gitref_type] + "'")
	else:
		print("\tno gitref requested (working on default repo branch)")
		
	# Details depending on referred status
	if subrepo['status'] == 'ERROR':
		print("\tstatus:", end=' ')
		print(Style.BRIGHT + Fore.RED + "ERROR")
		if 'extra_info' in subrepo:
			print("\textra info:", end=' ')
			print(Style.BRIGHT + subrepo['extra_info'].replace('\n','\n\t\t'))
		
	elif subrepo['status'] == 'WRONG_REMOTE':
		print("\tstatus: " + Style.BRIGHT + Fore.YELLOW + "REPO POINTS TO A WRONG REMOTE")
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
		print(Style.BRIGHT + Fore.YELLOW + "REMOTE REPO NOT YET INITIALISED")
		
	elif subrepo['status'] == 'UP_TO_DATE':
		print("\tstatus:", end=' ')
		print(Style.BRIGHT + Fore.GREEN + "UP TO DATE")
		
	elif subrepo['status'] == 'PENDING_UPDATE':
		print("\tstatus:", end=' ')
		print(Style.BRIGHT + Fore.YELLOW + "PENDING UPDATES")
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
