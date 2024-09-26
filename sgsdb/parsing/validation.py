#      Semgrep-Search Database
#      Copyright (C) 2024  Malte Heinzelmann
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

import subprocess
import tempfile
from typing import Type, Any, Tuple, List

from sgsdb.parsing.model import RuleMode
from sgsdb.rule import Rule
from sgsdb.util import logger


def validate_optional(rule: dict, key: str, expect_type: Type[Any]) -> bool:
    if key in rule and not isinstance(rule[key], expect_type):
        found_type = rule[key].__class__.__name__
        raise ValueError(f'wrong data type for {key} [expected: {expect_type.__name__}, found: {found_type}')
    return key in rule


def validate_any(rule: dict, keys_and_types: List[Tuple[str, Type[Any]]]) -> None:
    if not any(validate_optional(rule, key, expect_type) for key, expect_type in keys_and_types):
        raise ValueError(f'at least on of {", ".join(x[0] for x in keys_and_types)} must be provided')


def validate_key(rule: dict, key: str, expect_type: Type[Any]) -> None:
    if key not in rule:
        raise ValueError(f'missing {key}')
    if key in rule and not isinstance(rule[key], expect_type):
        found_type = rule[key].__class__.__name__
        raise ValueError(f'wrong data type for {key} [expected: {expect_type.__name__}, found: {found_type}]')


def is_valid_pattern(rule: dict) -> None:
    validate_any(rule, [('pattern', str), ('patterns', list), ('pattern-either', list), ('pattern-regex', str) ])


def is_valid(rule: dict) -> bool:
    try:
        validate_key(rule, 'id', str)
        mode = RuleMode(rule.get('mode', 'search'))
        match mode:
            case RuleMode.JOIN:
                # In join mode the language is defined on the joined rules themselves
                # TODO: How do we determine the correct languages for searching
                #       (also we need to unwrap the joined rules if linked with filenames for using them)
                logger.warning('Join rules are currently unsupported as they are an experimental feature')
                return False
            case RuleMode.TAINT:
                validate_key(rule, 'message', str)
                validate_key(rule, 'severity', str)
                validate_key(rule, 'languages', list)
                validate_optional(rule, 'pattern-sources', list)
                validate_optional(rule, 'pattern-sinks', list)
            case RuleMode.EXTRACT:
                validate_key(rule, 'languages', list)
                is_valid_pattern(rule)
                validate_key(rule, 'extract', str)
                validate_key(rule, 'dest-language', str)
            case RuleMode.SEARCH:
                validate_key(rule, 'message', str)
                validate_key(rule, 'severity', str)
                validate_key(rule, 'languages', list)
                is_valid_pattern(rule)
            case _:
                # Default catch just to make sure all enum values are handled
                raise ValueError(f'unsupported rule mode {mode}')
    except ValueError as e:
        logger.debug(str(e))
        return False

    return True


def validate_rule_file(path: str, rule: Rule) -> bool:
    with tempfile.NamedTemporaryFile(delete=True, delete_on_close=False) as fp:
        fp.write(rule.full_content.encode('utf8'))
        fp.close()

        proc = subprocess.run([  # noqa: S607, S603
            'semgrep', '--disable-version-check', '--metrics=off', '--validate', '--config', fp.name], shell=False,
            capture_output=True)

        if proc.returncode != 0:
            logger.debug(path)
            logger.debug(proc.stderr)
            return False
    return True
