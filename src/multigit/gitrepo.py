# -*- coding: utf-8 -*-

"""Compatibility shim for CLI package gitrepo implementation.

Canonical repository/domain behavior is owned by ``multigit_lib.gitrepo``.
"""

from multigit_lib.gitrepo import Gitrepo  # type: ignore  # noqa: E402

__all__ = ['Gitrepo']
