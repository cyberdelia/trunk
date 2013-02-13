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

    def listen(self, channel):
        with self.cursor() as cursor:
            cursor.execute("LISTEN \"%s\"" % channel)

    def get(self, channel=None, block=True, timeout=None):
        if not block:
            timeout = 0
        while True:
            for notify in self.conn.notifies:
                if channel and notify.channel != channel:
                    continue
                self.conn.notifies.remove(notify)
                return notify.channel, notify.payload
            else:
                r, w, e = select.select([self.conn], [], [], timeout)
                if not (r or w or e):
                    raise Empty()
                self.conn.poll()

    def notify(self, channel, payload=None):
        with self.cursor() as cursor:
            cursor.execute("SELECT pg_notify(%s, %s);", (channel, payload))

    def notifications(self, channel=None):
        while True:
            yield self.get(channel)

    def unlisten(self, channel):
        with self.cursor() as cursor:
            cursor.execute("UNLISTEN \"%s\";" % channel)

    def channels(self):
        with self.cursor() as cursor:
            cursor.execute("SELECT pg_listening_channels();")
            channels = cursor.fetchall()
            return [c[0] for c in channels]

    def close(self):
        self.conn.close()
