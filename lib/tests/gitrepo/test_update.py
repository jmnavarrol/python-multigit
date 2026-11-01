import os

from git import Repo

from .test_gitrepo import GitrepoTestCase


class TestGitrepoUpdate(GitrepoTestCase):
    def test_update_rejects_non_repository_directory(self):
        repoconf = {'path': os.path.join(self.scenarios_path, 'standard')}

        result = self.gitrepo.update(repoconf)

        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('not a valid git sandbox', result['extra_info'])

    def test_update_reports_missing_requested_branch(self):
        repoconf = {
            'repo': self.remotes['simplest_repo'],
            'path': os.path.join(self.scenarios_path, 'standard', 'simplest-git-subrepos'),
            'branch': 'nonexistent',
            'gitref_type': 'branch',
        }

        result = self.gitrepo.update(repoconf)

        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('nonexistent', result['extra_info'])

    def test_update_rejects_checked_out_local_branch_missing_on_remote(self):
        repoconf = {
            'repo': self.remotes['simplest_repo'],
            'path': os.path.join(self.scenarios_path, 'standard', 'simplest-git-subrepos'),
        }
        self.gitrepo.update(repoconf)
        repo = Repo(repoconf['path'])
        repo.create_head('new_branch').checkout()
        repoconf.update({'branch': 'new_branch', 'gitref_type': 'branch'})

        result = self.gitrepo.update(repoconf)

        self.assertEqual(result['status'], 'WRONG_REMOTE')
        self.assertIn('origin/new_branch', result['extra_info'])

    def test_update_reports_missing_tracking_branch(self):
        repoconf = {
            'repo': self.remotes['simplest_repo'],
            'path': os.path.join(self.scenarios_path, 'standard', 'simplest-git-subrepos'),
        }
        self.gitrepo.update(repoconf)
        Repo(repoconf['path']).create_head('new_branch')
        repoconf.update({'branch': 'new_branch', 'gitref_type': 'branch'})

        result = self.gitrepo.update(repoconf)

        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('tracking information', result['extra_info'])

    def test_update_clones_repository(self):
        repoconf = {
            'repo': self.remotes['simplest_repo'],
            'path': os.path.join(self.scenarios_path, 'standard', 'simplest-git-subrepos'),
        }

        result = self.gitrepo.update(repoconf)

        self.assertEqual(result['status'], 'CLONED')
        self.assertTrue(os.path.isdir(repoconf['path']))

    def test_update_moves_existing_clone_to_requested_branch(self):
        repoconf = {
            'repo': self.remotes['simplest_repo'],
            'path': os.path.join(self.scenarios_path, 'standard', 'simplest-git-subrepos'),
        }
        self.gitrepo.update(repoconf)
        repoconf.update({'branch': 'python-example', 'gitref_type': 'branch'})

        result = self.gitrepo.update(repoconf)

        self.assertEqual(result['status'], 'UPDATED')
        self.assertEqual(Repo(repoconf['path']).head.ref.name, 'python-example')

    def test_update_clones_at_requested_tag(self):
        remote_repo = Repo(self.remotes['standard_repo'])
        tag_commit = remote_repo.create_tag('v1.0', ref='main').commit.hexsha
        repoconf = {
            'repo': self.remotes['standard_repo'],
            'path': os.path.join(self.scenarios_path, 'standard', 'tagged-repo'),
            'tag': 'v1.0',
            'gitref_type': 'tag',
        }

        result = self.gitrepo.update(repoconf)
        cloned_repo = Repo(repoconf['path'])

        self.assertEqual(result['status'], 'CLONED')
        self.assertTrue(cloned_repo.head.is_detached)
        self.assertEqual(cloned_repo.head.commit.hexsha, tag_commit)

    def test_update_clones_at_requested_commit(self):
        commit = Repo(self.remotes['standard_repo']).commit('main').hexsha
        repoconf = {
            'repo': self.remotes['standard_repo'],
            'path': os.path.join(self.scenarios_path, 'standard', 'commit-repo'),
            'commit': commit,
            'gitref_type': 'commit',
        }

        result = self.gitrepo.update(repoconf)
        cloned_repo = Repo(repoconf['path'])

        self.assertEqual(result['status'], 'CLONED')
        self.assertTrue(cloned_repo.head.is_detached)
        self.assertEqual(cloned_repo.head.commit.hexsha, commit)

    def test_update_reports_missing_remote(self):
        repoconf = {
            'repo': self.remotes['missing_repo'],
            'path': os.path.join(self.scenarios_path, 'standard', 'empty-repo'),
        }

        result = self.gitrepo.update(repoconf)

        self.assertEqual(result['status'], 'ERROR')
        self.assertIn('doesnt-exist.git', result['extra_info'])

    def test_update_does_not_modify_dirty_repository(self):
        repoconf = {
            'repo': self.remotes['simplest_repo'],
            'path': os.path.join(self.scenarios_path, 'standard', 'simplest-git-subrepos'),
        }
        self.gitrepo.update(repoconf)
        readme_path = os.path.join(repoconf['path'], 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as readme_file:
            readme_file.write('local change\n')

        result = self.gitrepo.update(repoconf)

        self.assertEqual(result['status'], 'DIRTY')
        with open(readme_path, encoding='utf-8') as readme_file:
            self.assertEqual(readme_file.read(), 'local change\n')

    def test_update_checks_out_requested_branch(self):
        repoconf = {
            'repo': self.remotes['simplest_repo'],
            'path': os.path.join(self.scenarios_path, 'standard', 'simplest-git-subrepos'),
            'branch': 'python-example',
            'gitref_type': 'branch',
        }

        result = self.gitrepo.update(repoconf)

        self.assertEqual(result['status'], 'CLONED')
        self.assertEqual(Repo(repoconf['path']).head.ref.name, 'python-example')