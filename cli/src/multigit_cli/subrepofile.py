import errno
import importlib.resources as pkg_resources
import os

import yaml
from cerberus import Validator, schema
from colorama import init


class Subrepofile:
    """Load and validate a CLI-owned subrepos YAML file."""

    def __init__(self):
        init(autoreset=True)
        try:
            with pkg_resources.path(__package__, 'subrepos_schema.yaml') as schema_path:
                with open(schema_path, 'r', encoding='utf-8') as schema_file:
                    try:
                        yaml_rules = yaml.safe_load(schema_file)
                    except yaml.parser.ParserError as error:
                        raise SubrepofileError(
                            f"Malformed schema file 'subrepos_schema.yaml' - {error}",
                            errno=errno.EINVAL,
                        )
        except FileNotFoundError as error:
            raise SubrepofileError(
                f"Unable to load 'subrepos_schema.yaml':\n{error}",
                errno=errno.ENOENT,
            )

        try:
            self.yaml_validator = Validator(yaml_rules)
        except (schema.SchemaError, TypeError) as error:
            raise SubrepofileError(
                f"Invalid YAML schema at '{schema_path}'.\n\t{error}",
                errno=errno.EINVAL,
            )

    def load(self, subrepos_file):
        """Load, validate, and normalize entries from a subrepos file."""
        try:
            with open(subrepos_file, 'r', encoding='utf-8') as config_file:
                try:
                    config_map = yaml.safe_load(config_file)
                except (yaml.scanner.ScannerError, yaml.parser.ParserError) as error:
                    raise SubrepofileError(
                        f"malformed YAML in subrepos file '{subrepos_file}':\n{error}",
                        errno=errno.EINVAL,
                    )
        except PermissionError as error:
            raise SubrepofileError(
                f"trying to load '{subrepos_file}'\n\t{error}",
                errno=errno.EPERM,
            )

        if not config_map:
            return None

        if not self.yaml_validator.validate(config_map):
            raise SubrepofileError(
                f"malformed YAML in subrepos file '{subrepos_file}':\n"
                f"\t{self.yaml_validator.errors}",
                errno=errno.EINVAL,
            )

        subrepo_list = config_map['subrepos']
        for subrepo in subrepo_list:
            subrepo['path'] = os.path.realpath(
                os.path.join(os.path.dirname(subrepos_file), subrepo['path'])
            )
            gitref_type = {'branch', 'tag', 'commit'}.intersection(subrepo)
            subrepo['gitref_type'] = next(iter(gitref_type), None)

        return subrepo_list


class SubrepofileError(Exception):
    """Configuration-loading error with a suggested process exit code."""

    def __init__(self, message='error while operating subrepos file', errno=errno.EINVAL):
        super().__init__(message)
        self.errno = errno