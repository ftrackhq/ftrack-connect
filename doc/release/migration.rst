..
    :copyright: Copyright (c) 2015 ftrack

.. _release/migration:

***************
Migration notes
***************
.. _release/migration/0_1_3:

Migrate from 0.1.2 to 0.1.3
===========================

.. _release/migration/0_1_3/developer_notes:

Developer notes
---------------

.. _release/migration/0_1_3/developer_notes/updated_action_hooks:

Updated action hooks
^^^^^^^^^^^^^^^^^^^^

The default :ref:`discover <developing/hooks/action_discover>` and
:ref:`launch <developing/hooks/action_launch>` action hooks has been updated
to support the updated action format in ftrack 3.0.3. If you have created
custom hooks, please make sure they are updated accordingly. In particular,
the ``selection`` and contents of ``actionData`` to the root, ``event['data']``,
level.