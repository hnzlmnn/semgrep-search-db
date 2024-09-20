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
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator, Tuple, Callable
from zipfile import ZipFile

import requests
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from sgsdb.base_repo import BaseRepository
from sgsdb.parsing.model import ParsingResult
from sgsdb.parsing.parallel import CloseableQueue, Closed
from sgsdb.parsing.processing import RuleProcessor
from sgsdb.parsing.statistic import ParserStats
from sgsdb.rule import Rule
from sgsdb.util import logger, human_readable


@dataclass
class Repository(BaseRepository):
    @staticmethod
    def from_config(id: str, type: str, **kwargs: dict) -> 'Repository':
        match type:
            case 'github':
                return GithubOrigin(id=id, **kwargs)
            case 'gitlab':
                return GitlabOrigin(id=id, **kwargs)

    def get_paths(self, args: argparse.Namespace) -> Tuple[int, Callable[[], Generator[tuple[str, str], None, None]]]:
        raise NotImplementedError

    def iter_rules(self, args: argparse.Namespace) -> Generator[Rule, None, None]:
        start_time = datetime.now(timezone.utc)

        files_count, files_iter = self.get_paths(args)

        stats = ParserStats()
        rules = CloseableQueue[ParsingResult]()
        processor = RuleProcessor(args, self)

        thread = processor.start(files_iter(), rules)

        progress = None
        if args.progress:
            progress = tqdm(total=files_count, desc=f'Processing {self.name}')

        with logging_redirect_tqdm([logger]):
            try:
                while True:
                    result = rules.get()
                    stats.register(result)
                    yield from result.rules
                    if progress:
                        progress.update(1)
            except Closed:
                pass

        # Wait for the processing thread to conclude
        thread.join()

        if progress:
            progress.close()

        elapsed_time = datetime.now(timezone.utc) - start_time
        logger.info('Finished loading %s in %s [Ignored: %d, Errors: %d, Successful: %d]', self.name,
                    human_readable(elapsed_time), stats.ignored, stats.exceptions + stats.missing_rules + stats.invalid,
                    stats.success)


@dataclass
class GitOrigin(Repository):
    repo: str
    branch: str

    def to_dict(self) -> dict:
        return {**super().to_dict(), 'repo': self.repo, 'branch': self.branch}

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

    def get_paths(self, args: argparse.Namespace) -> Tuple[int, Callable[[], Generator[tuple[str, str], None, None]]]:
        archive = self._download_zip(args)

        paths = list(filter(lambda file: not file.is_dir(), archive.filelist))

        def _iter() -> Generator[tuple[str, str], None, None]:
            for file in paths:
                with archive.open(file, 'r') as fin:
                    yield file.filename, fin.read()

        return len(paths), _iter


@dataclass
class GithubOrigin(GitOrigin):
    @property
    def url(self) -> str:
        return f'https://github.com/{self.repo}'

    def to_dict(self) -> dict:
        return {**super().to_dict(), 'type': 'GitHub', 'url': self.url}

    def get_download_url(self) -> str:
        return f'{self.url}/archive/refs/heads/{self.branch}.zip'

    def __repr__(self) -> str:
        return self.url

    def filepath(self, path: str) -> str:
        return f'{self.url}/blob/{self.branch}/{Path(path).relative_to(Path(path).parts[0])}'


@dataclass
class GitlabOrigin(GitOrigin):
    @property
    def url(self) -> str:
        return f'https://gitlab.com/{self.repo}'

    def to_dict(self) -> dict:
        return {**super().to_dict(), 'type': 'GitLab', 'url': self.url}

    def get_download_url(self) -> str:
        return f'{self.url}/-/archive/{self.branch}/{self.repo.split("/")[-1]}-{self.branch}.zip'

    def __repr__(self) -> str:
        return self.url

    def filepath(self, path: str) -> str:
        return f'{self.url}/-/blob/{self.branch}/{Path(path).relative_to(Path(path).parts[0])}'
