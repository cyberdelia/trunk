# -*- coding: utf-8  -*-
try:
    from Queue import Empty, Full
except ImportError:
    from queue import Empty, Full  # noqa

from trunk import Trunk


class PGQueue(object):
    def __init__(self, dsn):
        self.trunk = Trunk(dsn)

    def create(self, name):
        self.trunk.listen(name)

    def get(self, name, block=True, timeout=None):
        channel, payload = self.trunk.get(name, block=block, timeout=timeout)
        with self.trunk.cursor() as cursor:
            cursor.execute("SELECT id, message FROM pop_lock(%s)", (name,))
            row = cursor.fetchone()
            if row is None:
                raise Empty()
            return row

    def get_nowait(self, name):
        return self.get(name, block=False)

    def put(self, name, message):
        with self.trunk.cursor() as cursor:
            cursor.execute("INSERT INTO trunk_queue (name, message) VALUES (%s, %s)", (name, message))
        self.trunk.notify(name)

    def empty(self, name):
        return 0 == self.qsize(name)

    def qsize(self, name):
        with self.trunk.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM trunk_queue WHERE name = %s", (name,))
            row = cursor.fetchone()
            return row[0]

    def purge(self, name):
        size = self.qsize(name)
        with self.trunk.cursor() as cursor:
            cursor.execute("DELETE FROM trunk_queue WHERE name = %s", (name,))
        return size

    def close(self):
        self.trunk.close()
