..
    :copyright: Copyright (c) 2016 ftrack

.. _developing/tutorial/adding_a_location:

************************
Adding a location plugin
************************

This tutorial assumes basic knowledge of the :term:`Location plugins` system in
ftrack and will focus on how to make Location plugins availble for Connect and
integrated applications.

Making Connect aware of your location plugin
============================================

Making use of the :term:`plugin directory` we can register a location plugin to
be available in Connect. Since Connect and other integrations are still using
the legacy api for publishing we will use it as a basis of this example. Let us
now implement a basic Location plugin::


    import ftrack

    def register(registry, **kw):
        '''Register plugin.'''

        # Validate that registry is an instance of ftrack.Registry. If not,
        # assume that register is being called from a new or incompatible API
        # and return without doing anything.
        if registry is not ftrack.LOCATION_PLUGINS:
            # Exit to avoid registering this plugin again.
            return

        ftrack.ensureLocation('studio.location')

        # Create a location instance
        location = ftrack.Location(
            'studio.location',
            accessor=ftrack.DiskAccessor(
                prefix='<path-to-directory-where-files-should-go>'
            ),
            structure=ftrack.IdStructure(),
            priority=5
        )
        registry.add(location)

If we now add our new location plugin, ``custom_location_plugin.py``, to the
plugin directory it will be automatically discovered and available in Connect::

    <ftrack-connect-plugin-directory>/
        my_location_plugin/
            hook/
                location/
                    custom_location_plugin.py

.. _developing/tutorial/adding_a_location/modifying_application_launch:

Modifying application launch
============================

We have now learned how to make a location plugin and use it for publishing in
Connect. However, this does not automatically mean that it will be picked up
by integrated applications.

We will now use the :ref:`developing/hooks/application_launch` hook to make our
applications aware of our new location::

Let us create a new file, my_application_launch_hook.py, and make sure our
plugin is on the `FTRACK_LOCATION_PLUGIN_PATH`::

    import os

    import ftrack

    LOCATION_DIRECTORY = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'location')
    )


    def modify_application_launch(event):
        '''Modify the application environment to include  our location plugin.'''
        options = event['data']['options']
        
        location_plugin_path = options['env'].get('FTRACK_LOCATION_PLUGIN_PATH')
        if location_plugin_path:
            location_plugin_path += os.pathsep + LOCATION_DIRECTORY
        else:
            location_plugin_path = LOCATION_DIRECTORY

        # Modify the environment variable.
        options['env']['FTRACK_LOCATION_PLUGIN_PATH'] = location_plugin_path


    def register(registry, **kw):
        '''Register location plugin.'''

        # Validate that registry is an instance of ftrack.Registry. If not,
        # assume that register is being called from a new or incompatible API
        # and return without doing anything.
        if registry is not ftrack.EVENT_HANDLERS:
            # Exit to avoid registering this plugin again.
            return

        ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.connect.application.launch',
            modify_application_launch
        )
