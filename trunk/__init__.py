# -*- coding: utf-8  -*-
import select
import psycopg2
import psycopg2.extensions

from contextlib import contextmanager

try:
    from Queue import Empty
except ImportError:
    from queue import Empty  # noqa


try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # noqa


class Trunk(object):
    def __init__(self, dsn):
        params = urlparse(dsn)
        self.conn = psycopg2.connect(database=params.path[1:], user=params.username,
                                     password=params.password, host=params.hostname,
                                     port=params.port)
        self.conn.autocommit = True

    @contextmanager
    def cursor(self):
        cursor = self.conn.cursor()
        yield cursor
        cursor.close()

    def listen(self, key):
        with self.cursor() as cursor:
            cursor.execute("LISTEN \"%s\"" % key)

    def get(self, key, block=True, timeout=None):
        if not block:
            timeout = 0
        while True:
            if self.conn.notifies:
                notify = self.conn.notifies.pop()
                return notify.channel, notify.payload
            else:
                r, w, e = select.select([self.conn], [], [], timeout)
                if not (r or w or e):
                    raise Empty()
                self.conn.poll()

    def notify(self, key, payload=None):
        with self.cursor() as cursor:
            cursor.execute("SELECT pg_notify(%s, %s);", (key, payload))

    def notifications(self, key):
        self.listen(key)
        while True:
            yield self.get(key)

    def unlisten(self, key):
        with self.cursor() as cursor:
            cursor.execute("UNLISTEN \"%s\";" % key)

    def channels(self):
        with self.cursor() as cursor:
            cursor.execute("SELECT pg_listening_channels();")
            channels = cursor.fetchall()
            return [c[0] for c in channels]

    def close(self):
        self.conn.close()
