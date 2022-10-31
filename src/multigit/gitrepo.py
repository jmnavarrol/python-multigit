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
		:return: returns the same repoconf dictionary provided as parameter with a new 'status' key populated.
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
			
		return repostatus
	
	
	def update(self, repoconf):
		'''
		Updates a repo entry as per its current state.
		
		:param repoconf: the configuration dictionary of the git repository to be processed.
		:return: returns the same repoconf dictionary provided as parameter with a new 'status' key populated after update process.
		'''
		
		repostatus = repoconf
		# First, let's check the repository's current status
		repostatus = self.status(repoconf)
		
		# Then, let's operate on the repository depending on its status
		if repostatus['status'] == 'ERROR':
			pass
		elif repostatus['status'] == 'NOT_CLONED':
			# Let's try to clone it
			if repostatus['gitref_type']:
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
		
		return repostatus
		
		
if __name__ == '__main__':
	# execute only if run as a script
	main()
