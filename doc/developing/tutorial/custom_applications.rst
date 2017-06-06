..
    :copyright: Copyright (c) 2015 ftrack

.. _developing/tutorial/custom_applications:

**************************
Adding custom applications
**************************

:term:`ftrack connect` is shipped with a bunch of existing plugins for
applications, for example :ref:`HieroPlayer <ftrack-connect-hieroplayer:using>` and
:ref:`cineSync <ftrack-connect-cinesync:using>`.

To start an application using :term:`ftrack connect` go to :term:`ftrack`,
open an entity in the sidebar and open :ref:`Actions <ftrack:using/actions>`.

The window will be populated with available actions based on your current
selection. Once they appear click an icon and the action will start.

Adding your own custom applications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The applications are added as regular :ref:`Actions <ftrack:developing/actions>`
and in this example we'll create an :ref:`Action <ftrack:developing/actions>`
to launch :term:`Houdini` with the current task and the ftrack :term:`API`
accessible within :term:`Houdini`.

First create a new :term:`python` file called `example_houdini_hook.py` and
open it in your favourite code editor.

We'll start off by creating a simple :ref:`Action <ftrack:developing/actions>`
which registers a :meth:`discover` and :meth:`launch` method. Discover is
triggered when the :ref:`Action <ftrack:developing/actions>` window is opened
in :term:`ftrack` and launch is run when selecting the :ref:`Action <ftrack:developing/actions>`.

.. note:: 

    You can download the complete example hook from here
    :download:`example_houdini_hook.py </resource/example_houdini_hook.py>`.

.. code-block:: python

    import logging

    import ftrack_api


    class HoudiniAction(object):
        '''Launch Houdini action.'''

        # Unique action identifier.
        identifier = 'my-houdini-launch-action'

        def __init__(self):
            '''Initialise action.'''
            super(HoudiniAction, self).__init__()

            self.logger = logging.getLogger(
                __name__ + '.' + self.__class__.__name__
            )

            if self.identifier is None:
                raise ValueError('The action must be given an identifier.')

        def register(self, session):
            '''Register action.'''
            session.event_hub.subscribe(
                'topic=ftrack.action.discover',
                self.discover
            )

            session.event_hub.subscribe(
                'topic=ftrack.action.launch and data.actionIdentifier={0}'.format(
                    self.identifier
                ),
                self.launch
            )

        def discover(self, event):
            '''Return action based on *event*.'''
            return {
                'items': [{
                    'label': 'Houdini',
                    'actionIdentifier': self.identifier
                }]
            }

        def launch(self, event):
            '''Callback method for Houdini action.'''
            self.logger.info(
                'Action executed for {0}'.format(event)
            )

            return {
                'success': True,
                'message': 'Houdini started successfully!'
            }


    def register(session, **kw):
        '''Register action in Connect.'''

        # Validate that session is an instance of ftrack_api.Session. If not, assume
        # that register is being called from an old or incompatible API and return
        # without doing anything.
        if not isinstance(session, ftrack_api.Session):
            return

        action = HoudiniAction()
        action.register(session)


This piece of code can now be used as a :ref:`hook <developing/hooks>` in
:term:`ftrack connect`. To make it run you'll need to copy the file to the
:term:`plugin directory` where :term:`ftrack connect` looks for plugin
:ref:`hooks <developing/hooks>`::

    <ftrack-connect-plugin-directory>/
        houdini_hook/
            hook/
                example_houdini_hook.py

Once copied start your :term:`ftrack connect` application and open the
:ref:`Actions <ftrack:using/actions>` window on a task in :term:`ftrack`. The
window should now be populated with an option called `Houdini` and when clicked
you'll get a success message.

Now let's make use of the functionality in :term:`ftrack connect`
to find and start applications.

This is done by using the :mod:`ftrack_connect.application` module and 
first we need an :py:class:`ftrack_connect.application.ApplicationStore`
which can find and hold our applications.

When creating our store we have to override the 
:py:meth:`ftrack_connect.application.ApplicationStore._discoverApplications`
method to specify which applications to look for. Add these imports and the
store definition to your custom hook file.

.. code-block:: python
    
    import sys
    import pprint

    import ftrack_connect.application


