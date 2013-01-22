# -*- coding: utf-8  -*-
import select
import psycopg2
import psycopg2.extensions

try:
    from Queue import Empty, Full
except ImportError:
    from queue import Empty, Full  # noqa


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

    def listen(self, key):
        cursor = self.conn.cursor()
        cursor.execute("LISTEN \"%s\"" % key)
        cursor.close()

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

    def get_nowait(self, key):
        return self.get(key, block=False)

    def put(self, key, payload=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT pg_notify(%s, %s);", (key, payload))
        except psycopg2.Error:
            raise Full()
        finally:
            cursor.close()

    def notify(self, key, payload=None):
        self.put(key, payload)

    def notifications(self, key):
        self.listen(key)
        while True:
            yield self.get(key)

    def unlisten(self, key):
        cursor = self.conn.cursor()
        cursor.execute("UNLISTEN \"%s\";" % key)
        cursor.close()

    def channels(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT pg_listening_channels();")
        channels = cursor.fetchall()
        cursor.close()
        return [c[0] for c in channels]

    def close(self):
        self.conn.close()
