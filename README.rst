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

.. code-block:: python
    t = Trunk("postgres://localhost/noclue")
    for notification in t.listen("clues"):
        print notification.channel, notification.payload
    t.notify("clues", "chandelier")
    t.unlisten("clues")
