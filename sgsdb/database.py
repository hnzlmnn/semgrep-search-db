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
import sys
from datetime import datetime, timezone
from typing import Generator

from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from sgsdb.repository import Repository
from sgsdb.processor import RepositoryProcessor
from sgsdb.rule import Rule
from sgsdb.util import logger, human_readable, generate_metdata

REPOSITORIES = [
    Repository('semgrep', 'Semgrep Registry',
               'https://github.com/semgrep/semgrep-rules/archive/refs/heads/develop.zip'),
    Repository('gitlab', 'GitLab SAST',
               'https://gitlab.com/gitlab-org/security-products/sast-rules/-/archive/main/sast-rules-main.zip'),
    Repository('0xdea', '0xdea Rules',
               'https://github.com/0xdea/semgrep-rules/archive/refs/heads/main.zip'),
    Repository('trailofbits', 'Trail of Bits Rules',
               'https://github.com/trailofbits/semgrep-rules/archive/refs/heads/main.zip'),
    Repository('elttam', 'Elttam Rules',
               'https://github.com/elttam/semgrep-rules/archive/refs/heads/main.zip'),
]


def collect(args: argparse.Namespace) -> Generator[Rule, None, None]:
    for repo in REPOSITORIES:
        try:
            yield from RepositoryProcessor(repo, args).iter_rules()
        except Exception as e:
            logger.debug(str(e), exc_info=e)
            logger.error('Exception during repository parsing')
            sys.exit(1)


def build_db(args: argparse.Namespace) -> int:
    db = TinyDB(args.DATABASE, storage=CachingMiddleware(JSONStorage))

    try:
        meta = db.table('meta')
        meta.truncate()
        metadata = generate_metdata()
        if args.verbose > 1:
            logger.debug('Using metadata: %s', ', '.join(f'{k}: {v}' for k, v in metadata.items()))
        meta.insert(metadata)

        rules = db.table('rules')
        if not args.append:
            rules.truncate()

        ids = set()

        start_time = datetime.now(timezone.utc)

        for rule in collect(args):
            if rule.id in ids:
                if args.log_duplicates:
                    logger.warning('Found duplicate ID: %s in %s', rule.id, rule.source)
                if args.ignore_duplicates:
                    continue
            ids.add(rule.id)
            rules.insert(rule.__dict__)

        elapsed_time = datetime.now(timezone.utc) - start_time
        logger.info('Finished database generation in %s resulting in %d rules.', human_readable(elapsed_time), len(rules))
    finally:
        db.close()

    return 0
