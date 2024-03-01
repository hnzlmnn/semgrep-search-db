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
from datetime import timedelta

from ruamel.yaml import YAML

yaml = YAML(typ='rt')


def hours_minutes_seconds(td: timedelta):
    return td.seconds//3600, (td.seconds//60) % 60, td.seconds % 60


def human_readable(td: timedelta):
    hours, minutes, seconds = hours_minutes_seconds(td)
    if hours > 0:
        return f'{hours}h{minutes}m{seconds}s'
    if minutes > 0:
        return f'{minutes}m{seconds}s'
    if seconds > 0:
        return f'{seconds}s'
    return f'0.{td.microseconds // 1000}s'
