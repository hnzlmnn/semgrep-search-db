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

from sgsdb import build_db

logger = logging.getLogger('sgsdb')

LOG_LEVEL = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog='sgs-db',
                                     description='Build the database for sgs (semgrep-search) from multiple sources')

    parser.add_argument('DATABASE', help='The path to the database file')

    parser.add_argument('-a', '--append', dest='append', action='store_true', default=False,
                        help='Append to the database instead of truncating')
    parser.add_argument('-d', '--log-duplicated', dest='log_duplicates', action='store_true', default=False,
                        help='Log duplicate IDs')
    parser.add_argument('-i', '--ignore-duplicates', dest='ignore_duplicates', action='store_true', default=False,
                        help='Do not add duplicate IDs to the database')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', default=False,
                        help='Do not log errors found while parsing a rule file')
    parser.add_argument('-c', '--cache', dest='cache', action='store_true', default=False,
                        help='Only download repository data if not already present')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False,
                        help='Enable verbose logging')

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    log_format = '%(message)s'
    if LOG_LEVEL:
        log_format = f'[%(levelname)s] {log_format}'
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format=log_format)

    return build_db(args)



if __name__ == '__main__':
    sys.exit(main())
