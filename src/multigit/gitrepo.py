# -*- coding: utf-8 -*-

# Import stuff
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
		
		repostatus = repoconf
		repostatus['status'] = 'UNPROCESSED'
		#print(str(repoconf))
		
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
			if (
				'gitref_type' in repostatus
				and repostatus['gitref_type'] is not None
			):
				if repostatus['gitref_type'] == 'branch':
					if repo.head.ref.name != repostatus['branch']:
						 repostatus['status'] = 'PENDING_UPDATE'
						 repostatus['from'] = repo.head.ref.name
						 repostatus['to'] = repostatus['branch']
			else:
				# default branch requested
				pass
			
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
					
				desired_commit = str(repo.commit(remote_ref))
			else:
				desired_commit = repo.remotes.origin.refs.HEAD.commit.hexsha
				desired_gitref = repo.git.symbolic_ref('refs/remotes/origin/HEAD').replace('refs/remotes/origin/','')
				
			if local_commit != desired_commit:
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
			# Let's try to clone it
			try:
				if (
					'gitref_type' in repostatus
					and repostatus['gitref_type'] is not None
				):
					gitref_type = repostatus['gitref_type']
					repo = Repo.clone_from(
						repostatus['repo'],
						repostatus['path'],
						branch=repostatus[gitref_type]
					)
				else:
					repo = Repo.clone_from(
						repostatus['repo'],
						repostatus['path']
					)
				
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
				repo.git.pull()
				
			if repostatus['status'] != 'ERROR':
				repostatus['status'] = 'UPDATED'
			
		return repostatus
	
	
if __name__ == '__main__':
	# execute only if run as a script
	main()
