# -*- coding: utf-8 -*-
"""Utilities to build local git remotes for offline tests."""

import os
import shutil
import tempfile

from git import Repo


def _ensure_parent(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _write_file(path, content):
    with open(path, 'w', encoding='utf-8') as handler:
        handler.write(content)


def _configure_repo_identity(repo):
    with repo.config_writer() as config:
        config.set_value('user', 'name', 'multigit-tests')
        config.set_value('user', 'email', 'multigit-tests@example.com')


def _commit_file(repo, filename, content, message):
    file_path = os.path.join(repo.working_tree_dir, filename)
    _write_file(file_path, content)
    repo.index.add([filename])
    repo.index.commit(message)


def _set_remote_head(remote_path, branch):
    remote_repo = Repo(remote_path)
    remote_repo.git.symbolic_ref('HEAD', f'refs/heads/{branch}')


def create_empty_bare_remote(remote_path):
    _ensure_parent(remote_path)
    Repo.init(remote_path, bare=True)


def create_seeded_bare_remote(remote_path, default_branch, extra_branches):
    _ensure_parent(remote_path)
    Repo.init(remote_path, bare=True)

    work_path = tempfile.mkdtemp(prefix='multigit-seed-')
    try:
        work_repo = Repo.init(work_path)
        _configure_repo_identity(work_repo)

        # Initial commit
        _commit_file(work_repo, 'README.md', 'seed\n', 'Initial commit')
        work_repo.git.branch('-M', default_branch)
        work_repo.create_remote('origin', remote_path)
        work_repo.git.push('--set-upstream', 'origin', default_branch)

        # Extra branches with additional commits
        for branch_name in extra_branches:
            branch = work_repo.create_head(branch_name)
            branch.checkout()
            _commit_file(
                work_repo,
                f'{branch_name}.txt',
                f'branch: {branch_name}\n',
                f'Commit on {branch_name}',
            )
            work_repo.git.push('--set-upstream', 'origin', branch_name)

        work_repo.heads[default_branch].checkout()
        _set_remote_head(remote_path, default_branch)
    finally:
        shutil.rmtree(work_path)


def build_test_remotes(remotes_root):
    """Create all remotes needed by the suite and return their paths."""
    os.makedirs(remotes_root, exist_ok=True)

    remotes = {
        'simplest_repo': os.path.join(remotes_root, 'simplest-git-subrepos.git'),
        'standard_repo': os.path.join(remotes_root, 'python-multigit-standard-repo.git'),
        'empty_repo': os.path.join(remotes_root, 'python-multigit-empty-repo.git'),
        'different_remote': os.path.join(remotes_root, 'different-remote.git'),
        'missing_repo': os.path.join(remotes_root, 'doesnt-exist.git'),
    }

    create_seeded_bare_remote(
        remote_path=remotes['simplest_repo'],
        default_branch='master',
        extra_branches=['python-example'],
    )
    create_seeded_bare_remote(
        remote_path=remotes['standard_repo'],
        default_branch='main',
        extra_branches=['a-branch'],
    )
    create_empty_bare_remote(remotes['empty_repo'])
    create_seeded_bare_remote(
        remote_path=remotes['different_remote'],
        default_branch='main',
        extra_branches=[],
    )

    return remotes


def write_subrepos_file(path, entries):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as handler:
        handler.write('---\n')
        handler.write('subrepos:\n')
        for entry in entries:
            handler.write(f"- path: '{entry['path']}'\n")
            handler.write(f"  repo: '{entry['repo']}'\n")
            if 'branch' in entry:
                handler.write(f"  branch: '{entry['branch']}'\n")
