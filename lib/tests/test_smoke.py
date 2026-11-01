import unittest
import re
import importlib

import multigit_lib


class TestMultigitLibSmoke(unittest.TestCase):
    def test_import_works(self):
        self.assertIsNotNone(multigit_lib)

    def test_version(self):
        version = multigit_lib.__version__
        self.assertIsInstance(version, str)
        self.assertNotEqual(version.strip(), "")
        self.assertRegex(
            version,
            re.compile(r"^\d+\.\d+\.\d+(?:(?:a|b|rc)\d+|\.(?:dev|post)\d+)?$"),
        )

    def test_public_surface_excludes_config_file_workflow(self):
        self.assertTrue(hasattr(multigit_lib, 'Gitrepo'))
        self.assertFalse(hasattr(multigit_lib, 'Subrepofile'))
        self.assertFalse(hasattr(multigit_lib, 'SubrepofileError'))
        with self.assertRaises(ModuleNotFoundError):
            importlib.import_module('multigit_lib.subrepos_orchestration')


if __name__ == "__main__":
    unittest.main()
