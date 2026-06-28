# -*- coding: utf-8 -*-

"""Compatibility shim for CLI package subrepofile implementation.

Canonical YAML parsing/validation behavior is owned by ``multigit_lib.subrepofile``.
"""

import os
import sys


def _ensure_lib_src_on_path():
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    lib_src = os.path.join(repo_root, 'lib', 'src')
    if os.path.isdir(lib_src) and lib_src not in sys.path:
        sys.path.insert(0, lib_src)


_ensure_lib_src_on_path()

from multigit_lib.subrepofile import Subrepofile, SubrepofileError  # type: ignore  # noqa: E402

__all__ = ['Subrepofile', 'SubrepofileError']
