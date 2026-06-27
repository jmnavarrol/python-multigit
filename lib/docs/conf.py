# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath('../src'))

from multigit_lib import __version__

project = 'multigit-lib'
author = 'Jesús M. Navarro'
release = __version__

extensions = [
    'sphinx.ext.autodoc',
]

templates_path = ['_templates']
exclude_patterns = []

html_static_path = ['_static']
