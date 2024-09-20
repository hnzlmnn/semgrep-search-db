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
import enum
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sgsdb.parsing.model import ParsingResult


class ResultStatus(enum.Enum):
    SUCCESS = 0
    IGNORED = 1
    EXCEPTION = 2
    MISSING_RULE = 3
    INVALID_RULE = 4


@dataclass
class ParserStats:
    success: int = 0
    ignored: int = 0
    exceptions: int = 0
    missing_rules: int = 0
    invalid: int = 0

    def update(self, status: ResultStatus) -> None:
        if status == ResultStatus.SUCCESS:
            self.success += 1
        elif status == ResultStatus.IGNORED:
            self.ignored += 1
        elif status == ResultStatus.EXCEPTION:
            self.exceptions += 1
        elif status == ResultStatus.MISSING_RULE:
            self.missing_rules += 1
        elif status == ResultStatus.INVALID_RULE:
            self.invalid += 1
        else:
            raise ValueError(f'Invalid result status: {status}')

    def register(self, result: 'ParsingResult') -> None:
        if result.status is None:
            return
        for res in result.status:
            self.update(res)
