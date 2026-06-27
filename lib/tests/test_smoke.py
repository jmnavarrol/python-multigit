import unittest
import re

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


if __name__ == "__main__":
    unittest.main()
