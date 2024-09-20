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
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

from sgsdb.parsing.statistic import ResultStatus
from sgsdb.rule import Rule

if TYPE_CHECKING:
    from sgsdb.repository import Repository


@dataclass
class ParsingResult:
    repository: 'Repository'
    path: str
    content: str
    status: List[ResultStatus] = field(default_factory=list)
    data: dict | None = None
    rules: List[Rule] = field(default_factory=list)


class RuleMode(enum.Enum):
    SEARCH = 'search'
    TAINT = 'taint'
    JOIN = 'join'  # Experimental
    EXTRACT = 'extract'  # Experimental
