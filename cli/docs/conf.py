import os
import sys

sys.path.insert(0, os.path.abspath('../src'))

project = 'multigit CLI'
author = 'Jesús M. Navarro'
release = '0.12.0.dev5'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]

master_doc = 'index'
exclude_patterns = ['_build']
html_theme = 'alabaster'
