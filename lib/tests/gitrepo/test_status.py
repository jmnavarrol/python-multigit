import os

from .test_gitrepo import GitrepoTestCase


class TestGitrepoStatus(GitrepoTestCase):
    def test_status_reports_uncloned_repository(self):
        repoconf = {
            'path': os.path.join(self.scenarios_path, 'standard', 'empty-repo'),
        }

        result = self.gitrepo.status(repoconf)

        self.assertEqual(result['status'], 'NOT_CLONED')

    def test_status_reports_empty_remote(self):
        repoconf = {
            'repo': self.remotes['empty_repo'],
            'path': os.path.join(self.scenarios_path, 'standard', 'empty-repo'),
        }

        update_result = self.gitrepo.update(repoconf)
        status_result = self.gitrepo.status(dict(repoconf))

        self.assertEqual(update_result['status'], 'CLONED')
        self.assertEqual(status_result['status'], 'EMPTY')

    def test_status_detects_mismatched_remote(self):
        repoconf = {
            'repo': self.remotes['empty_repo'],
            'path': os.path.join(self.scenarios_path, 'standard', 'empty-repo'),
        }
        self.gitrepo.update(repoconf)
        repoconf['repo'] = self.remotes['different_remote']

        result = self.gitrepo.status(repoconf)

        self.assertEqual(result['status'], 'WRONG_REMOTE')
        self.assertIn(self.remotes['different_remote'], result['extra_info'])

    def test_status_reports_requested_branch_update(self):
        repoconf = {
            'repo': self.remotes['simplest_repo'],
            'path': os.path.join(self.scenarios_path, 'standard', 'simplest-git-subrepos'),
        }
        self.gitrepo.update(repoconf)
        repoconf.update({'gitref_type': 'branch', 'branch': 'python-example'})

        result = self.gitrepo.status(repoconf)

        self.assertEqual(result['status'], 'PENDING_UPDATE')
        self.assertEqual(result['from'], 'master')
        self.assertEqual(result['to'], 'python-example')

    def test_status_reports_up_to_date_repository(self):
        repoconf = {
            'repo': self.remotes['simplest_repo'],
            'path': os.path.join(self.scenarios_path, 'standard', 'simplest-git-subrepos'),
        }
        self.gitrepo.update(repoconf)

        result = self.gitrepo.status(repoconf)

        self.assertEqual(result['status'], 'UP_TO_DATE')