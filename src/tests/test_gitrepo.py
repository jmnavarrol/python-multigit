# -*- coding: utf-8 -*-
# Tests the Gitrepo class

# Import stuff
import unittest
from . import TESTS_PATH, PROJECT_PATH

import os, shutil

from multigit import Gitrepo

class TestGitrepo(unittest.TestCase):
	
	@classmethod
	def setUp(self):
		self.scenarios_path = os.path.join(TESTS_PATH, 'scenarios')
		self.test_scenarios = [
			'standard',
			'nonexistent-branch',
		]
		
		for test_item in self.test_scenarios:
			current_scenario_path = os.path.join(self.scenarios_path, test_item)
			if not os.path.exists(current_scenario_path):
				os.makedirs(current_scenario_path)
				
			shutil.copy(
				TESTS_PATH + '/subrepos.' + test_item,
				os.path.join(current_scenario_path, 'subrepos')
			)
			
		self.gitrepo = Gitrepo()
		
		
	def test_busy_dir(self):
		print("TEST: 'test_busy_dir'")
		# prepares a suitable configuration
		repoconf = {}
		repoconf['path'] = os.path.join(self.scenarios_path, 'standard')
		result = self.gitrepo.update(repoconf)
		print(str(result))
		self.assertEqual(result['status'], 'ERROR')
		
		
	def test_nonexitent_branch(self):
		print("TEST: 'test_status_not_cloned'")
		# prepares a suitable configuration
		repoconf = {}
		repoconf['repo'] = 'git@github.com:jmnavarrol/simplest-git-subrepos.git'
		repoconf['path'] = os.path.join(self.scenarios_path, 'standard/simplest-git-subrepos')
		repoconf['branch'] = 'nonexistent'
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
		
		
	@classmethod
	def tearDown(self):
		# clean up after the test
		shutil.rmtree(self.scenarios_path)
		
		
if __name__ == '__main__':
	unittest.main()
	
