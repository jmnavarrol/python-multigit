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
				TESTS_PATH + '/../helperfiles/subrepos.' + test_item,
				os.path.join(current_scenario_path, 'subrepos')
			)
			
		self.gitrepo = Gitrepo()
		
		
	@classmethod
	def tearDown(self):
		# clean up after the test
		shutil.rmtree(self.scenarios_path)
		
		
if __name__ == '__main__':
	unittest.main()
	
