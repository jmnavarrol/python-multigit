# -*- coding: utf-8 -*-

"""Compatibility shim for CLI package gitrepo implementation.

Canonical repository/domain behavior is owned by ``multigit_lib.gitrepo``.
"""

import os
import sys


def _ensure_lib_src_on_path():
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    lib_src = os.path.join(repo_root, 'lib', 'src')
    if os.path.isdir(lib_src) and lib_src not in sys.path:
        sys.path.insert(0, lib_src)


_ensure_lib_src_on_path()

from multigit_lib.gitrepo import Gitrepo  # type: ignore  # noqa: E402

__all__ = ['Gitrepo']
