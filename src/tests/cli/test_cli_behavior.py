# -*- coding: utf-8 -*-

import os
import io
import subprocess
import sys
import tempfile
import threading
import unittest
import inspect
from contextlib import redirect_stdout
from unittest.mock import patch

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

    def test_version_reports_current_version(self):
        result = self._run_cli('-V')
        self.assertEqual(result.returncode, 0)
        self.assertIn(cli_main.__version__, result.stdout)

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

    def test_cli_rendering_prints_requested_gitref(self):
        subrepo = {
            'path': '/tmp/example-repo',
            'repo': 'example-origin',
            'gitref_type': 'branch',
            'branch': 'python-example',
            'status': 'UP_TO_DATE',
        }
        output = io.StringIO()

        with redirect_stdout(output):
            cli_rendering.print_subrepo_status(subrepo)

        rendered = output.getvalue()
        self.assertIn("requested branch:", rendered)
        self.assertIn("'python-example'", rendered)

    def test_adapter_renders_each_streamed_result_before_completion(self):
        first_result = {
            'path': '/tmp/first-repo',
            'repo': 'first-origin',
            'gitref_type': None,
            'status': 'UP_TO_DATE',
        }
        second_result = {
            'path': '/tmp/second-repo',
            'repo': 'second-origin',
            'gitref_type': None,
            'status': 'UP_TO_DATE',
        }
        first_rendered = threading.Event()
        release_second = threading.Event()
        rendered = []
        worker_errors = []

        def streamed_process(**kwargs):
            yield first_result
            if not release_second.wait(timeout=2):
                raise AssertionError('second result was not released')
            yield second_result

        def record_rendered(result):
            rendered.append(result)
            if result is first_result:
                first_rendered.set()

        def run_adapter():
            try:
                status_run_adapter.process_subrepos_with_adapter(
                    base_path=self.repo_root,
                    report_only=True,
                    subrepos_filename='subrepos',
                )
            except Exception as error:  # pragma: no cover - assertion below reports it
                worker_errors.append(error)

        with patch.object(
            status_run_adapter,
            '_load_multigit_lib_status_orchestrator',
            return_value=(streamed_process, RuntimeError),
        ), patch.object(
            status_run_adapter,
            'print_subrepo_status',
            side_effect=record_rendered,
        ):
            worker = threading.Thread(target=run_adapter)
            worker.start()
            self.assertTrue(first_rendered.wait(timeout=2))
            self.assertEqual(rendered, [first_result])
            release_second.set()
            worker.join(timeout=2)

        self.assertFalse(worker.is_alive())
        self.assertEqual(worker_errors, [])
        self.assertEqual(rendered, [first_result, second_result])

    def test_adapter_passes_status_and_run_modes_to_orchestrator(self):
        received_modes = []

        def streamed_process(**kwargs):
            received_modes.append(kwargs['report_only'])
            return iter(())

        with patch.object(
            status_run_adapter,
            '_load_multigit_lib_status_orchestrator',
            return_value=(streamed_process, RuntimeError),
        ):
            for report_only in (True, False):
                status_run_adapter.process_subrepos_with_adapter(
                    base_path=self.repo_root,
                    report_only=report_only,
                    subrepos_filename='subrepos',
                )

        self.assertEqual(received_modes, [True, False])

    def test_adapter_resolves_streaming_library_orchestrator(self):
        from multigit_lib.subrepos_orchestration import iter_process_subrepos

        resolved_process, _ = status_run_adapter._load_multigit_lib_status_orchestrator()

        self.assertIs(resolved_process, iter_process_subrepos)


if __name__ == '__main__':
    unittest.main()
