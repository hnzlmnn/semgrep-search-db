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
import dataclasses
from dataclasses import dataclass
from io import StringIO
from typing import Optional

from ruamel.yaml import CommentedMap, CommentedSeq, YAML

from .base_repo import BaseRepository
from .util import fix_languages, remove_comments


@dataclass
class Rule:
    source: str
    id: str
    severity: str
    languages: list[str]
    category: Optional[str]
    _data: dict
    content: str

    @staticmethod
    def from_file(source: BaseRepository, data: dict, path: str) -> 'Rule':
        # Remove all comments as their indentation might be broken
        data = remove_comments(data)

        # Add metadata
        data.setdefault('metadata', CommentedMap())
        data['metadata'].setdefault('semgrep.dev', CommentedMap())
        data['metadata']['semgrep.dev'].setdefault('rule', CommentedMap())
        data['metadata']['semgrep.dev']['rule']['origin'] = source.name

        data['metadata'].setdefault('semgrep-search', CommentedMap())
        data['metadata']['semgrep-search']['id'] = source.id
        data['metadata']['semgrep-search']['name'] = source.name
        data['metadata']['semgrep-search']['source'] = repr(source)
        data['metadata']['semgrep-search']['file'] = source.filepath(path)

        buf = StringIO()
        YAML(typ='rt').dump(data, buf)

        return Rule(
            source.id,
            data['id'],
            data.get('severity', None),
            list(fix_languages(data['languages'])),
            data.get('metadata', {}).get('category', None),
            data,
            buf.getvalue(),
        )

    def asdict(self) -> dict:
        return {key: value for key, value in dataclasses.asdict(self).items() if not key.startswith('_')}

    @property
    def full_content(self) -> str:
        buf = StringIO()
        YAML(typ='rt').dump(CommentedMap({'rules': CommentedSeq([self._data])}), buf)
        return buf.getvalue()
