# -*- coding: utf-8 -*-
# Tests the Gitrepo class: remote operations
# TODO: to be seggregated into different files

# Import stuff
from .test_gitrepo import TestGitrepo

import os
from git import Repo

# Subclasses so it gets parent's setUp and tearDown
class TestGitrepoOther(TestGitrepo):
	
	def test_busy_dir(self):
		print("TEST: 'test_busy_dir'")
		# prepares a suitable configuration
		repoconf = {}
		repoconf['path'] = os.path.join(self.scenarios_path, 'standard')
		result = self.gitrepo.update(repoconf)
		print(str(result))
		self.assertEqual(result['status'], 'ERROR')
		
		
	def test_nonexitent_branch(self):
		print("TEST: 'test_nonexitent_branch'")
		# prepares a suitable configuration
		repoconf = {}
		repoconf['repo'] = 'git@github.com:jmnavarrol/simplest-git-subrepos.git'
		repoconf['path'] = os.path.join(self.scenarios_path, 'standard/simplest-git-subrepos')
		repoconf['branch'] = 'nonexistent'
		repoconf['gitref_type'] = 'branch'
		
		result = self.gitrepo.update(repoconf)
		print(str(result))
		self.assertEqual(result['status'], 'ERROR')
		
		
	def test_local_not_in_remote_same_branch(self):
		print("TEST: 'test_local_not_in_remote_same_branch'")
		# prepares a suitable configuration
		repoconf = {}
		repoconf['repo'] = 'git@github.com:jmnavarrol/simplest-git-subrepos.git'
		repoconf['path'] = os.path.join(self.scenarios_path, 'standard/simplest-git-subrepos')
		
		# First, let's clone the repo
		result = self.gitrepo.update(repoconf)
		print(str(result))
		# Then, let's create a local branch
		repo = Repo(repoconf['path'])
		new_branch = repo.create_head('new_branch')
		new_branch.checkout()
		# Finally, let's update config to request the new local branch
		repoconf['branch'] = 'new_branch'
		repoconf['gitref_type'] = 'branch'
		result = self.gitrepo.update(repoconf)
		print(str(result))
		self.assertEqual(result['status'], 'WRONG_REMOTE')
		
		
	def test_local_not_in_remote_different_branch(self):
		print("TEST: 'test_local_not_in_remote_different_branch'")
		# prepares a suitable configuration
		repoconf = {}
		repoconf['repo'] = 'git@github.com:jmnavarrol/simplest-git-subrepos.git'
		repoconf['path'] = os.path.join(self.scenarios_path, 'standard/simplest-git-subrepos')
		
		# First, let's clone the repo
		result = self.gitrepo.update(repoconf)
		print(str(result))
		# Then, let's create a local branch
		repo = Repo(repoconf['path'])
		new_branch = repo.create_head('new_branch')
		# Finally, let's update config to request the new local branch
		repoconf['branch'] = 'new_branch'
		repoconf['gitref_type'] = 'branch'
		result = self.gitrepo.update(repoconf)
		print(str(result))
		self.assertEqual(result['status'], 'ERROR')
		
		
	def test_status_not_cloned(self):
		print("TEST: 'test_status_not_cloned'")
		# prepares a suitable configuration
		repoconf = {}
		repoconf['path'] = os.path.join(self.scenarios_path, 'standard/empty-repo')
		
		result = self.gitrepo.status(repoconf)
		print(str(result))
		self.assertEqual(result['status'], 'NOT_CLONED')
		
		
	def test_status_unitialized(self):
		print("TEST: 'test_status_unitialized'")
		# prepares a suitable configuration
		repoconf = {}
		repoconf['repo'] = 'git@github.com:jmnavarrol/python-multigit-empty-repo.git'
		repoconf['path'] = os.path.join(self.scenarios_path, 'standard/empty-repo')
		
		# First, let's clone an unitialized repo
		result = self.gitrepo.update(repoconf)
		# Then, check its status
		result = self.gitrepo.status(repoconf)
		print(str(result))
		self.assertEqual(result['status'], 'EMPTY')
		
		
	def test_wrong_repo(self):
		print("TEST: 'test_wrong_repo'")
		# prepares a suitable configuration
		repoconf = {}
		repoconf['repo'] = 'git@github.com:jmnavarrol/doesnt-exist.git'
		repoconf['path'] = os.path.join(self.scenarios_path, 'standard/empty-repo')
		
		result = self.gitrepo.update(repoconf)
		print(str(result))
		self.assertEqual(result['status'], 'ERROR')
		
		
	def test_wrong_remote_status(self):
		print("TEST: 'test_wrong_remote_status'")
		# prepares a suitable configuration
		repoconf = {}
		repoconf['repo'] = 'git@github.com:jmnavarrol/python-multigit-empty-repo.git'
		repoconf['path'] = os.path.join(self.scenarios_path, 'standard/empty-repo')
		
		# First, let's clone an unitialized repo
		result = self.gitrepo.update(repoconf)
		
		# Then, let's change its remote and check
		repoconf['repo'] = 'git@github.com:jmnavarrol/different-remote.git'
		result = self.gitrepo.status(repoconf)
		print(str(result))
		self.assertEqual(result['status'], 'WRONG_REMOTE')
		
		
	def test_pending_updates(self):
		print("TEST: 'test_pending_updates'")
		# prepares a suitable configuration
		repoconf = {}
		repoconf['repo'] = 'git@github.com:jmnavarrol/simplest-git-subrepos.git'
		repoconf['path'] = os.path.join(self.scenarios_path, 'standard/simplest-git-subrepos')
		
		# First, let's clone a standard repo
		result = self.gitrepo.update(repoconf)
		
		# Then, let's change its remote commit and check
		repoconf['gitref_type'] = 'branch'
		repoconf['branch'] = 'python-example'
		result = self.gitrepo.status(repoconf)
		print(str(result))
		self.assertEqual(result['status'], 'PENDING_UPDATE')
		
		
	def test_dirty(self):
		print("TEST: 'test_dirty'")
		# prepares a suitable configuration
		repoconf = {}
		repoconf['repo'] = 'git@github.com:jmnavarrol/simplest-git-subrepos.git'
		repoconf['path'] = os.path.join(self.scenarios_path, 'standard/simplest-git-subrepos')
		
		# First, let's clone a standard repo
		result = self.gitrepo.update(repoconf)
		# Make it dirty
		my_file = os.path.join(
			self.scenarios_path,
			'standard/simplest-git-subrepos',
			'README.md'
		)
		with open(my_file, 'w') as f:
			f.write('THIS IS A CHANGE')
		# Now check the results
		result = self.gitrepo.update(repoconf)
		with open(my_file, 'r') as f:
			print(f.read())
		print(str(result))
		self.assertEqual(result['status'], 'DIRTY')
		
		
	def test_updated(self):
		print("TEST: 'test_updated'")
		# prepares a suitable configuration
		repoconf = {}
		repoconf['repo'] = 'git@github.com:jmnavarrol/simplest-git-subrepos.git'
		repoconf['path'] = os.path.join(self.scenarios_path, 'standard/simplest-git-subrepos')
		
		# First, let's clone a standard repo
		result = self.gitrepo.update(repoconf)
		
		# Then, let's change its remote commit and check
		repoconf['gitref_type'] = 'branch'
		repoconf['branch'] = 'python-example'
		result = self.gitrepo.update(repoconf)
		print(str(result))
		self.assertEqual(result['status'], 'UPDATED')
		
		
	def test_up_to_date(self):
		print("TEST: 'test_up_to_date'")
		# prepares a suitable configuration
		repoconf = {}
		repoconf['repo'] = 'git@github.com:jmnavarrol/simplest-git-subrepos.git'
		repoconf['path'] = os.path.join(self.scenarios_path, 'standard/simplest-git-subrepos')
		
		# First, let's clone a standard repo
		result = self.gitrepo.update(repoconf)
		
		# Then, let's check status is OK
		result = self.gitrepo.status(repoconf)
		print(str(result))
		self.assertEqual(result['status'], 'UP_TO_DATE')
		
		
