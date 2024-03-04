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

from typing import Type, Any

from sgsdb.util import logger


def validate_optional(rule: dict, key: str, expect_type: Type[Any]) -> None:
    if key in rule and not isinstance(rule[key], expect_type):
        found_type = rule[key].__class__.__name__
        raise ValueError(f'wrong data type for {key} [expected: {expect_type.__name__}, found: {found_type}')


def is_valid_taint(rule: dict) -> None:
    validate_optional(rule, 'pattern-sources', list)
    validate_optional(rule, 'pattern-sinks', list)


def is_valid(rule: dict) -> bool:
    try:
        if rule.get('id') is None:
            raise ValueError('missing id')
        if rule.get('message') is None:
            raise ValueError('missing message')
        if rule.get('severity') is None:
            raise ValueError('missing severity')
        if rule.get('languages') is None:
            raise ValueError('missing languages')

        if rule.get('mode') == 'taint':
            is_valid_taint(rule)
        else:
            validate_optional(rule, 'pattern', str)
            validate_optional(rule, 'patterns', list)
            validate_optional(rule, 'patter-either', list)
            validate_optional(rule, 'pattern-regex', str)
    except ValueError as e:
        logger.debug(str(e))
        return False

    return True
