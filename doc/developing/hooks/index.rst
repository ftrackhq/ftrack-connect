..
    :copyright: Copyright (c) 2014 ftrack

.. _hooks:

*****
Hooks
*****

Hooks in ftrack connect can be used to extend or modify the default behaviour
of the application. They build upon the event system used in ftrack.

The built-in hooks can be overridden by creating new hooks and placing them in a
directory. Then configure the environment by setting the
:envvar:`FTRACK_TOPIC_PLUGIN_PATH` environment variable.

It is also possible to prevent a default hook from being triggered by calling
py:func:`event.stop` in a callback with higher priority or by removing the
default hook using :py:func:`ftrack.TOPICS.unsubscribe`

.. note::

    Unlike regular events, hooks will typically be run synchronously on the
    system running the ftrack connect application.

.. toctree::
    :maxdepth: 1

    make-web-playable
    launch-application
