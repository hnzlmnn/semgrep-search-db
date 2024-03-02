#      Semgrep-Search Database (sgs-db)
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
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator, Optional
from zipfile import ZipFile, ZipInfo

import requests
from ruamel.yaml import YAML
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from .rule import Rule, is_valid
from .util import human_readable, logger

RE_FILENAME = re.compile(r'^.*\.ya?ml$')
RE_TESTFILE = re.compile(r'^.*\.test\.ya?ml$')


@dataclass
class Repository:
    id: str
    name: str
    url: str


class RepositoryProcessor:
    def __init__(self, repo: Repository, args: argparse.Namespace) -> None:
        self.repo = repo
        self.args = args

        self.success = 0
        self.ignored = 0
        self.exceptions = 0
        self.missing_rules = 0
        self.invalid = 0

    def _download_zip(self, repo: Repository) -> ZipFile:
        filename = Path(f'cache/{repo.id}.zip')
        filename.parent.mkdir(exist_ok=True, parents=True)

        if not self.args.cache or not filename.exists():
            r = requests.get(repo.url, timeout=30)
            r.raise_for_status()
            with filename.open('wb+') as f:
                f.write(r.content)

        return ZipFile(filename)

    def _get_path(self, file: ZipInfo) -> Optional[Path]:
        if file.is_dir():
            self.ignored += 1
            return None

        if not RE_FILENAME.match(file.filename) or RE_TESTFILE.match(file.filename):
            if self.args.verbose > 1:
                logger.debug('Ignoring due to file name: %s', file.filename)
            self.ignored += 1
            return None

        path = Path(file.filename).relative_to(Path(file.filename).parents[-2])
        if any(d.startswith('.') for d in path.parts):
            if self.args.verbose > 1:
                logger.debug('Ignoring hidden file: %s', path)
            self.ignored += 1
            return None

        return path

    def _load_file(self, file: ZipInfo, path: Path, archive: ZipFile) -> Optional[dict]:
        data = YAML(typ='rt').load(archive.open(file, 'r').read().decode())
        if 'rules' not in data:
            if not self.args.quiet:
                logger.warning('Found file without "rules" section: %s', path)
            self.missing_rules += 1
            return None
        return data

    def _process_rules(self, data: dict, path: Path) -> Generator[Rule, None, None]:
        for rule in data['rules']:
            if not is_valid(rule):
                if not self.args.quiet:
                    logger.warning('Found invalid rule within file: %s', path)
                self.invalid += 1
                continue
            self.success += 1
            yield Rule.from_file(self.repo.id, rule)

    def iter_rules(self) -> Generator[Rule, None, None]:
        archive = self._download_zip(self.repo)

        files = archive.filelist
        if self.args.progress:
            files = tqdm(archive.filelist, desc=f'Processing {self.repo.name}')

        start_time = datetime.now(timezone.utc)
        with logging_redirect_tqdm([logger]):
            for file in files:
                try:
                    path = self._get_path(file)
                    if not path:
                        continue

                    data = self._load_file(file, path, archive)
                    if not data:
                        continue

                    yield from self._process_rules(data, path)
                except Exception:
                    self.exceptions += 1

        elapsed_time = datetime.now(timezone.utc) - start_time
        logger.info('Finished loading %s in %s [Ignored: %d, Errors: %d, Successful: %d]',
                    self.repo.name, human_readable(elapsed_time), self.ignored,
                    self.exceptions + self.missing_rules + self.invalid, self.success)
