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

from dataclasses import dataclass
from io import StringIO
from typing import Optional

from .base_repo import BaseRepository
from .util import yaml, fix_languages


@dataclass
class Rule:
    source: str
    id: str
    severity: str
    languages: list[str]
    category: Optional[str]
    content: str

    @staticmethod
    def from_file(source: BaseRepository, data: dict) -> 'Rule':
        data.setdefault('metadata', {})
        data['metadata'].setdefault('semgrep.dev', {})
        data['metadata']['semgrep.dev'].setdefault('rule', {})
        data['metadata']['semgrep.dev']['rule']['origin'] = source.name

        buf = StringIO()
        yaml.dump(data, buf)

        return Rule(
            source.id,
            data['id'],
            data['severity'],
            list(fix_languages(data['languages'])),
            data.get('metadata', {}).get('category', None),
            buf.getvalue(),
        )
