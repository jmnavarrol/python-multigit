# -*- coding: utf-8 -*-

"""
**multigit** library provides reusable Git repository operations.

Manages multiple git repositories with recursive subrepo support.

:package: multigit-lib
:author: `Jesús M. Navarro <mailto:jesusmnavarrolopez@gmail.com>`_
:license: `GNU General Public License v3.0 <https://github.com/jmnavarrol/python-multigit/blob/main/LICENSE>`_
:source: https://github.com/jmnavarrol/python-multigit
"""

from .__about__ import __version__
from .gitrepo import Gitrepo
from .exceptions import SubrepofileError

__all__ = [
	'__version__',
	'Gitrepo',
	'SubrepofileError',
]
