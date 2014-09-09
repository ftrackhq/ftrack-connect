..
    :copyright: Copyright (c) 2014 ftrack

.. _developing/hooks:

*****
Hooks
*****

Hooks in ftrack connect can be used to extend or modify the default behaviour
of the application. They build upon the event system used in ftrack. As such,
each hook receives a single argument which is an instance of
:py:class:`ftrack.Event`.

The built-in hooks can be overridden by creating new hooks and placing them in a
directory. Then configure the environment by setting the
:envvar:`FTRACK_EVENT_PLUGIN_PATH` environment variable.

It is also possible to prevent a default hook from being triggered by calling
:py:meth:`event.stop <ftrack.Event.stop>` in a callback with higher
priority or by removing the default hook using
:py:meth:`ftrack.EVENT_HUB.unsubscribe <ftrack.EventHub.unsubscribe>`

.. note::

    Unlike regular events, hooks will typically be run synchronously on the
    system running the ftrack connect application.

.. toctree::
    :maxdepth: 1

    make_web_playable
    launch_application
    get_applications
