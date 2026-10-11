import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from multigit_cli import __main__ as cli_main


class TestCliOfflineAcceptance(unittest.TestCase):
    def _git(self, args, cwd):
        result = subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        return result

    def _create_remote(self, remote_dir, default_branch='main', extra_branches=None):
        extra_branches = extra_branches or []
        os.makedirs(os.path.dirname(remote_dir), exist_ok=True)
        self._git(['init', '--bare', remote_dir], cwd=os.getcwd())

        work_dir = tempfile.mkdtemp(prefix='multigit-remote-')
        try:
            self._git(['init', work_dir], cwd=os.getcwd())
            self._git(['config', 'user.name', 'multigit-tests'], cwd=work_dir)
            self._git(['config', 'user.email', 'multigit-tests@example.com'], cwd=work_dir)
            with open(os.path.join(work_dir, 'README.md'), 'w', encoding='utf-8') as handle:
                handle.write('seed\n')
            self._git(['add', 'README.md'], cwd=work_dir)
            self._git(['commit', '-m', 'initial commit'], cwd=work_dir)
            self._git(['branch', '-M', default_branch], cwd=work_dir)
            self._git(['remote', 'add', 'origin', remote_dir], cwd=work_dir)
            self._git(['push', '--set-upstream', 'origin', default_branch], cwd=work_dir)

            for branch_name in extra_branches:
                self._git(['checkout', '-b', branch_name], cwd=work_dir)
                with open(os.path.join(work_dir, f'{branch_name}.txt'), 'w', encoding='utf-8') as handle:
                    handle.write(f'branch: {branch_name}\n')
                self._git(['add', f'{branch_name}.txt'], cwd=work_dir)
                self._git(['commit', '-m', f'commit on {branch_name}'], cwd=work_dir)
                self._git(['push', '--set-upstream', 'origin', branch_name], cwd=work_dir)

            self._git(['checkout', default_branch], cwd=work_dir)
            self._git(['symbolic-ref', 'HEAD', f'refs/heads/{default_branch}'], cwd=remote_dir)
        finally:
            shutil.rmtree(work_dir)

    def _write_subrepos(self, directory, entries):
        with open(os.path.join(directory, 'subrepos'), 'w', encoding='utf-8') as handle:
            handle.write('---\nsubrepos:\n')
            for entry in entries:
                handle.write(f"- path: '{entry['path']}'\n")
                handle.write(f"  repo: '{entry['repo']}'\n")
                if 'branch' in entry:
                    handle.write(f"  branch: '{entry['branch']}'\n")

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

    def test_cli_resolves_installed_library_orchestrator(self):
        from multigit_lib.subrepos_orchestration import (
            iter_process_subrepos,
            SubreposOrchestrationError,
        )

        resolved_process, resolved_error = cli_main._load_orchestrator()

        self.assertIs(resolved_process, iter_process_subrepos)
        self.assertIs(resolved_error, SubreposOrchestrationError)

    def test_status_runs_against_local_git_scenario(self):
        with tempfile.TemporaryDirectory(prefix='multigit-acceptance-') as temp_dir:
            remote_path = os.path.join(temp_dir, 'remotes', 'python-multigit-empty-repo.git')
            self._create_remote(remote_path, default_branch='main', extra_branches=['a-branch'])
            self._write_subrepos(
                temp_dir,
                [{'path': 'child-repo', 'repo': remote_path, 'branch': 'a-branch'}],
            )
            result = self._run_multigit('--status', cwd=temp_dir)

        self.assertEqual(result.returncode, 0)
        self.assertIn('NOT YET CLONED', result.stdout)
        self.assertIn('child-repo', result.stdout)

    def test_run_clones_local_subrepo(self):
        with tempfile.TemporaryDirectory(prefix='multigit-acceptance-') as temp_dir:
            remote_path = os.path.join(temp_dir, 'remotes', 'python-multigit-empty-repo.git')
            self._create_remote(remote_path, default_branch='main', extra_branches=['a-branch'])
            self._write_subrepos(
                temp_dir,
                [{'path': 'child-repo', 'repo': remote_path, 'branch': 'a-branch'}],
            )
            result = self._run_multigit('--run', cwd=temp_dir)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.isdir(os.path.join(temp_dir, 'child-repo')))


if __name__ == '__main__':
    unittest.main()
