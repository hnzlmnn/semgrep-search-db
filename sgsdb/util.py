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
import logging
import sys
from collections import OrderedDict
from datetime import timedelta, datetime, timezone
from importlib import metadata
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import Tuple, Union, Any

import tomli
from gitinfo import gitinfo
from ruamel.yaml import CommentedSeq, CommentedMap

from sgsdb.const import LANGUAGE_ALIASES

PRINT_LOG_LEVEL = False


def fix_languages(langauges: Union[set[str], list[str]]) -> set[str]:
    """
    Resolves all aliased languages to their base name
    """
    return {LANGUAGE_ALIASES.get(lang, lang).lower() for lang in langauges}


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


logger = logging.getLogger('semgrep-search-db')


def build_logger(args: argparse.Namespace) -> None:
    log_format = '%(message)s'
    if PRINT_LOG_LEVEL:
        log_format = f'[%(threadName)s] [%(levelname)s] {log_format}'

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(logging.Formatter(log_format))
    console_handler.setLevel(logging.DEBUG if args.verbose > 0 else logging.INFO)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)


def generate_metdata() -> dict:
    git = gitinfo.get_git_info()

    try:
        version = metadata.version('semgrep-search-db')
    except PackageNotFoundError:
        try:
            with Path('pyproject.toml').open('rb') as fin:
                version = tomli.load(fin).get('tool').get('poetry').get('version')
        except Exception:
            version = '0.0.0-dev'

    return {
        'created_on': str(datetime.now(timezone.utc)),
        'version': version,
        'commit': 'unknown' if git is None else git['commit'][:7],
        'min_version': '1.1.0',
    }


def remove_comments(data: Any) -> Any:  # noqa: ANN401
    if isinstance(data, (dict, OrderedDict, CommentedMap)):
        return CommentedMap(OrderedDict([
            (key, remove_comments(value)) for key, value in data.items()
        ]))

    if isinstance(data, (list, CommentedSeq)):
        return CommentedSeq([remove_comments(item) for item in data])

    return data
