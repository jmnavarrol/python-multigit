import importlib
import inspect
import io
import unittest
from contextlib import redirect_stdout


class TestDev5CliRedGate(unittest.TestCase):
    def test_cli_component_package_exists(self):
        module = importlib.import_module('multigit_cli')
        self.assertTrue(hasattr(module, '__version__'))

    def test_cli_entrypoint_module_is_available(self):
        module = importlib.import_module('multigit_cli.__main__')
        self.assertTrue(hasattr(module, 'main'))
        self.assertTrue(callable(module.main))

    def test_cli_version_and_help_paths_run(self):
        module = importlib.import_module('multigit_cli.__main__')

        version_buffer = io.StringIO()
        with redirect_stdout(version_buffer):
            result = module.main(['--version'])
        self.assertEqual(result, 0)
        self.assertIn(module.__version__, version_buffer.getvalue())

        help_buffer = io.StringIO()
        with redirect_stdout(help_buffer):
            result = module.main(['--help'])
        self.assertEqual(result, 0)
        self.assertIn('usage', help_buffer.getvalue().lower())

    def test_cli_rendering_uses_legacy_status_format(self):
        rendering = importlib.import_module('multigit_cli.cli_rendering')
        subrepo = {
            'path': '/tmp/example-repo',
            'repo': 'example-origin',
            'gitref_type': 'branch',
            'branch': 'python-example',
            'status': 'UP_TO_DATE',
        }

        output = io.StringIO()
        with redirect_stdout(output):
            rendering.print_subrepo_status(subrepo)

        rendered = output.getvalue()
        self.assertIn("requested branch:", rendered)
        self.assertIn("'python-example'", rendered)

    def test_cli_has_no_repo_relative_fallback(self):
        module = importlib.import_module('multigit_cli.__main__')
        source = inspect.getsource(module)
        self.assertNotIn('sys.path.insert', source)
        self.assertNotIn('lib/src', source)
        self.assertNotIn('repo_root', source)


if __name__ == '__main__':
    unittest.main()
