# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

import re
from setuptools import setup

version = re.search('^__version__\s*=\s*"(.*)"', open('multigit/multigit.py').read(), re.M).group(1)

with open('README.md', 'rb') as f:
	long_descr = f.read().decode('utf-8')
	
setup(
	name = 'multigit',
	packages = ['multigit'],
	entry_points = {
		"console_scripts": ['multigit = multigit.multigit:main']
	},
	version = version,
	description = "Manages git repos within git repos.",
	long_description = long_descr,
	long_description_content_type="text/markdown",
	author = 'Jesús M. Navarro',
	author_email = 'jesusmnavarrolopez@gmail.com',
	url = 'https://github.com/jmnavarrol/python-multigit',
	license = 'GPLv3',
	install_requires = [
		'colorama==0.4.4',
		'GitPython==3.1.20',
		'PyYAML==5.4.1',
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Build Tools',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Programming Language :: Python :: 3',
	]
)
