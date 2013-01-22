# -*- coding: utf-8  -*-
from anyjson import loads, dumps

from kombu.transport import virtual

from trunk import Trunk
from trunk.utils import build_dsn


class Channel(virtual.Channel):
    def __init__(self, *args, **kwargs):
        super(Channel, self).__init__(*args, **kwargs)
        parts = self.connection.client
        dsn = build_dsn(scheme='postgres', hostname=parts.hostname,
                        port=parts.port, path=parts.virtual_host,
                        username=parts.userid, password=parts.password)
        self.trunk = Trunk(dsn)

    def _new_queue(self, queue, **kwargs):
        self.trunk.listen(queue)

    def _get(self, queue, timeout=None):
        _, message = self.trunk.get_nowait(queue)
        return loads(message)

    def _put(self, queue, message, **kwargs):
        self.trunk.put(queue, dumps(message))

    def _purge(self, queue):
        self.trunk.unlisten(queue)

    def close(self):
        super(Channel, self).close()
        self.trunk.close()


class Transport(virtual.Transport):
    Channel = Channel

    default_port = 5432

    driver_type = 'postgres'
    driver_name = 'postgres'

transport = Transport  # hack to get kombu to load the class
