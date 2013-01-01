# -*- coding: utf-8  -*-
import select
import psycopg2
import psycopg2.extensions

from Queue import Empty

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
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    def listen(self, key, timeout=None):
        cursor = self.conn.cursor()
        cursor.execute("LISTEN \"%s\"" % key)
        cursor.close()
        while not self.conn.notifies:
            r, w, e = select.select([self.conn], [], [], timeout)
            if not (r or w or e):
                raise StopIteration
            self.conn.poll()
            while self.conn.notifies:
                notify = self.conn.notifies.pop()
                yield notify.channel, notify.payload

    def pop(self, key):
        cursor = self.conn.cursor()
        cursor.execute("LISTEN \"%s\"" % key)
        cursor.close()
        self.conn.poll()
        if self.conn.notifies:
            notify = self.conn.notifies.pop()
            return notify.channel, notify.payload
        else:
            raise Empty()

    def notify(self, key, payload=None):
        cursor = self.conn.cursor()
        cursor.execute("SELECT pg_notify(%s, %s);", (key, payload))
        cursor.close()

    def unlisten(self, key):
        cursor = self.conn.cursor()
        cursor.execute("UNLISTEN \"%s\";" % key)
        cursor.close()
