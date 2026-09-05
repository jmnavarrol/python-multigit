# Tests the main entryproints

import unittest
import os, shutil, errno
from unittest.mock import patch

from . import TESTS_PATH, PROJECT_PATH
from git_scaffold import build_test_remotes, write_subrepos_file
from multigit_lib.subrepos_orchestration import Subrepos, SubreposOrchestrationError

class TestSubrepos(unittest.TestCase):
	
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

		# And a scenario with no subrepos file
		if not os.path.exists(os.path.join(self.scenarios_path, 'nosubrepos')):
			os.makedirs(os.path.join(self.scenarios_path, 'nosubrepos'))
			
		self.my_subrepos = Subrepos()
	
	
	def test_wrong_subrepos_permissions(self):
		print("TEST: 'test_wrong_subrepos_permissions'")
		base_path = os.path.join(self.scenarios_path, 'standard')
		subrepo_file = os.path.join(base_path, 'subrepos')
		os.chmod(subrepo_file, 0o222)
			
		with self.assertRaises(SubreposOrchestrationError) as cm:
			self.my_subrepos.process(
				base_path   = base_path,
				report_only = True
			)
			
		self.assertEqual(cm.exception.errno, errno.EPERM)
	
	
	def test_no_subrepos_found(self):
		print("TEST: 'test_no_subrepos_found'")
		with self.assertRaises(SubreposOrchestrationError) as cm:
			self.my_subrepos.process(
				base_path   = os.path.join(self.scenarios_path, 'nosubrepos'),
			)
			
		self.assertEqual(cm.exception.errno, errno.ENOENT)
		
		
	def test_process_clean_status(self):
		print("TEST: 'test_process_clean_status'")
		for test_item in self.test_scenarios:
			print("SCENARIO: '" + test_item + "', report_only=True:")
			result = self.my_subrepos.process(
				base_path   = os.path.join(self.scenarios_path, test_item),
				report_only = True
			)
			print(str(result))
			self.assertIsInstance(result, list)


	def test_process_materializes_all_results_before_return(self):
		print("TEST: 'test_process_materializes_all_results_before_return'")
		processed_paths = []

		def record_status(repoconf):
			processed_paths.append(os.path.basename(repoconf['path']))
			repoconf['status'] = 'UP_TO_DATE'
			return repoconf

		with patch(
			'multigit_lib.subrepos_orchestration.Gitrepo.status',
			side_effect=record_status,
		):
			result = self.my_subrepos.process(
				base_path=os.path.join(self.scenarios_path, 'standard'),
				report_only=True,
			)

		self.assertEqual(processed_paths, ['empty-repo', 'standard-repo'])
		self.assertIsInstance(result, list)
		self.assertEqual(len(result), len(processed_paths))


	def test_iter_process_yields_before_second_repository_finishes(self):
		print("TEST: 'test_iter_process_yields_before_second_repository_finishes'")
		from multigit_lib.subrepos_orchestration import iter_process_subrepos

		results = iter_process_subrepos(
			base_path=os.path.join(self.scenarios_path, 'standard'),
			report_only=True,
		)
		self.assertEqual(next(results)['path'], os.path.join(
			self.scenarios_path, 'standard', 'empty-repo'
		))


	def test_iter_process_continues_after_repository_error(self):
		print("TEST: 'test_iter_process_continues_after_repository_error'")
		from multigit_lib.subrepos_orchestration import iter_process_subrepos

		def fail_first_status(repoconf):
			if repoconf['path'].endswith('empty-repo'):
				raise RuntimeError('simulated repository failure')
			repoconf['status'] = 'UP_TO_DATE'
			return repoconf

		with patch(
			'multigit_lib.subrepos_orchestration.Gitrepo.status',
			side_effect=fail_first_status,
		):
			results = list(iter_process_subrepos(
				base_path=os.path.join(self.scenarios_path, 'standard'),
				report_only=True,
			))

		self.assertEqual(len(results), 2)
		self.assertEqual(results[0]['status'], 'ERROR')
		self.assertIn('simulated repository failure', results[0]['extra_info'])
		self.assertEqual(results[1]['path'], os.path.join(
			self.scenarios_path, 'standard', 'standard-repo'
		))
			
		
	def test_process_run_ok(self):
		print("TEST: 'test_process_run_ok'")
		# Runs "happy" subrepos
		print("TEST: 'test_process_run_ok', RUN")
		result = self.my_subrepos.process(
			base_path   = os.path.join(self.scenarios_path, 'standard'),
			report_only = False
		)
		print(str(result))
		self.assertIsInstance(result, list)
		# Checks status after run
		print("TEST: 'test_process_run_ok', STATUS")
		result = self.my_subrepos.process(
			base_path   = os.path.join(self.scenarios_path, 'standard'),
			report_only = True
		)
		print(str(result))
		self.assertIsInstance(result, list)
		
		
	@classmethod
	def tearDown(self):
		# clean up after the test
		if os.path.exists(self.scenarios_path):
			shutil.rmtree(self.scenarios_path)
		
		
if __name__ == '__main__':
	unittest.main()
	
