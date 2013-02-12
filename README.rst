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
    for channel, payload in t.notifications("clues"):
        print channel, payload
    t.notify("clues", "chandelier")
    t.unlisten("clues")


Celery
======

Trunk provides a `Kombu <http://kombu.readthedocs.org>`_ transport,
that allows you to use trunk with `Celery <http://celeryproject.org>`_,
to do so, configure Celery with : ::

    BROKER_URL = 'trunk.transport.Transport://localhost/database'

Setup
-----

You will need to create a new table and add two functions to your database.
See `table.sql <https://github.com/cyberdelia/trunk/blob/master/sql/table.sql>`_
and `ddl.sql <https://github.com/cyberdelia/trunk/blob/master/sql/ddl.sql>`_.
