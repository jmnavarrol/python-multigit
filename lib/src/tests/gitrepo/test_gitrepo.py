# -*- coding: utf-8 -*-
# Tests the Gitrepo class

# Import stuff
import unittest
from . import TESTS_PATH, PROJECT_PATH

import os, shutil
from git_scaffold import build_test_remotes, write_subrepos_file

from multigit import Gitrepo

class TestGitrepo(unittest.TestCase):
	
	@classmethod
	def setUp(self):
		self.scenarios_path = os.path.join(TESTS_PATH, 'scenarios')
		self.remotes_path = os.path.join(self.scenarios_path, '_remotes')
		self.test_scenarios = [
			'standard',
			'nonexistent-branch',
		]
		os.makedirs(self.scenarios_path, exist_ok=True)
		self.remotes = build_test_remotes(self.remotes_path)
		
		for test_item in self.test_scenarios:
			current_scenario_path = os.path.join(self.scenarios_path, test_item)
			if not os.path.exists(current_scenario_path):
				os.makedirs(current_scenario_path)

		write_subrepos_file(
			os.path.join(self.scenarios_path, 'standard', 'subrepos'),
			[
				{
					'path': 'empty-repo',
					'repo': self.remotes['empty_repo'],
				},
				{
					'path': 'standard-repo',
					'repo': self.remotes['standard_repo'],
					'branch': 'a-branch',
				},
			],
		)

		write_subrepos_file(
			os.path.join(self.scenarios_path, 'nonexistent-branch', 'subrepos'),
			[
				{
					'path': 'standard-repo',
					'repo': self.remotes['standard_repo'],
					'branch': 'non-existant',
				},
			],
		)
			
		self.gitrepo = Gitrepo()
		
		
	@classmethod
	def tearDown(self):
		# clean up after the test
		if os.path.exists(self.scenarios_path):
			shutil.rmtree(self.scenarios_path)
		
		
if __name__ == '__main__':
	unittest.main()
	
