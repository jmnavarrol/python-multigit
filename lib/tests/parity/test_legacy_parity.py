# -*- coding: utf-8 -*-
"""Parity checks between legacy src/multigit and lib/src/multigit_lib."""

import errno
import os
import shutil
import sys
import unittest

from git_scaffold import build_test_remotes, write_subrepos_file
from multigit_lib.gitrepo import Gitrepo as LibGitrepo
from multigit_lib.subrepofile import Subrepofile as LibSubrepofile
from multigit_lib.subrepofile import SubrepofileError as LibSubrepofileError


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
LEGACY_SRC_PATH = os.path.join(REPO_ROOT, 'src')
if LEGACY_SRC_PATH not in sys.path:
    sys.path.insert(0, LEGACY_SRC_PATH)

from multigit.gitrepo import Gitrepo as LegacyGitrepo  # noqa: E402
from multigit.subrepofile import Subrepofile as LegacySubrepofile  # noqa: E402
from multigit.subrepofile import SubrepofileError as LegacySubrepofileError  # noqa: E402


class TestLegacyParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenarios_path = os.path.join(REPO_ROOT, 'lib', 'tests', 'scenarios_parity')
        cls.remotes_path = os.path.join(cls.scenarios_path, '_remotes')
        os.makedirs(cls.scenarios_path, exist_ok=True)
        cls.remotes = build_test_remotes(cls.remotes_path)

        cls.legacy_gitrepo = LegacyGitrepo()
        cls.lib_gitrepo = LibGitrepo()
        cls.legacy_subrepofile = LegacySubrepofile()
        cls.lib_subrepofile = LibSubrepofile()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.scenarios_path):
            shutil.rmtree(cls.scenarios_path)

    def _repoconf_pair(self, case_name, remote_key='simplest_repo', extra=None):
        legacy_path = os.path.join(self.scenarios_path, case_name, 'legacy-repo')
        lib_path = os.path.join(self.scenarios_path, case_name, 'lib-repo')
        os.makedirs(os.path.dirname(legacy_path), exist_ok=True)
        os.makedirs(os.path.dirname(lib_path), exist_ok=True)

        repoconf_legacy = {
            'repo': self.remotes[remote_key],
            'path': legacy_path,
        }
        repoconf_lib = {
            'repo': self.remotes[remote_key],
            'path': lib_path,
        }

        if extra:
            repoconf_legacy.update(extra)
            repoconf_lib.update(extra)

        return repoconf_legacy, repoconf_lib

    def test_status_not_cloned_parity(self):
        legacy_conf, lib_conf = self._repoconf_pair('status-not-cloned')

        legacy_result = self.legacy_gitrepo.status(dict(legacy_conf))
        lib_result = self.lib_gitrepo.status(dict(lib_conf))

        self.assertEqual(legacy_result['status'], lib_result['status'])
        self.assertEqual(lib_result['status'], 'NOT_CLONED')

    def test_update_clone_parity(self):
        legacy_conf, lib_conf = self._repoconf_pair('update-clone')

        legacy_result = self.legacy_gitrepo.update(dict(legacy_conf))
        lib_result = self.lib_gitrepo.update(dict(lib_conf))

        self.assertEqual(legacy_result['status'], lib_result['status'])
        self.assertEqual(lib_result['status'], 'CLONED')

    def test_status_pending_update_parity(self):
        legacy_conf, lib_conf = self._repoconf_pair('status-pending-update')

        self.legacy_gitrepo.update(dict(legacy_conf))
        self.lib_gitrepo.update(dict(lib_conf))

        legacy_conf.update({'gitref_type': 'branch', 'branch': 'python-example'})
        lib_conf.update({'gitref_type': 'branch', 'branch': 'python-example'})

        legacy_result = self.legacy_gitrepo.status(dict(legacy_conf))
        lib_result = self.lib_gitrepo.status(dict(lib_conf))

        self.assertEqual(legacy_result['status'], lib_result['status'])
        self.assertEqual(lib_result['status'], 'PENDING_UPDATE')
        self.assertEqual(bool(legacy_result.get('from')), bool(lib_result.get('from')))
        self.assertEqual(bool(legacy_result.get('to')), bool(lib_result.get('to')))

    def test_status_wrong_remote_parity(self):
        legacy_conf, lib_conf = self._repoconf_pair('status-wrong-remote', remote_key='empty_repo')

        self.legacy_gitrepo.update(dict(legacy_conf))
        self.lib_gitrepo.update(dict(lib_conf))

        legacy_conf['repo'] = self.remotes['different_remote']
        lib_conf['repo'] = self.remotes['different_remote']

        legacy_result = self.legacy_gitrepo.status(dict(legacy_conf))
        lib_result = self.lib_gitrepo.status(dict(lib_conf))

        self.assertEqual(legacy_result['status'], lib_result['status'])
        self.assertEqual(lib_result['status'], 'WRONG_REMOTE')

    def test_subrepofile_load_valid_parity(self):
        valid_file = os.path.join(self.scenarios_path, 'subrepofile-valid', 'subrepos')
        write_subrepos_file(
            valid_file,
            [
                {
                    'path': 'empty-repo',
                    'repo': self.remotes['empty_repo'],
                },
                {
                    'path': 'standard-repo',
                    'repo': self.remotes['standard_repo'],
                    'branch': 'a-branch',
                },
            ],
        )

        legacy_result = self.legacy_subrepofile.load(valid_file)
        lib_result = self.lib_subrepofile.load(valid_file)

        self.assertEqual(legacy_result, lib_result)

    def test_subrepofile_load_malformed_yaml_parity(self):
        malformed_file = os.path.join(self.scenarios_path, 'subrepofile-malformed', 'subrepos')
        os.makedirs(os.path.dirname(malformed_file), exist_ok=True)
        with open(malformed_file, 'w', encoding='utf-8') as handler:
            handler.write('subrepos:\n  - path: [broken\n')

        with self.assertRaises(LegacySubrepofileError) as legacy_ctx:
            self.legacy_subrepofile.load(malformed_file)

        with self.assertRaises(LibSubrepofileError) as lib_ctx:
            self.lib_subrepofile.load(malformed_file)

        self.assertEqual(legacy_ctx.exception.errno, errno.EINVAL)
        self.assertEqual(lib_ctx.exception.errno, errno.EINVAL)


if __name__ == '__main__':
    unittest.main()
