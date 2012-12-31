# -*- coding: utf-8  -*-
import select
import psycopg2
import psycopg2.extensions

from urlparse import urlparse, uses_netloc

uses_netloc.append('postgres')


class Trunk(object):
    def __init__(self, dsn):
        params = urlparse(dsn)
        self.conn = psycopg2.connect(database=params.path[1:], user=params.username,
                                     password=params.password, host=params.hostname,
                                     port=params.port)
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    def listen(self, key):
        cursor = self.conn.cursor()
        cursor.execute("LISTEN %s" % key)
        cursor.close()
        while True:
            if select.select([self.conn], [], [], 5) == ([], [], []):
                pass
            else:
                self.conn.poll()
                while self.conn.notifies:
                    yield self.conn.notifies.pop()

    def notify(self, key, payload):
        cursor = self.conn.cursor()
        cursor.execute("SELECT pg_notify(%s, %s);", (key, payload))
        cursor.close()

    def unlisten(self, key):
        cursor = self.conn.cursor()
        cursor.execute("UNLISTEN %s;" % key)
        cursor.close()
