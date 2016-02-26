..
    :copyright: Copyright (c) 2015 ftrack

.. _release/migration:

***************
Migration notes
***************

.. _release/migration/upcoming:

Migrate from 0.1.19 to upcoming
===============================

.. _release/migration/upcoming/developer_notes:

Developer notes
---------------

The :ref:`ftrack-python-api <ftrack-python-api:introduction>` will from now discover plugins that
are added to the `FTRACK_EVENT_PLUGIN_PATH`.

This means that register functions will be called several times, both for
the ftrack-python-api and the legacy api. To avoid registering a hook multiple
times, developers should validate the register functions arguments::

    import ftrack

    ...

    def register(registry, **kw):
        '''Register plugin.'''

        # Validate that registry is an instance of ftrack.Registry. If not,
        # assume that register is being called from a new or incompatible API
        # and return without doing anything.
        if not isinstance(registry, ftrack.Registry):
            # Exit to avoid registering this plugin again.
            return

        # Register plugin event listener.
        ...

Plugins for the new Python API must validate that they are called with an
:ref:`ftrack_api.session.Session` as a first argument::

    import ftrack_api

    ...

    def register(session, **kw):
        '''Register plugin.'''

        # Validate that session is an instance of ftrack_api.Session. If not,
        # assume that register is being called from an incompatible API
        # and return without doing anything.
        if not isinstance(session, ftrack_api.Session):
            # Exit to avoid registering this plugin again.
            return

        # Register plugin event listener.
        ...



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
custom hooks, please make sure they are updated accordingly. In the updated
format of the event data ``selection`` and the contents of ``actionData`` has
been moved to the root, ``event['data']``, level.