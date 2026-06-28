# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath('../src'))

from multigit_lib import __version__

project = 'multigit-lib'
copyright = '2021-2026, Jesús M. Navarro'
author = 'Jesús M. Navarro'
release = __version__

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
