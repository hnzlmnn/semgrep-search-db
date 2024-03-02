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
from datetime import timedelta
from typing import Tuple

from ruamel.yaml import YAML

yaml = YAML(typ='rt')

PRINT_LOG_LEVEL = False


def hours_minutes_seconds(td: timedelta) -> Tuple[int, int, int]:
    return td.seconds//3600, (td.seconds//60) % 60, td.seconds % 60


def human_readable(td: timedelta) -> str:
    hours, minutes, seconds = hours_minutes_seconds(td)
    if hours > 0:
        return f'{hours}h{minutes}m{seconds}s'
    if minutes > 0:
        return f'{minutes}m{seconds}s'
    if seconds > 0:
        return f'{seconds}s'
    return f'0.{td.microseconds // 1000}s'


logger = logging.getLogger('sgsdb')


def build_logger(args: argparse.Namespace) -> None:
    log_format = '%(message)s'
    if PRINT_LOG_LEVEL:
        log_format = f'[%(levelname)s] {log_format}'

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(logging.Formatter(log_format))
    console_handler.setLevel(logging.DEBUG if args.verbose > 0 else logging.INFO)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)
