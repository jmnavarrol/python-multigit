# -*- coding: utf-8 -*-

# Import stuff
import sys
from git import Repo, exc as git_exception


class Gitrepo(object):
	'''Processes a single git repo entity as defined by multigit.'''
	
	def __init__(self):
		pass
		
		
	def status(self, repoconf):
		'''
		Finds the status of the repo configuration that gets as param.
		
		:param repoconf: the configuration dictionary of the git repository to be processed.
		:return: returns the same repoconf dictionary provided as parameter with a new 'status' key populated and, optionally a 'extra_info' key.
		'''
		
		#print(str(repoconf))
		repostatus = repoconf
		repostatus['status'] = 'UNPROCESSED'
		if not 'gitref_type' in repostatus:
			repostatus['gitref_type'] = None
		
		# Let's check if it's at least cloned
		try:
			repo = Repo(repoconf['path'])
		except git_exception.NoSuchPathError as e:
			# repo not yet cloned
			repostatus['status'] = 'NOT_CLONED'
		except git_exception.InvalidGitRepositoryError as e:
			# directory exists but, for whatever reason, is not a valid repo
			repostatus['status'] = 'ERROR'
			my_error_msg =  "directory '" + repostatus['path'] + "' exists, but it's not a valid git sandbox."
			my_error_msg += "\n\tPlease, review its contents."
			repostatus['extra_info'] = my_error_msg
			
		# if still unprocessed it's because the repo is there
		# Check remotes
		if repostatus['status'] == 'UNPROCESSED':
			if repostatus['repo'] != repo.remotes.origin.url:
				repostatus['status'] = 'WRONG_REMOTE'
				my_error_msg = "Requested remote is '" + repostatus['repo'] + "' "
				my_error_msg += "but current origin is '" + repo.remotes.origin.url + "'."
				repostatus['extra_info'] = my_error_msg
			
		# if still unprocessed it's because the repo is there and the remote is right
		# Let's try to update its status
		if repostatus['status'] == 'UNPROCESSED':
			try:
				repo.git.fetch(prune=True)
			except git_exception.GitCommandError as e:
				if e.status == 128:
					repostatus['status'] = 'ERROR'
					repostatus['extra_info'] = e.stderr.replace('stderr: ','').strip('\n').strip()
				else:
					raise
			
		if repostatus['status'] == 'UNPROCESSED':
			try:
				local_commit = repo.commit().hexsha
			except ValueError as e:
				if (
					"Reference at 'refs/heads/master' does not exist" in str(e)
					or "Reference at 'refs/heads/main' does not exist" in str(e)
				):
					# Remote repo exists, but it's still "un-initialized" (lacks its first commit)
					repostatus['status'] = 'EMPTY'
				else:
					raise e
				
		# if still unprocessed, it's a good repo.
		# can it be updated?
		if repostatus['status'] == 'UNPROCESSED':
			if repo.is_dirty():
				repostatus['status'] = 'DIRTY'
				
		# is the proper gitref already checked out?
		if repostatus['status'] == 'UNPROCESSED':
			# print(str(repo))
			if (
				'gitref_type' in repostatus
				and repostatus['gitref_type'] is not None
			):
				if repostatus['gitref_type'] == 'branch':
					if repo.head.is_detached:
						repostatus['status'] = 'PENDING_UPDATE'
						repostatus['from'] = repo.commit().hexsha
						repostatus['to'] = repostatus['branch']
					elif repo.head.ref.name != repostatus['branch']:
						repostatus['status'] = 'PENDING_UPDATE'
						repostatus['from'] = repo.head.ref.name
						repostatus['to'] = repostatus['branch']
			else:
				# default branch requested
				# find its remote name (i.e. 'origin/master')
				remote_head = next(ref for ref in repo.remotes.origin.refs if '/HEAD' in ref.name).ref.name
				# ...and convert to a proper local name (i.e. 'master')
				default_branch = remote_head.split('/', 1)[-1]
				if repo.head.is_detached:
					repostatus['status'] = 'PENDING_UPDATE'
					repostatus['from'] = repo.commit().hexsha
					repostatus['to'] = default_branch
				elif default_branch != repo.head.ref.name:
					repostatus['status'] = 'PENDING_UPDATE'
					repostatus['from'] = repo.head.ref.name
					repostatus['to'] = default_branch
					
		# Let's check its current commit vs the remote one
		if repostatus['status'] == 'UNPROCESSED':
			if (
				'gitref_type' in repostatus
				and repostatus['gitref_type'] is not None
			):
				gitref_type = repostatus['gitref_type']
				desired_gitref = repostatus[gitref_type]
				if gitref_type == 'branch':
					remote_ref = str('origin/' + repostatus[gitref_type])
				else:
					remote_ref = str(repostatus[gitref_type])
				try:
					desired_commit = str(repo.commit(remote_ref))
				except git_exception.BadName as e:
					if ("Ref '" + remote_ref + "' did not resolve to an object" in str(e)):
						# The requested gitref doesn't exist at the remote end (for whatever reason)
						desired_commit = None  # ...so no desired commit possible
						repostatus['status'] = 'WRONG_REMOTE'
						repostatus['extra_info'] = "It seems you requested a gitref that can't be found on remote.\n"
						repostatus['extra_info'] += str(e)
					else:
						raise e
			else:
				desired_commit = repo.remotes.origin.refs.HEAD.commit.hexsha
				desired_gitref = repo.git.symbolic_ref('refs/remotes/origin/HEAD').replace('refs/remotes/origin/','')
				
			if (desired_commit and local_commit != desired_commit):
				repostatus['status'] = 'PENDING_UPDATE'
				repostatus['from'] = local_commit
				repostatus['to'] = desired_commit
				
		# if still unprocessed, it's up to date
		if repostatus['status'] == 'UNPROCESSED':
			repostatus['status'] = 'UP_TO_DATE'
			
		return repostatus
	
	
	def update(self, repoconf):
		'''
		Updates a repo entry as per its current state.
		
		:param repoconf: the configuration dictionary of the git repository to be processed.
		:return: returns the same repoconf dictionary provided as parameter with a new 'status' key populated after update process and, optionally, a 'extra_info' key.
		'''
		
		# First, let's check the repository's current status
		repostatus = self.status(repoconf)
		# print(repostatus)
		
		# Then, let's operate on the repository depending on its status
		if (
			# all these are statuses we can't deal with here
			repostatus['status'] == 'ERROR'
			or repostatus['status'] == 'UP_TO_DATE'
			or repostatus['status'] == 'EMPTY'
			or repostatus['status'] == 'DIRTY'
			or repostatus['status'] == 'WRONG_REMOTE'
		):
			pass
		elif repostatus['status'] == 'NOT_CLONED':
			# Let's try to clone it:
			# you can `git clone` or `git clone --branch` (which can take either branch or tag but **not** a commit)
			# in case a specific commit is requested, first "bare" clone, then move to the requested commit.
			try:
				if (
					repostatus['gitref_type'] == 'branch'
					or repostatus['gitref_type'] == 'tag'
				):
					gitref_type = repostatus['gitref_type']
					repo = Repo.clone_from(
						url     = repostatus['repo'],
						to_path = repostatus['path'],
						branch  = repostatus[gitref_type],
					)
				else:
					repo = Repo.clone_from(
						url     = repostatus['repo'],
						to_path = repostatus['path'],
					)
					if repostatus['gitref_type'] == 'commit':
						repo.git.checkout(repostatus['commit'])
						
				repostatus['status'] = 'CLONED'
			except git_exception.GitCommandError as e:
				if e.status == 128:
					repostatus['status'] = 'ERROR'
					repostatus['extra_info'] = e.stderr.replace('stderr: ','').strip('\n').strip()
				else:
					raise
		elif repostatus['status'] == 'PENDING_UPDATE':
			repo = Repo(repostatus['path'])
			repo.git.fetch(prune=True)
			
			if (
				'gitref_type' in repostatus
				and repostatus['gitref_type'] is not None
			):
				gitref_type = repostatus['gitref_type']
				desired_gitref = repostatus[gitref_type]
				
				if gitref_type == 'branch':
					remote_ref = str('origin/' + repostatus[gitref_type])
				else:
					remote_ref = str(repostatus[gitref_type])
			else:
				desired_gitref = repo.git.symbolic_ref('refs/remotes/origin/HEAD').replace('refs/remotes/origin/','')
				
			try:
				repo.git.checkout(desired_gitref)
			except git_exception.GitCommandError as e:
				repostatus['status'] = 'ERROR'
				repostatus['extra_info'] = str(e)
				
			if not repo.head.is_detached:
				try:
					repo.git.pull()
				except git_exception.GitCommandError as e:
					repostatus['status'] = 'ERROR'
					repostatus['extra_info'] = e.stderr.replace('stderr: ','').strip('\n').strip()
				
			if repostatus['status'] != 'ERROR':
				repostatus['status'] = 'UPDATED'
			
		return repostatus
	
	
if __name__ == '__main__':
	# execute only if run as a script
	sys.exit(
		main()
	)
