=====
Trunk
=====

Installing
==========

To install : ::

    pip install trunk


Usage
=====

Trunk tries to be as simple as possible ::

    t = Trunk("postgres://localhost/noclue")
    for notification in t.listen("clues"):
        print notification.channel, notification.payload
    t.notify("clues", "chandelier")
    t.unlisten("clues")


Use with Celery
===============

Trunk provides a `Kombu <http://kombu.readthedocs.org>`_, that allows you to
use trunk with `Celery <http://celeryproject.org>`_, to do configure Celery with ::

    BROKER_URL = 'trunk.transport.Transport://localhost/database'
