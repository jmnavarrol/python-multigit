import unittest

import multigit_lib


class TestMultigitLibSmoke(unittest.TestCase):
    def test_import_works(self):
        self.assertIsNotNone(multigit_lib)

    def test_version(self):
        self.assertEqual(multigit_lib.__version__, "0.0.1.dev1")


if __name__ == "__main__":
    unittest.main()
