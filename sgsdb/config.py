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
from pathlib import Path
from typing import Generator, Any

from sgsdb.repository import Repository
from sgsdb.util import yaml


class Configuration:
    def __init__(self, file: Path) -> None:
        with file.open('r') as fin:
            self.config: dict[str, Any] = yaml.load(fin)

    @property
    def repositories(self) -> Generator[Repository, None, None]:
        for key, value in self.config['repositories'].items():
            yield Repository.from_config(key, **value)
