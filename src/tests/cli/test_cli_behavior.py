# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import tempfile
import unittest
import inspect

import multigit.__main__ as cli_main
import multigit.status_run_adapter as status_run_adapter
import multigit.cli_rendering as cli_rendering


class TestCliBehavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = os.path.realpath(
            os.path.join(os.path.dirname(__file__), '..', '..', '..')
        )
        cls.env = os.environ.copy()
        cls.env['PYTHONPATH'] = os.path.join(cls.repo_root, 'src')

    def _run_cli(self, *args, cwd=None):
        return subprocess.run(
            [sys.executable, '-m', 'multigit', *args],
            cwd=cwd or self.repo_root,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_help_shows_usage(self):
        result = self._run_cli('-h')
        self.assertEqual(result.returncode, 0)
        self.assertIn('usage:', result.stdout)

    def test_version_reports_dev2(self):
        result = self._run_cli('-V')
        self.assertEqual(result.returncode, 0)
        self.assertIn('0.12.0.dev2', result.stdout)

    def test_no_args_requires_arguments(self):
        result = self._run_cli()
        self.assertEqual(result.returncode, 0)
        self.assertIn('arguments required', result.stdout)

    def test_status_missing_config_maps_exit_and_message(self):
        with tempfile.TemporaryDirectory(prefix='multigit-cli-', dir=self.repo_root) as temp_dir:
            result = self._run_cli('--status', cwd=temp_dir)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Couldn't find any 'subrepos' file... exiting.", result.stdout)

    def test_legacy_lane_env_toggle_retired(self):
        source = inspect.getsource(cli_main)
        self.assertNotIn('MULTIGIT_USE_LEGACY_LANE', source)

    def test_legacy_lane_selector_helper_removed(self):
        self.assertFalse(hasattr(cli_main, '_should_use_legacy_lane'))

    def test_status_run_adapter_does_not_depend_on_subrepos_class(self):
        source = inspect.getsource(status_run_adapter)
        self.assertNotIn('from .subrepos import Subrepos', source)

    def test_cli_rendering_exposes_subrepo_status_renderer(self):
        self.assertTrue(hasattr(cli_rendering, 'print_subrepo_status'))


if __name__ == '__main__':
    unittest.main()
