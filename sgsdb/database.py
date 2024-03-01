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
import logging
import sys
from typing import Generator

from tinydb import TinyDB

from sgsdb.repository import Repository, RepositoryProcessor
from sgsdb.rule import Rule

logger = logging.getLogger(__name__)

REPOSITORIES = [
    Repository('semgrep', 'Semgrep Registry',
               'https://github.com/semgrep/semgrep-rules/archive/refs/heads/develop.zip'),
    Repository('semgrep', 'GitLab SAST',
               'https://gitlab.com/gitlab-org/security-products/sast-rules/-/archive/main/sast-rules-main.zip'),
    Repository('semgrep', '0xdea Rules',
               'https://github.com/0xdea/semgrep-rules/archive/refs/heads/main.zip'),
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
    db = TinyDB(args.DATABASE)

    if not args.append:
        db.truncate()

    ids = set()
    for rule in collect(args):
        if rule.id in ids:
            if args.log_duplicates:
                logger.warning('Found duplicate ID: %s in %s', rule.id, rule.source)
            if args.ignore_duplicates:
                continue
        ids.add(rule.id)
        db.insert(rule.__dict__)

    return 0