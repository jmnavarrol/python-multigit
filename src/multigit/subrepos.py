# -*- coding: utf-8 -*-

# Import stuff
import errno, os, sys
from git import Repo, exc as git_exception

from colorama import init, Fore, Back, Style
#Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: DIM, NORMAL, BRIGHT, RESET_ALL

# "local" imports
from .gitrepo import Gitrepo
from .subrepofile import Subrepofile, SubrepofileError

class Subrepos(object):
	'''Recursively reads subrepos files and runs git commands as per its findings'''
	
	def __init__(self):
		'''Activates colored output'''
		init(autoreset=True)
		
		
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
			print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
			print("no valid ", end=' ')
			print(Style.BRIGHT + "'" + subrepos_filename + "'", end=' found at ')
			print(Style.BRIGHT + "'" + base_path + "'", end='.\n')
			# No subrepos file found at current path. Let's check if we are within a git sandbox
			try:
				repo = Repo(base_path, search_parent_directories=True)
				# we are in a git sandbox: get its "root"
				root_dir = repo.working_tree_dir
				print(Style.BRIGHT + Fore.GREEN + "INFO:", end=' ')
				print("processing git repository rooted at", end=' ')
				print(Style.BRIGHT + "'" + root_dir + "'", end=':\n')
				
				if os.path.isfile(os.path.join(root_dir, subrepos_filename)):
					subrepos_file = os.path.realpath(
						os.path.join(root_dir, subrepos_filename)
					)
			except git_exception.InvalidGitRepositoryError as e:
				# Not a git repo: no more options left
				print(Style.BRIGHT + Fore.YELLOW + "WARNING:", end=' ')
				print("Current dir " + Style.BRIGHT + "'" + base_path + "'", end=' ')
				print("is not within a valid git sandbox.")
			
		# Let's see if we found a valid subrepos 'entry point'
		try:
			subrepos_file
		except NameError:
			print(Style.BRIGHT + Fore.RED + "ERROR:", end=' ')
			print("Couldn't find any", end=' ')
			print(Style.BRIGHT + "'" + subrepos_filename + "'", end=' ')
			print("file... exiting.")
			sys.exit(errno.ENOENT)
		
		subrepo = Subrepofile()
		try:
			subrepos = subrepo.load(subrepos_file)
		except SubrepofileError as e:
			err_msg = f"{Style.BRIGHT}{Fore.RED}ERROR:{Style.RESET_ALL} ({os.strerror(e.errno)}) "
			err_msg += f"{e}"
			print(err_msg)
			sys.exit(e.errno)
				
		if not subrepos:
			print(Style.BRIGHT + Fore.YELLOW + "WARNING:", end=' ')
			print("Couldn't find any", end=' ')
			print(Style.BRIGHT + "'" + subrepos_filename + "'", end=' ')
			print("file... exiting.")
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
			self.__print_subrepo_status(current_subrepo)
			
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
		
		
	def __print_subrepo_status(self, subrepo):
		'''prints a report on the repo info provided as param.
		
		:param dict subrepo: a dictionary in the enhanced form returned by __process_subrepo()
		'''
		
		# Header
		print(Style.BRIGHT + "'" + subrepo['path'] + "':")
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
			print(Style.BRIGHT + Fore.YELLOW + "REMOTE REPO NOT YET INITIALIZED")
			
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
		
		
if __name__ == '__main__':
	# execute only if run as a script
	sys.exit(
		main()
	)
