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
import threading

from pathlib import Path
from typing import Generator, TYPE_CHECKING

from sgsdb.parsing.model import ParsingResult
from sgsdb.parsing.parallel import enqueue_thread, CloseableQueue, Closed
from sgsdb.parsing.parser import RuleParser
from sgsdb.parsing.statistic import ResultStatus
from sgsdb.util import logger

if TYPE_CHECKING:
    from sgsdb.repository import Repository

RE_FILENAME = re.compile(r'^.*\.ya?ml$')
RE_TESTFILE = re.compile(r'^.*\.test\.ya?ml$')


class RuleProcessor:
    def __init__(self, args: argparse.Namespace, repo: 'Repository') -> None:
        self.args = args
        self.repo = repo
        self.progress_mutex = threading.Lock()
        self.progress = None
        self.parser = RuleParser(args, repo)

    def _process(self, in_queue: CloseableQueue[tuple[str, str]], out_queue: CloseableQueue[ParsingResult]) -> None:
        while True:
            try:
                path, content = in_queue.get()
                result = ParsingResult(self.repo, path, content)

                if not self.filter_filename(result.path):
                    result.status = [ResultStatus.IGNORED]
                else:
                    self.parser.process(result)

                out_queue.put(result)
            except Closed:
                break

    def filter_filename(self, filename: str) -> bool:
        if not RE_FILENAME.match(filename) or RE_TESTFILE.match(filename):
            if self.args.verbose > 1:
                logger.debug('Ignoring due to file name: %s', filename)
            return False

        path = Path(filename).relative_to(Path(filename).parents[-2])
        if any(d.startswith('.') for d in path.parts):
            if self.args.verbose > 1:
                logger.debug('Ignoring hidden file: %s', path)
            return False

        return True

    def _run(self, iterator: Generator[tuple[str, str], None, None],
             result_queue: CloseableQueue[ParsingResult]) -> None:

        in_queue = CloseableQueue[tuple[str, str]]()
        enqueue_thread(iterator, in_queue)

        threads = [threading.Thread(target=self._process, args=(in_queue, result_queue)) for _ in
                   range(self.args.threads)]
        for thread in threads:
            thread.daemon = True
            thread.start()

        for thread in threads:
            thread.join()

        # All input threads are done, we can safely close the result queue
        result_queue.close()

    def start(self, iterator: Generator[tuple[str, str], None, None],
              result_queue: CloseableQueue[ParsingResult]) -> threading.Thread:
        thread = threading.Thread(target=self._run, args=(iterator, result_queue))
        thread.daemon = True
        thread.start()
        return thread
