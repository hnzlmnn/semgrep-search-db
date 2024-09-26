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

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from sgsdb.config import Configuration
from sgsdb.rule import Rule
from sgsdb.util import logger, human_readable, generate_metdata


def collect(args: argparse.Namespace, config: Configuration) -> Generator[Rule, None, None]:
    for repo in config.repositories:
        try:
            yield from repo.iter_rules(args)
        except Exception as e:
            if not args.quiet:
                logger.info(str(e), exc_info=e)
                logger.debug(str(e))
            logger.error(f'Exception during repository parsing: {str(e)}')
            sys.exit(1)


def build_db(args: argparse.Namespace, config: Configuration) -> int:
    db = TinyDB(args.DATABASE, storage=CachingMiddleware(JSONStorage))

    try:
        meta = db.table('meta')
        meta.truncate()
        metadata = generate_metdata()
        if args.verbose > 1:
            logger.debug('Using metadata: %s', ', '.join(f'{k}: {v}' for k, v in metadata.items()))
        meta.insert(metadata)

        repos = db.table('repos')
        repos.truncate()
        for repo in config.repositories:
            repos.upsert(repo.to_dict(), Query().id == repo.id)

        if isinstance(db.storage, CachingMiddleware):
            db.storage.flush()

        rules = db.table('rules')
        if not args.append:
            rules.truncate()

        ids = set()

        start_time = datetime.now(timezone.utc)

        for rule in collect(args, config):
            if rule.id in ids:
                if args.log_duplicates:
                    logger.warning('Found duplicate ID: %s in %s', rule.id, rule.source)
                if args.ignore_duplicates:
                    continue
            ids.add(rule.id)
            rules.insert(rule.asdict())

        elapsed_time = datetime.now(timezone.utc) - start_time
        logger.info('Finished database generation in %s resulting in %d rules from %d origins.',
                    human_readable(elapsed_time), len(rules), len(list(config.repositories)))
    finally:
        db.close()

    return 0
