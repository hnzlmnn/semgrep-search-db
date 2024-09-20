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

from queue import Queue, Full, Empty
from threading import Thread
from time import time
from typing import TypeVar, Generic, Callable, Iterable, Optional

T = TypeVar('T')


class Closed(Exception):
    pass


class CloseableQueue(Queue, Generic[T]):
    def __init__(self) -> None:
        super().__init__()
        self._closed = False

    def close(self) -> None:
        self.mutex.acquire()
        try:
            if not self._closed:
                self._closed = True
                self.not_empty.notify_all()
                self.not_full.notify_all()
        finally:
            self.mutex.release()

    def closed(self) -> bool:
        self.mutex.acquire()
        try:
            return self._closed
        finally:
            self.mutex.release()

    def put(self, item: T, *, block: bool = True, timeout: Optional[float] = None, last: bool = False) -> None:
        with self.not_full:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() >= self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() >= self.maxsize:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time() + timeout
                    while self._qsize() >= self.maxsize:
                        remaining = endtime - time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)

            if self._closed:
                raise Closed

            self._put(item)
            self.unfinished_tasks += 1
            if last:
                self._closed = True
                self.not_empty.notify_all()
                self.not_full.notify_all()
            else:
                self.not_empty.notify()

    def get(self, *, block: bool = True, timeout: Optional[float] = None) -> T:
        with self.not_empty:
            if not block:
                if not self._qsize() and not self._closed:
                    raise Empty
            elif timeout is None:
                while not self._qsize() and not self._closed:
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a positive number")
            else:
                endtime = time() + timeout
                while not self._qsize() and not self._closed:
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)

            if self._closed and not self._qsize():
                raise Closed

            item = self._get()
            self.not_full.notify()
            return item


def enqueue(it: Iterable, q: CloseableQueue, *, putargs: Optional[dict] = None, join: bool = False,
            close: bool = True) -> None:
    if putargs is None:
        putargs = {}
    for value in iter(it):
        q.put(value, **putargs)
    if close:
        q.close()
    if join:
        q.join()


def enqueue_thread(it: Iterable, q: CloseableQueue = None, *, name: str = 'enqueue', start: bool = True,
                   enqueue: Callable = enqueue, **kwargs) -> Thread:
    if q is None:
        q = CloseableQueue()
    thread = Thread(name=name, target=enqueue, args=(it, q), kwargs=kwargs)
    thread.daemon = True
    thread.q = q
    if start:
        thread.start()
    return thread
