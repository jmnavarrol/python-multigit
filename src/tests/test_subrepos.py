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
			
		# And a scenario with no subrepos file
			if not os.path.exists(os.path.join(self.scenarios_path, 'nosubrepos')):
				os.makedirs(os.path.join(self.scenarios_path, 'nosubrepos'))
			
		self.my_subrepos = multigit.Subrepos()
	
	
	def test_no_subrepos_found(self):
		print("TEST: 'test_no_subrepos_found'")
		for test_status in [True, False]:
			print("'test_no_subrepos_found', report_only=" + str(test_status))
			with self.assertRaises(SystemExit) as cm:
				self.my_subrepos.process(
					base_path   = os.path.join(self.scenarios_path, 'nosubrepos'),
					report_only = test_status
				)
				
			self.assertEqual(cm.exception.code, errno.ENOENT)
		
		
	def test_process_clean_status(self):
		print("TEST: 'test_process_clean_status'")
		for test_item in self.test_scenarios:
			print("SCENARIO: '" + test_item + "', report_only=True:")
			result = self.my_subrepos.process(
				base_path   = os.path.join(self.scenarios_path, test_item),
				report_only = True
			)
			print(str(result))
			self.assertEqual(result, None)
			
		
	def test_process_run_ok(self):
		print("TEST: 'test_process_run_ok'")
		# Runs "happy" subrepos
		print("TEST: 'test_process_run_ok', RUN")
		result = self.my_subrepos.process(
			base_path   = os.path.join(self.scenarios_path, 'standard'),
			report_only = False
		)
		print(str(result))
		self.assertEqual(result, None)
		# Checks status after run
		print("TEST: 'test_process_run_ok', STATUS")
		result = self.my_subrepos.process(
			base_path   = os.path.join(self.scenarios_path, 'standard'),
			report_only = True
		)
		print(str(result))
		self.assertEqual(result, None)
		
		
	@classmethod
	def tearDown(self):
		# clean up after the test
		shutil.rmtree(self.scenarios_path)
		
		
if __name__ == '__main__':
	unittest.main()
	
