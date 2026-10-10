# -*- coding: utf-8 -*-

import errno
import sys

from .cli_rendering import print_missing_subrepos_context, print_orchestration_error


def exit_from_orchestration_error(error, base_path, subrepos_filename):
    """Translate orchestration errors to legacy CLI output and exit codes."""
    exit_code = getattr(error, 'errno', errno.EINVAL)
    if exit_code == errno.ENOENT:
        print_missing_subrepos_context(base_path, subrepos_filename)
    print_orchestration_error(error, subrepos_filename)
    sys.exit(exit_code)
