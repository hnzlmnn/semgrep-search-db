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

import argparse
from typing import Generator, TYPE_CHECKING

from ruamel.yaml import YAML

from sgsdb.parsing.model import ParsingResult
from sgsdb.parsing.statistic import ResultStatus
from sgsdb.parsing.validation import is_valid, validate_rule_file
from sgsdb.rule import Rule
from sgsdb.util import logger

if TYPE_CHECKING:
    from sgsdb.repository import Repository


class RuleParser:

    def __init__(self, args: argparse.Namespace, repo: 'Repository') -> None:
        self.args = args
        self.repo = repo

    def _load_file(self, result: ParsingResult) -> bool:
        try:
            data = YAML(typ='rt').load(result.content)
            if 'rules' not in data:
                if not self.args.quiet:
                    logger.warning('Found file without "rules" section: %s', result.path)
                result.status = [ResultStatus.MISSING_RULE]
                return False
            result.data = data
            return True
        except Exception as e:
            logger.debug(str(e), exc_info=e)
            result.status = [ResultStatus.INVALID_RULE]
        return False

    def _process_rules(self, result: ParsingResult) -> Generator[Rule, None, None]:
        for rule in result.data['rules']:
            if not is_valid(rule):
                if not self.args.quiet:
                    logger.warning('Found invalid rule within file: %s', result.path)
                result.status.append(ResultStatus.INVALID_RULE)
                continue
            try:
                yield Rule.from_file(self.repo, rule, result.path)
            except Exception as e:
                logger.debug(str(e), exc_info=e)
                result.status = [ResultStatus.EXCEPTION]

    def process(self, result: ParsingResult) -> None:
        if not self._load_file(result):
            return

        for rule in self._process_rules(result):
            try:
                if self.args.verify and not validate_rule_file(result.path, rule):
                    result.status.append(ResultStatus.INVALID_RULE)
                    continue
                result.rules.append(rule)
                result.status.append(ResultStatus.SUCCESS)
            except Exception as e:
                logger.debug(str(e), exc_info=e)
                result.status.append(ResultStatus.EXCEPTION)
