# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import tempfile
import unittest


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


if __name__ == '__main__':
    unittest.main()
