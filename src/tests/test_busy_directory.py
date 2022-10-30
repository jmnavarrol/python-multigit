# tests trying to clone a repository into an already busy directory

import unittest

# Other dependencies
import os, shutil

class BusyDirectory(unittest.TestCase):
	
	# sets up the environment needed for the test
	@classmethod
	def setUp(self):
		# Creates a test directory
		self.tests_dir = os.path.dirname(os.path.realpath(__file__))
		self.tmp_path = os.path.dirname(os.path.realpath(__file__)) + '/test'
		if not os.path.exists(self.tmp_path):
			os.makedirs(self.tmp_path)
			
		# Adds a custom subrepos file and contents to the test path
		shutil.copy(
			self.tests_dir + '/subrepos.empty_repo',
			os.path.join(self.tmp_path, 'subrepos')
		)
		
		
	def test_not_yet_cloned(self):
		# Should show a proper 'not cloned' message for this repository
		os.chdir(self.tmp_path)
		result = os.system('multigit --status')
		self.assertEqual(result, 0)
		
		
	def test_busy_directory(self):
		# Creates a "busy directory"
		if not os.path.exists(self.tmp_path + '/empty-repo'):
			os.makedirs(self.tmp_path + '/empty-repo')
		# ...with a file within
		with open(self.tmp_path + '/empty-repo/readme.txt', 'w') as f:
			f.write('Simple text file')
			
		# Should throw an ERROR message since git won't be able to clone to an already in use dir
		os.chdir(self.tmp_path)
		result = os.system('multigit --run')
		self.assertEqual(result, 0)
		
		
	@classmethod
	def tearDown(self):
		# clean up after the test
		shutil.rmtree(self.tmp_path)
		
		
if __name__ == '__main__':
	unittest.main()
	
