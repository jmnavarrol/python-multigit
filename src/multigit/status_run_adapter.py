# -*- coding: utf-8 -*-

from .cli_error_translation import exit_from_orchestration_error
from .cli_rendering import print_subrepo_status


def _load_multigit_lib_status_orchestrator():
    """Resolve multigit_lib status orchestration function and error class."""
    from multigit_lib.subrepos_orchestration import (  # type: ignore
        iter_process_subrepos,
        SubreposOrchestrationError,
    )
    return iter_process_subrepos, SubreposOrchestrationError


def process_subrepos_with_adapter(base_path, report_only, subrepos_filename):
    """Run status/run paths through multigit_lib while preserving CLI output semantics."""
    iter_process_subrepos, orchestration_error = _load_multigit_lib_status_orchestrator()
    try:
        processed_subrepos = iter_process_subrepos(
            base_path=base_path,
            subrepos_filename=subrepos_filename,
            report_only=report_only,
        )
        for current_subrepo in processed_subrepos:
            print_subrepo_status(current_subrepo)
    except orchestration_error as error:
        exit_from_orchestration_error(error, base_path, subrepos_filename)

    return None
