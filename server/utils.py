#!/usr/bin/python
# -*- coding: utf-8 -*
import sys
from numbers import Number
from itertools import tee
from datetime import tzinfo, timedelta, datetime

py3k = sys.version_info.major > 2

if py3k:
    from queue import Queue
    unicode = str
else:  # 2.x
    from Queue import Queue
    unicode = unicode


# Some helpers for string/bytes handling
def to_bytes(s, encoding='utf8'):
    if isinstance(s, unicode):
        return s.encode(encoding)
    if isinstance(s, (bool, Number)):
        return str(s).encode(encoding)
    return bytes('' if s is None else s)


def to_unicode(s, encoding='utf8', errors='strict'):
    if isinstance(s, bytes):
        return s.decode(encoding, errors)
    return unicode('' if s is None else s)


to_string = to_unicode if py3k else to_bytes


class IterBetter:
    def __init__(self, iterator):
        self.i, self.c = iterator, 0

    def first(self, default=None):
        try:
            return next(iter(self))
        except StopIteration:
            return default

    def list(self):
        return list(self)

    def __iter__(self):
        while 1:
            try:
                yield next(self.i)
            except StopIteration:
                return
            self.c += 1

    def __getitem__(self, i):
        if i < self.c:
            raise IndexError('already passed ' + str(i))
        try:
            while i > self.c:
                next(self.i)
                self.c += 1
            self.c += 1
            return next(self.i)
        except StopIteration:
            raise IndexError(str(i))

    def __nonzero__(self):
        if hasattr(self, '_head'):
            return True
        else:
            try:
                self.i, _i = tee(self.i)
                self._head = next(_i)
            except StopIteration:
                return False
            else:
                return True

    __bool__ = __nonzero__


iterbetter = IterBetter


class UTC(tzinfo):
    def __init__(self, offset=0):
        self._offset = offset

    def utcoffset(self, dt):
        return timedelta(hours=self._offset)

    def tzname(self, dt):
        return 'UTC %+d:00' % self._offset

    def dst(self, dt):
        return timedelta(hours=self._offset)
 

def now():
    return datetime.now(UTC(8))  # tz: Shanghai


def tomorrow():  
    return now() + timedelta(hours=24)
