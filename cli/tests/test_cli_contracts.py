import importlib
import io
import unittest
from contextlib import redirect_stdout


class TestCliPackageContracts(unittest.TestCase):
    def test_cli_package_exposes_version(self):
        module = importlib.import_module('multigit_cli')
        self.assertTrue(hasattr(module, '__version__'))

    def test_cli_entrypoint_is_importable(self):
        module = importlib.import_module('multigit_cli.__main__')
        self.assertTrue(callable(module.main))

    def test_main_reports_version_and_help(self):
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

    def test_status_rendering_includes_requested_branch(self):
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
        self.assertIn('requested branch:', rendered)
        self.assertIn("'python-example'", rendered)


if __name__ == '__main__':
    unittest.main()