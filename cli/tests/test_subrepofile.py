import errno
import os
import tempfile
import unittest

from multigit_cli.subrepofile import Subrepofile, SubrepofileError


class TestSubrepofile(unittest.TestCase):
    def _write_subrepos_file(self, path, contents):
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(contents)

    def test_load_normalizes_relative_paths_and_gitrefs(self):
        with tempfile.TemporaryDirectory(prefix='multigit-subrepofile-') as temp_dir:
            subrepos_file = os.path.join(temp_dir, 'subrepos')
            self._write_subrepos_file(
                subrepos_file,
                """---
subrepos:
  - path: empty-repo
    repo: file:///empty.git
  - path: standard-repo
    repo: file:///standard.git
    branch: a-branch
""",
            )

            result = Subrepofile().load(subrepos_file)

        self.assertEqual(
            result,
            [
                {
                    'path': os.path.realpath(os.path.join(temp_dir, 'empty-repo')),
                    'repo': 'file:///empty.git',
                    'gitref_type': None,
                },
                {
                    'path': os.path.realpath(os.path.join(temp_dir, 'standard-repo')),
                    'repo': 'file:///standard.git',
                    'branch': 'a-branch',
                    'gitref_type': 'branch',
                },
            ],
        )

    def test_load_malformed_yaml_raises_einval(self):
        with tempfile.TemporaryDirectory(prefix='multigit-subrepofile-') as temp_dir:
            subrepos_file = os.path.join(temp_dir, 'subrepos')
            self._write_subrepos_file(subrepos_file, 'subrepos:\n  - path: [broken\n')

            with self.assertRaises(SubrepofileError) as context:
                Subrepofile().load(subrepos_file)

        self.assertEqual(context.exception.errno, errno.EINVAL)