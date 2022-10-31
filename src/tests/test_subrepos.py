# Tests the main entryproints

import unittest
import os, shutil, errno

from . import TESTS_PATH, PROJECT_PATH
import multigit

class TestSubrepos(unittest.TestCase):
	
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
			
		self.my_subrepos = multigit.Subrepos()
	
	
	def test_process_clean_status(self):
		print("TEST: 'test_process_clean_status'")
		for test_item in self.test_scenarios:
			print("SCENARIO: '" + test_item + "', report_only=True:")
			result = self.my_subrepos.process(
				base_path   = os.path.join(self.scenarios_path, test_item),
				report_only = True
			)
			self.assertEqual(result, None)
			
		
	def test_process_run_ok(self):
		print("TEST: 'test_process_run_ok'")
		# Runs "happy" subrepos
		result = self.my_subrepos.process(
			base_path   = os.path.join(self.scenarios_path, 'standard'),
			report_only = False
		)
		self.assertEqual(result, None)
		# Checks status after run
		result = self.my_subrepos.process(
			base_path   = os.path.join(self.scenarios_path, 'standard'),
			report_only = True
		)
		self.assertEqual(result, None)
		
		
	def test_process_run_nonexistent_branch(self):
		print("TEST: 'test_process_run_nonexistent_branch'")
		with self.assertRaises(SystemExit) as cm:
			self.my_subrepos.process(
				base_path   = os.path.join(self.scenarios_path, 'nonexistent-branch'),
				report_only = False
			)
		
		
	@classmethod
	def tearDown(self):
		# clean up after the test
		shutil.rmtree(self.scenarios_path)
		
		
if __name__ == '__main__':
	unittest.main()
	
