..
    :copyright: Copyright (c) 2016 ftrack

.. _developing/plugins:

*******
Plugins
*******

By placing hook plugins in a discoverable :term:`plugin directory` Connect will
automatically register event hooks for custom event processing, actions and
locations.

In this article we will learn about the structure of a plugin and some best
practices that will help you on your way to become an ftrack Connect ninja.

Structure
=========

A plugins structure is easy to grasp and relies on a simple directory structure.
The plugin itself should be contained in a directory and inside the directory
there must be a `hook` directory::

    <ftrack-connect-plugin-directory>/
        my_custom_plugin/
            hook/
                my_action.py

Easy right? When Connect starts it will go over the hook directories in the
:term:`plugin directory` and call register on each of the python scripts in the
hook directory. The `my_action.py` may look something like this::


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


Separating resources
--------------------

Although possible we recommend keeping the `hook` directory as clean as possible
and have any shared modules or other data in a separate directory. This is not
something you have to do but it will make things easier down the line. 

Now let's say that you have a few different actions that share the same modules.
You want to keep things
`DRY <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_
and therefore place them in a resource directory, `resource`::


    <ftrack-connect-plugin-directory>/
        my_custom_plugin/
            hook/
                my_action.py
                another_action.py
            resource/
                my_module/
                    __init__.py

To access the module in the resource/ folder we need to do some manual work
to allow us to import it. In my_action.py we will add it to the `sys.path`::

    import os
    import sys

    RESOURCE_DIRECTORY = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'resource', 'my_module')
    )

    if RESOURCE_DIRECTORY not in sys.path:
        sys.path.append(RESOURCE_DIRECTORY)

    # Define register and rest of action.
    ...