.. code-block:: python

    class ApplicationStore(ftrack_connect.application.ApplicationStore):
        '''Store used to find and keep track of available applications.'''

        def _discoverApplications(self):
            '''Return a list of applications that can be launched from this host.'''
             applications = []

            if sys.platform == 'darwin':
                prefix = ['/', 'Applications']

                applications.extend(self._searchFilesystem(
                    expression=prefix + [
                        'Houdini*', 'Houdini.app'
                    ],
                    label='Houdini {version}',
                    applicationIdentifier='houdini_{version}'
                ))

            elif sys.platform == 'win32':
                prefix = ['C:\\', 'Program Files.*']

                applications.extend(self._searchFilesystem(
                    expression=(
                        prefix +
                        ['Side Effects Software', 'Houdini*', 'bin', 'houdini.exe']
                    ),
                    label='Houdini {version}',
                    applicationIdentifier='houdini_{version}'
                ))

            self.logger.debug(
                'Discovered applications:\n{0}'.format(
                    pprint.pformat(applications)
                )
            )

            return applications

To make use of the store we now need to update our existing :meth:`discover`
method to use the store instead of just returning a hard coded value. Let's
modify the :meth:`__init__`, :meth:`register` and :meth:`discover` to use the
store.

    .. code-block:: python

        def __init__(self, applicationStore):
            '''Initialise action with *applicationStore*.

            *applicationStore* should be an instance of
            :class:`ftrack_connect.application.ApplicationStore`.

            '''
            super(HoudiniAction, self).__init__()

            self.logger = logging.getLogger(
                __name__ + '.' + self.__class__.__name__
            )

            self.applicationStore = applicationStore

            if self.identifier is None:
                raise ValueError('The action must be given an identifier.')

    .. code-block:: python

        def discover(self, event):
            '''Return available actions based on *event*.

            Each action should contain

                actionIdentifier - Unique identifier for the action
                label - Nice name to display in ftrack
                icon(optional) - predefined icon or URL to an image
                applicationIdentifier - Unique identifier to identify application
                                        in store.

            '''
            items = []
            applications = self.applicationStore.applications
            applications = sorted(
                applications, key=lambda application: application['label']
            )

            for application in applications:
                applicationIdentifier = application['identifier']
                label = application['label']
                items.append({
                    'actionIdentifier': self.identifier,
                    'label': label,
                    'icon': application.get('icon', 'default'),
                    'applicationIdentifier': applicationIdentifier
                })

            return {
                'items': items
            }

    .. code-block:: python

        def register(session, **kw):
            '''Register action in Connect.'''

            # Validate that session is an instance of ftrack_api.Session. If not, assume
            # that register is being called from an old or incompatible API and return
            # without doing anything.
            if not isinstance(session, ftrack_api.Session):
                return

            # Create store containing applications.
            applicationStore = ApplicationStore()

            # Create action and register to respond to discover and launch actions.
            action = HoudiniAction(applicationStore)
            action.register(session)



Now restart :term:`ftrack connect` and open the :ref:`Actions <ftrack:using/actions>`
window again. It should now display your available :term:`Houdini` applications
including version number.

When clicking the icon the application still won't launch the application
though. To fix this we need to add an :py:class:`ftrack_connect.application.ApplicationLauncher`
to the `launch` method.

To create a basic launcher which will handle starting applications with the 
ftrack API loaded and any selected task specified in the environment modify the
:term:`__init__`, :term:`register` and :term:`launch` methods to look like this:
    
    .. code-block:: python

        def __init__(self, applicationStore, launcher):
            '''Initialise action with *applicationStore* and *launcher*.

            *applicationStore* should be an instance of
            :class:`ftrack_connect.application.ApplicationStore`.

            *launcher* should be an instance of
            :class:`ftrack_connect.application.ApplicationLauncher`.

            '''
            super(HoudiniAction, self).__init__()

            self.logger = logging.getLogger(
                __name__ + '.' + self.__class__.__name__
            )

            self.applicationStore = applicationStore
            self.launcher = launcher

            if self.identifier is None:
                raise ValueError('The action must be given an identifier.')

    .. code-block:: python

        def register(session, **kw):
            '''Register action in Connect.'''

            # Validate that session is an instance of ftrack_api.Session. If not, assume
            # that register is being called from an old or incompatible API and return
            # without doing anything.
            if not isinstance(session, ftrack_api.Session):
                return
            
            # Create store containing applications.
            applicationStore = ApplicationStore()

            # Create a launcher with the store containing applications.
            launcher = ftrack_connect.application.ApplicationLauncher(
                applicationStore
            )

            # Create action and register to respond to discover and launch actions.
            action = HoudiniAction(applicationStore, launcher)
            action.register(session)

    .. code-block:: python

        def launch(self, event):
            '''Callback method for Houdini action.'''
            applicationIdentifier = (
                event['data']['applicationIdentifier']
            )

            context = event['data'].copy()

            return self.launcher.launch(
                applicationIdentifier, context
            )

