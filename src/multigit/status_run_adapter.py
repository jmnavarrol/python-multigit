# -*- coding: utf-8 -*-

import os
import sys

from .cli_error_translation import exit_from_orchestration_error
from .cli_rendering import print_subrepo_status


def _load_multigit_lib_status_orchestrator():
    """Resolve multigit_lib status orchestration function and error class."""
    try:
        from multigit_lib.subrepos_orchestration import (  # type: ignore
            process_subrepos,
            SubreposOrchestrationError,
        )
        return process_subrepos, SubreposOrchestrationError
    except ModuleNotFoundError:
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        lib_src = os.path.join(repo_root, 'lib', 'src')
        if os.path.isdir(lib_src) and lib_src not in sys.path:
            sys.path.insert(0, lib_src)
        from multigit_lib.subrepos_orchestration import (  # type: ignore
            process_subrepos,
            SubreposOrchestrationError,
        )
        return process_subrepos, SubreposOrchestrationError


def process_subrepos_with_adapter(base_path, report_only, subrepos_filename):
    """Run status/run paths through multigit_lib while preserving CLI output semantics."""
    process_subrepos, orchestration_error = _load_multigit_lib_status_orchestrator()
    try:
        processed_subrepos = process_subrepos(
            base_path=base_path,
            subrepos_filename=subrepos_filename,
            report_only=report_only,
        )
    except orchestration_error as error:
        exit_from_orchestration_error(error, base_path, subrepos_filename)

    for current_subrepo in processed_subrepos:
        print_subrepo_status(current_subrepo)

    return None
