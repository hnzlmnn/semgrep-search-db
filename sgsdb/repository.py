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
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator, Optional, IO, Tuple, Callable
from zipfile import ZipFile, ZipInfo

import requests
from ruamel.yaml import YAML
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from sgsdb.base_repo import BaseRepository
from sgsdb.rule import Rule
from sgsdb.validation import is_valid
from sgsdb.util import logger, human_readable

RE_FILENAME = re.compile(r'^.*\.ya?ml$')
RE_TESTFILE = re.compile(r'^.*\.test\.ya?ml$')


@dataclass
class Repository(BaseRepository):
    @staticmethod
    def from_config(id: str, type: str, **kwargs: dict) -> 'Repository':
        match type:
            case 'github':
                return GithubOrigin(id=id, **kwargs)
            case 'gitlab':
                return GitlabOrigin(id=id, **kwargs)

    def get_files(self, args: argparse.Namespace) -> list[Path]:
        raise NotImplementedError

    def filter_filename(self, args: argparse.Namespace, filename: str) -> bool:
        if not RE_FILENAME.match(filename) or RE_TESTFILE.match(filename):
            if args.verbose > 1:
                logger.debug('Ignoring due to file name: %s', filename)
            return False

        path = Path(filename).relative_to(Path(filename).parents[-2])
        if any(d.startswith('.') for d in path.parts):
            if args.verbose > 1:
                logger.debug('Ignoring hidden file: %s', path)
            return False

        return True

    def load_file(self, args: argparse.Namespace, stream: IO[bytes], path: str) -> Optional[dict]:
        data = YAML(typ='rt').load(stream.read().decode())
        if 'rules' not in data:
            if not args.quiet:
                logger.warning('Found file without "rules" section: %s', path)
            return None
        return data

    def process_rules(self, args: argparse.Namespace, data: dict, path: str) -> Generator[Rule, None, None]:
        for rule in data['rules']:
            if not is_valid(rule):
                if not args.quiet:
                    logger.warning('Found invalid rule within file: %s', path)
                yield None
                continue
            yield Rule.from_file(self, rule)

    def get_iter(self, args: argparse.Namespace, stats: Callable[[str], None]) -> Tuple[
        int, Callable[[tqdm], Generator[Rule, None, None]]]:
        raise NotImplementedError

    def iter_rules(self, args: argparse.Namespace) -> Generator[Rule, None, None]:
        stats = {
            'success': 0,
            'ignored': 0,
            'exceptions': 0,
            'missing_rules': 0,
            'invalid': 0,
        }

        def update_stats(key: str) -> None:
            stats[key] += 1

        length, iterator = self.get_iter(args, update_stats)

        progress = None
        if args.progress:
            progress = tqdm(total=length, desc=f'Processing {self.name}')

        start_time = datetime.now(timezone.utc)

        with logging_redirect_tqdm([logger]):
            yield from iterator(progress)

        if progress:
            progress.close()

        elapsed_time = datetime.now(timezone.utc) - start_time
        logger.info('Finished loading %s in %s [Ignored: %d, Errors: %d, Successful: %d]',
                    self.name, human_readable(elapsed_time), stats['ignored'],
                    stats['exceptions'] + stats['missing_rules'] + stats['invalid'], stats['success'])


@dataclass
class GitOrigin(Repository):
    repo: str
    branch: str

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            'repo': self.repo,
            'branch': self.branch,
        }

    def get_download_url(self) -> str:
        raise NotImplementedError

    def _download_zip(self, args: argparse.Namespace) -> ZipFile:
        filename = Path(f'cache/{self.id}.zip')
        filename.parent.mkdir(exist_ok=True, parents=True)

        if not args.cache or not filename.exists():
            r = requests.get(self.get_download_url(), timeout=30)
            r.raise_for_status()
            with filename.open('wb+') as f:
                f.write(r.content)

        return ZipFile(filename)

    def filter_file(self, args: argparse.Namespace, file: ZipInfo) -> bool:
        if file.is_dir():
            return False

        if not self.filter_filename(args, file.filename):
            return False
        return True

    def get_iter(self, args: argparse.Namespace, stats: Callable[[str], None]) -> Tuple[
        int, Callable[[tqdm], Generator[Rule, None, None]]]:
        archive = self._download_zip(args)

        def _iter(progress: tqdm) -> Generator[Rule, None, None]:
            for file in archive.filelist:
                try:
                    if not self.filter_file(args, file):
                        stats('ignored')
                        continue

                    data = self.load_file(args, archive.open(file, 'r'), file.filename)
                    if data is None:
                        stats('missing_rules')
                        continue

                    for rule in self.process_rules(args, data, file.filename):
                        if rule is None:
                            stats('invalid')
                        else:
                            stats('success')
                            yield rule
                except Exception as e:
                    logger.debug(str(e), exc_info=e)
                    stats('exceptions')
                finally:
                    if progress is not None:
                        progress.update(1)

        return len(archive.filelist), _iter


@dataclass
class GithubOrigin(GitOrigin):
    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            'type': 'GitHub',
            'url': f'https://github.com/{self.repo}',
        }

    def get_download_url(self) -> str:
        return f'https://github.com/{self.repo}/archive/refs/heads/{self.branch}.zip'


@dataclass
class GitlabOrigin(GitOrigin):
    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            'type': 'GitLab',
            'url': f'https://gitlab.com/{self.repo}',
        }

    def get_download_url(self) -> str:
        return f'https://gitlab.com/{self.repo}/-/archive/{self.branch}/{self.repo.split("/")[-1]}-{self.branch}.zip'

