import errno
import os
import shutil
import unittest
from unittest.mock import patch

from git_scaffold import build_test_remotes, create_seeded_bare_remote, write_subrepos_file
from multigit_cli.subrepos_orchestration import Subrepos, SubreposOrchestrationError


class TestSubreposOrchestration(unittest.TestCase):
    def setUp(self):
        self.scenarios_path = os.path.join(os.path.dirname(__file__), 'scenarios')
        self.remotes = build_test_remotes(os.path.join(self.scenarios_path, '_remotes'))
        for scenario in ('standard', 'nonexistent-branch', 'nosubrepos'):
            os.makedirs(os.path.join(self.scenarios_path, scenario), exist_ok=True)

        write_subrepos_file(
            os.path.join(self.scenarios_path, 'standard', 'subrepos'),
            [
                {'path': 'empty-repo', 'repo': self.remotes['empty_repo']},
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
        self.subrepos = Subrepos()

    def tearDown(self):
        if os.path.exists(self.scenarios_path):
            shutil.rmtree(self.scenarios_path)

    def test_wrong_subrepos_permissions(self):
        base_path = os.path.join(self.scenarios_path, 'standard')
        subrepos_file = os.path.join(base_path, 'subrepos')
        os.chmod(subrepos_file, 0o222)

        with self.assertRaises(SubreposOrchestrationError) as context:
            self.subrepos.process(base_path=base_path, report_only=True)

        self.assertEqual(context.exception.errno, errno.EPERM)

    def test_no_subrepos_found(self):
        with self.assertRaises(SubreposOrchestrationError) as context:
            self.subrepos.process(
                base_path=os.path.join(self.scenarios_path, 'nosubrepos'),
            )

        self.assertEqual(context.exception.errno, errno.ENOENT)

    def test_process_reports_status_for_each_configured_repository(self):
        expected_statuses = {
            'standard': ['NOT_CLONED', 'NOT_CLONED'],
            'nonexistent-branch': ['NOT_CLONED'],
        }
        for scenario, expected_statuses_for_scenario in expected_statuses.items():
            result = self.subrepos.process(
                base_path=os.path.join(self.scenarios_path, scenario),
                report_only=True,
            )

            self.assertEqual(
                [entry['status'] for entry in result],
                expected_statuses_for_scenario,
            )
            self.assertEqual(len(result), len(expected_statuses_for_scenario))

    def test_process_discovers_nested_subrepos_file(self):
        nested_parent_remote = os.path.join(self.scenarios_path, '_remotes', 'nested-parent.git')
        nested_subrepos_contents = (
            "---\nsubrepos:\n"
            f"- path: 'nested-child'\n  repo: '{self.remotes['empty_repo']}'\n"
        )
        create_seeded_bare_remote(
            remote_path=nested_parent_remote,
            default_branch='main',
            extra_branches=[],
            extra_files={'subrepos': nested_subrepos_contents},
        )
        nested_base_path = os.path.join(self.scenarios_path, 'nested')
        os.makedirs(nested_base_path, exist_ok=True)
        write_subrepos_file(
            os.path.join(nested_base_path, 'subrepos'),
            [{'path': 'parent', 'repo': nested_parent_remote}],
        )

        result = self.subrepos.process(base_path=nested_base_path, report_only=False)

        self.assertEqual(
            [entry['path'] for entry in result],
            [
                os.path.realpath(os.path.join(nested_base_path, 'parent')),
                os.path.realpath(os.path.join(nested_base_path, 'parent', 'nested-child')),
            ],
        )
        self.assertEqual([entry['status'] for entry in result], ['CLONED', 'CLONED'])

    def test_process_materializes_all_results_before_return(self):
        processed_paths = []

        def record_status(repoconf):
            processed_paths.append(os.path.basename(repoconf['path']))
            repoconf['status'] = 'UP_TO_DATE'
            return repoconf

        with patch('multigit_cli.subrepos_orchestration.Gitrepo.status', side_effect=record_status):
            result = self.subrepos.process(
                base_path=os.path.join(self.scenarios_path, 'standard'),
                report_only=True,
            )

        self.assertEqual(processed_paths, ['empty-repo', 'standard-repo'])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(processed_paths))

    def test_iterator_yields_first_result_before_processing_second(self):
        from multigit_cli.subrepos_orchestration import iter_process_subrepos

        processed_paths = []

        def record_status(repoconf):
            processed_paths.append(os.path.basename(repoconf['path']))
            repoconf['status'] = 'UP_TO_DATE'
            return repoconf

        with patch(
            'multigit_cli.subrepos_orchestration.Gitrepo.status',
            side_effect=record_status,
        ):
            results = iter_process_subrepos(
                base_path=os.path.join(self.scenarios_path, 'standard'),
                report_only=True,
            )
            first_result = next(results)
            self.assertEqual(processed_paths, ['empty-repo'])
            second_result = next(results)

        self.assertEqual(processed_paths, ['empty-repo', 'standard-repo'])
        self.assertEqual(first_result['status'], 'UP_TO_DATE')
        self.assertEqual(second_result['status'], 'UP_TO_DATE')

    def test_iter_process_continues_after_repository_error(self):
        from multigit_cli.subrepos_orchestration import iter_process_subrepos

        def fail_first_status(repoconf):
            if repoconf['path'].endswith('empty-repo'):
                raise RuntimeError('simulated repository failure')
            repoconf['status'] = 'UP_TO_DATE'
            return repoconf

        with patch(
            'multigit_cli.subrepos_orchestration.Gitrepo.status',
            side_effect=fail_first_status,
        ):
            results = list(
                iter_process_subrepos(
                    base_path=os.path.join(self.scenarios_path, 'standard'),
                    report_only=True,
                )
            )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['status'], 'ERROR')
        self.assertIn('simulated repository failure', results[0]['extra_info'])
        self.assertEqual(
            results[1]['path'],
            os.path.join(self.scenarios_path, 'standard', 'standard-repo'),
        )

    def test_process_run_clones_and_reports_expected_statuses(self):
        run_results = self.subrepos.process(
            base_path=os.path.join(self.scenarios_path, 'standard'),
            report_only=False,
        )
        self.assertEqual([entry['status'] for entry in run_results], ['CLONED', 'CLONED'])

        status_results = self.subrepos.process(
            base_path=os.path.join(self.scenarios_path, 'standard'),
            report_only=True,
        )
        self.assertEqual([entry['status'] for entry in status_results], ['EMPTY', 'UP_TO_DATE'])