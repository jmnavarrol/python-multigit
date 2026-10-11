# -*- coding: utf-8 -*-

"""Compatibility shim for CLI package subrepofile implementation.

Canonical YAML parsing/validation behavior is owned by ``multigit_lib.subrepofile``.
"""

from multigit_lib.subrepofile import Subrepofile, SubrepofileError  # type: ignore  # noqa: E402

__all__ = ['Subrepofile', 'SubrepofileError']
