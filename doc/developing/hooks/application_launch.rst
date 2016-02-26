..
    :copyright: Copyright (c) 2016 ftrack

.. _developing/hooks/application_launch:

*********************************
ftrack.connect.application.launch
*********************************

The `ftrack.connect.application.launch` synchronous event is triggered when an
application is launched using the
:py:class:`ftrack_connect.application.ApplicationLauncher`.

It can be used to modify the environment and arguments used when launching
applications using :py:func:`subprocess.Popen`.

Example event passed to hook::

    Event(
        topic='ftrack.connect.application.launch',
        data=launch_data
    )

The passed data variable, launch_data is a dictionary containing:

command
    This is the first arugment :py:class:`list` command that is passed to
    subprocess.Popen.

options
    A dictionary with keyword arguments passed as arguments to subprocess.Popen.

application
    A dictionary containing information about the application that is being
    launched.

context
    The ftrack entity context that the application is being launched for.

By modifying the passed launch_data dictionary, either by replacing the content
or modifying it directly, will be picked up and used by the application
launcher.

.. seealso::

    :ref:`developing/tutorial/adding_a_location/modifying_application_launch`
    for a tutorial example on how this hook can be used to add make a 
    location plugin available in applications.
