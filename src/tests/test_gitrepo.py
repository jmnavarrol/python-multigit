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
		
		# Fist, let's clone an unitialized repo
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
		
		
	@classmethod
	def tearDown(self):
		# clean up after the test
		shutil.rmtree(self.scenarios_path)
		
		
if __name__ == '__main__':
	unittest.main()
	