Once again restart :term:`ftrack connect` to pick up the changes and open the
:ref:`Actions <ftrack:using/actions>` window. Now try to click the icon and
:term:`Houdini` should start.

.. note:: 

    If you haven't been following along you can download the finished 
    hook :download:`example_houdini_hook.py </resource/example_houdini_hook.py>`.

When :term:`Houdini` is running you can try to use the ftrack :term:`API`
by opening the built-in python console and type
    
    .. code-block:: python


        import ftrack_api

        session = ftrack_api.Session()
        projects = session.query('Project')


Modify environment before application start
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::
    
    This section assumes that you've followed the previous part of the tutorial
    or that you've downloaded the complete hook
    :download:`example_houdini_hook.py </resource/example_houdini_hook.py>`.

.. note::

    In most situations the application launch hook described in
    :ref:`developing/hooks/application_launch` should provide enough flexibility
    and can be used to modify the application environment and launch arguments.
    
    If you're satisfied with the `ftrack.connect.application.launch` hook you do
    not have to read further.

To get complete control over the entire applcation launch process you can modify
the existing :py:class:`ftrack_connect.application.ApplicationLauncher` and
override the
:meth:`ftrack_connect.application.ApplicationLauncher._getApplicationEnvironment`.

Start by adding the following class to your hook and modify the :meth:`register`
to use the new launcher class.

    .. code-block:: python


        def register(session, **kw):
            '''Register hooks.'''

            # Validate that session is an instance of ftrack_api.Session. If not, assume
            # that register is being called from an old or incompatible API and return
            # without doing anything.
            if not isinstance(session, ftrack_api.Session):
                return

            # Create store containing applications.
            applicationStore = ApplicationStore()

            # Create a launcher with the store containing applications.
            launcher = ApplicationLauncher(
                applicationStore
            )

            # Create action and register to respond to discover and launch actions.
            action = HoudiniAction(applicationStore, launcher)
            action.register(session)

    .. code-block:: python

        class ApplicationLauncher(ftrack_connect.application.ApplicationLauncher):
            '''Custom launcher to modify environment before launch.'''

            def _getApplicationEnvironment(
                self, application, context=None
            ):
                '''Override to modify environment before launch.'''
                
                # Make sure to call super to retrieve original environment
                # which contains the selection and ftrack API.
                environment = super(
                    ApplicationLauncher, self
                )._getApplicationEnvironment(application, context)

                # Append or Prepend values to the environment.
                # Note that if you assign manually you will overwrite any
                # existing values on that variable.


                # Add my custom path to the HOUDINI_SCRIPT_PATH.
                environment = ftrack_connect.application.appendPath(
                    'path/to/my/custom/scripts',
                    'HOUDINI_SCRIPT_PATH',
                    environment
                )

                # Set an internal user id of some kind.
                environment = ftrack_connect.application.appendPath(
                    'my-unique-user-id-123',
                    'STUDIO_SPECIFIC_USERID',
                    environment
                )

                # Always return the environment at the end.
                return environment

In the overridden method we first call `super` to make sure that we still get
the original environment created by :term:`ftrack connect`.

After doing this we can append or prepend values to environment variables using
the two utility methods :meth:`ftrack_connect.application.prependPath` and 
:meth:`ftrack_connect.application.appendPath`.

Once you've modified your hook restart :term:`ftrack connect` and launch
:term:`Houdini`.

When :term:`Houdini` has started you can validate that the environment is updated
correct by starting the build-in python console and type:

    .. code-block:: python

        import os
        print os.environ['STUDIO_SPECIFIC_USERID'] # my-unique-user-id-123

.. note::

    Download complete example hook with modified launcher
    :download:`example_houdini_hook.py </resource/example_houdini_hook.py>`.
