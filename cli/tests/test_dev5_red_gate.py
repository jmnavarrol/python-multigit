import importlib
import unittest


class TestDev5CliRedGate(unittest.TestCase):
    def test_cli_component_package_exists(self):
        module = importlib.import_module('multigit_cli')
        self.assertTrue(hasattr(module, '__version__'))

    def test_cli_entrypoint_module_is_available(self):
        module = importlib.import_module('multigit_cli.__main__')
        self.assertTrue(hasattr(module, 'main'))
        self.assertTrue(callable(module.main))


if __name__ == '__main__':
    unittest.main()
