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
		
		# Let's check if it's at least cloned
		try:
			repo = Repo(repoconf['path'])
		except git_exception.NoSuchPathError as e:
			# repo not yet cloned
			repostatus['status'] = 'NOT_CLONED'
			
		return repostatus
	
	
if __name__ == '__main__':
	# execute only if run as a script
	main()
