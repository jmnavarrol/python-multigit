# -*- coding: utf-8 -*-
import unittest
import os
import shutil

from . import TESTS_PATH
from git_scaffold import build_test_remotes

from multigit_lib import Gitrepo

class GitrepoTestCase(unittest.TestCase):
    def setUp(self):
        self.scenarios_path = os.path.join(TESTS_PATH, 'scenarios')
        self.remotes_path = os.path.join(self.scenarios_path, '_remotes')
        os.makedirs(os.path.join(self.scenarios_path, 'standard'), exist_ok=True)
        self.remotes = build_test_remotes(self.remotes_path)
        self.gitrepo = Gitrepo()

    def tearDown(self):
        if os.path.exists(self.scenarios_path):
            shutil.rmtree(self.scenarios_path)

