# -*- coding: utf-8 -*-

import argparse
import os
import sys

from . import __version__
from .cli_error_translation import exit_from_orchestration_error
from .cli_rendering import print_subrepo_status

SUBREPOS_FILE = 'subrepos'


def _load_orchestrator():
    """Load CLI orchestration while reporting a missing library dependency clearly."""
    try:
        from .subrepos_orchestration import iter_process_subrepos, SubreposOrchestrationError
        return iter_process_subrepos, SubreposOrchestrationError
    except ModuleNotFoundError as exc:
        if exc.name == 'multigit_lib':
            raise RuntimeError(
                "The multigit CLI requires the installed 'multigit-lib' dependency. "
                "Install it before running the command."
            ) from exc
        raise


def _process_subrepos(base_path, report_only):
    iter_process_subrepos, orchestration_error = _load_orchestrator()
    try:
        for current_subrepo in iter_process_subrepos(
            base_path=base_path,
            subrepos_filename=SUBREPOS_FILE,
            report_only=report_only,
        ):
            print_subrepo_status(current_subrepo)
    except orchestration_error as err:
        exit_from_orchestration_error(err, base_path, SUBREPOS_FILE)


def main(argv=None):
    """Process CLI arguments and dispatch to the library-backed workflow."""
    parser = argparse.ArgumentParser(
        prog='multigit',
        description='Manages git repos within git repos.',
        add_help=False,
    )

    main_parser = parser.add_mutually_exclusive_group()
    main_parser.add_argument('-h', '--help', action='store_true', help="Shows this help.")
    main_parser.add_argument('-V', '--version', action='store_true', help="Shows the CLI version and quits.")
    main_parser.add_argument('-r', '--run', action='store_true', help="Recursively processes 'subrepos' files found.")
    main_parser.add_argument('-s', '--status', action='store_true', help="Shows repositories' current status.")

    args = parser.parse_args(argv)

    if len(sys.argv[1:] if argv is None else argv) > 0:
        if args.help:
            print(f"{parser.prog} ({__version__})")
            parser.print_help()
            return 0
        if args.version:
            print(f"{parser.prog} {__version__}")
            return 0

        _process_subrepos(base_path=os.getcwd(), report_only=args.status)
        return 0

    print(f"{parser.prog} ({__version__}): arguments required.")
    parser.print_help()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
