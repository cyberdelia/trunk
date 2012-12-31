=====
Trunk
=====

Installing
==========

To install : ::

    pip install trunk


Usage
=====

.. code-block:: python
    t = Trunk("postgres://localhost/noclue")
    for notification in t.listen("clues"):
        print notification.channel, notification.payload
    t.notify("clues", "chandelier")
    t.unlisten("clues")
