import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from git_scaffold import create_seeded_bare_remote, write_subrepos_file
from multigit_cli import __main__ as cli_main


class TestCliOfflineAcceptance(unittest.TestCase):
    def _run_multigit(self, *args, cwd=None):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        venv_bin = os.path.join(project_root, '.bme.d', '.virtualenvs', 'multigit-development', 'bin')
        script_path = os.path.join(venv_bin, 'multigit') if os.path.isfile(os.path.join(venv_bin, 'multigit')) else shutil.which('multigit') or 'multigit'
        env = os.environ.copy()
        if os.path.isdir(venv_bin):
            env['PATH'] = f"{venv_bin}{os.pathsep}{env.get('PATH', '')}"
        return subprocess.run(
            [script_path, *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

    def test_help_and_version_are_available(self):
        help_result = self._run_multigit('--help', cwd=os.getcwd())
        self.assertEqual(help_result.returncode, 0)
        self.assertIn('usage', help_result.stdout.lower())

        version_result = self._run_multigit('--version', cwd=os.getcwd())
        self.assertEqual(version_result.returncode, 0)
        self.assertIn('multigit', version_result.stdout.lower())

    def test_no_args_reports_usage(self):
        with tempfile.TemporaryDirectory(prefix='multigit-acceptance-') as temp_dir:
            result = self._run_multigit(cwd=temp_dir)
        self.assertEqual(result.returncode, 0)
        self.assertIn('arguments required', result.stdout.lower())

    def test_status_without_subrepos_reports_missing_config(self):
        with tempfile.TemporaryDirectory(prefix='multigit-acceptance-') as temp_dir:
            result = self._run_multigit('--status', cwd=temp_dir)

        self.assertEqual(result.returncode, 2)
        self.assertIn("Couldn't find any 'subrepos' file... exiting.", result.stdout)

    def test_each_subrepo_is_rendered_before_next_result_is_requested(self):
        first_result = {'path': '/tmp/first-repo', 'status': 'UP_TO_DATE'}
        second_result = {'path': '/tmp/second-repo', 'status': 'UP_TO_DATE'}
        rendered = []

        def streamed_process(**kwargs):
            yield first_result
            self.assertEqual(rendered, [first_result])
            yield second_result

        with patch.object(
            cli_main,
            '_load_orchestrator',
            return_value=(streamed_process, RuntimeError),
        ), patch.object(
            cli_main,
            'print_subrepo_status',
            side_effect=rendered.append,
        ):
            cli_main._process_subrepos('/tmp', report_only=True)

        self.assertEqual(rendered, [first_result, second_result])

    def test_process_passes_status_and_run_modes_to_orchestrator(self):
        received_calls = []

        def streamed_process(**kwargs):
            received_calls.append(kwargs)
            return iter(())

        with patch.object(
            cli_main,
            '_load_orchestrator',
            return_value=(streamed_process, RuntimeError),
        ):
            cli_main._process_subrepos('/tmp/example', report_only=True)
            cli_main._process_subrepos('/tmp/example', report_only=False)

        self.assertEqual(
            [call['report_only'] for call in received_calls],
            [True, False],
        )
        self.assertTrue(all(call['base_path'] == '/tmp/example' for call in received_calls))
        self.assertTrue(all(call['subrepos_filename'] == 'subrepos' for call in received_calls))

    def test_cli_orchestrator_uses_library_repository_service(self):
        from multigit_lib import Gitrepo
        from multigit_cli.subrepos_orchestration import (
            iter_process_subrepos,
            SubreposOrchestrationError,
            Gitrepo as OrchestratorGitrepo,
        )

        resolved_process, resolved_error = cli_main._load_orchestrator()

        self.assertIs(resolved_process, iter_process_subrepos)
        self.assertIs(resolved_error, SubreposOrchestrationError)
        self.assertIs(OrchestratorGitrepo, Gitrepo)

    def test_status_runs_against_local_git_scenario(self):
        with tempfile.TemporaryDirectory(prefix='multigit-acceptance-') as temp_dir:
            remote_path = os.path.join(temp_dir, 'remotes', 'python-multigit-empty-repo.git')
            create_seeded_bare_remote(remote_path, default_branch='main', extra_branches=['a-branch'])
            write_subrepos_file(
                os.path.join(temp_dir, 'subrepos'),
                [{'path': 'child-repo', 'repo': remote_path, 'branch': 'a-branch'}],
            )
            result = self._run_multigit('--status', cwd=temp_dir)

        self.assertEqual(result.returncode, 0)
        self.assertIn('NOT YET CLONED', result.stdout)
        self.assertIn('child-repo', result.stdout)

    def test_run_clones_local_subrepo(self):
        with tempfile.TemporaryDirectory(prefix='multigit-acceptance-') as temp_dir:
            remote_path = os.path.join(temp_dir, 'remotes', 'python-multigit-empty-repo.git')
            create_seeded_bare_remote(remote_path, default_branch='main', extra_branches=['a-branch'])
            write_subrepos_file(
                os.path.join(temp_dir, 'subrepos'),
                [{'path': 'child-repo', 'repo': remote_path, 'branch': 'a-branch'}],
            )
            result = self._run_multigit('--run', cwd=temp_dir)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.isdir(os.path.join(temp_dir, 'child-repo')))


if __name__ == '__main__':
    unittest.main()
