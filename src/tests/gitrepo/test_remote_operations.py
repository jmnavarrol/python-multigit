# -*- coding: utf-8 -*-
# Tests the Gitrepo class: remote operations

# Import stuff
from .test_gitrepo import TestGitrepo
from multigit import Gitrepo

from git import Repo
import os

# Subclasses so it gets parent's setUp and tearDown
class TestGitrepoRemote(TestGitrepo):

# https://github.com/jmnavarrol/python-multigit/issues/11
# multigit should return to the default branch
# even if current checkout happens to be on same commit
	def test_different_branches_same_commit(self):
		print("TEST: 'test_different_branches_same_commit'")
		# prepares a suitable configuration
		repoconf = {}
		repoconf['repo'] = 'git@github.com:jmnavarrol/python-multigit-standard-repo.git'
		repoconf['path'] = os.path.join(self.scenarios_path, 'standard/standard-repo')
		
		# First, let's clone the repo
		result = self.gitrepo.update(repoconf)
		print(str(result))
		
		# get current branch's name
		repo = Repo(repoconf['path'])
		original_branch_name = repo.head.ref.name
		
		# Create and push a new branch (same commit than default's tip)
		repo = Repo(repoconf['path'])
		test_commit_branch = repo.create_head('test_commit')
		test_commit_branch.checkout()
		repo.git.push('origin', 'test_commit')
		
		# Run multigit on default branch and see what happens
		result = self.gitrepo.update(repoconf)
		print(str(result))
		current_branch_name = repo.head.ref.name
		# Branch should return to its original value
		self.assertEqual(current_branch_name, original_branch_name)
		
		# Cleansing: delete remote branch
		repo.git.push('origin', ':test_commit')
