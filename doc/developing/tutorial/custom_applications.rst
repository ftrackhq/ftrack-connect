..
    :copyright: Copyright (c) 2015 ftrack

**************************
Adding custom applications
**************************

ftrack connect is shipped with a bunch of existing plugins for applications like
Maya, Nuke, Hiero, HieroPlayer and cineSync.

To start an application using :term:`ftrack connect` go to :term:`ftrack`,
open an entity in the sidebar and click the :ref:`Actions icon <>`_.

The window will be populated with available actions based on your current
selection. Once they appear click an icon and the action will start.

Adding your own custom applications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add your own custom application to the Actions menu you will need to do a 
bit of coding.

The applications are added as regular :ref:`Actions` and in this example we'll
create an :ref:`Action` to launch Houdini with the current task and
ftrack API available.

First create a new :term:`Python` file called `my_houdini_hook.py` and open in
in you preferred code editor.

We'll start off by creating a simple :ref:`Action` which registers a discover
and launch method. The discover is triggered when the Action window is opened
in ftrack and the launch is triggered when clicking the Action in the window.

.. note:: 

    You can download the complete example hook from here
    :download:`example_houdini_hook.py </resource/example_houdini_hook.py>`.

.. code-block:: python

    import logging

    import ftrack


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

        def register(self):
            '''Register action.'''
            ftrack.EVENT_HUB.subscribe(
                'topic=ftrack.action.discover',
                self.discover
            )

            ftrack.EVENT_HUB.subscribe(
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


    def register(registry, **kw):
        '''Register action in Connect.'''
        action = HoudiniAction()
        action.register()



This piece of code can now be used as a hook in ftrack connect. To make it run
you'll need to copy the file to a folder where ftrack connect looks for hooks.

On windows the default directory is:
    
    .. code-block:: bash

        C:\Program Files\ftrack-connect-package\resource\hook

And on OSX the default directory is:

    .. code-block:: bash

        /Applications/ftrack-connect.app/Contents/MacOS/resource/hook/

Once copied start your ftrack connect application and open the Actions window
on a task in ftrack. The window should now be populated with an option called
`Houdini` and when clicked you'll get a success message.

Now let's make use of the functionality in ftrack connect to find and start
applications.

First we need an application store which find and hold our applications. When
creating our store we have to override the 
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

To make use of the store we now need to update our existing `discover` method
to use the store instead of just returning a hard coded value. Let's modify the 
`__init__`, `register` and `discover` to use the store.

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

        def register(registry, **kw):
            '''Register action in Connect.'''
            
            # Create store containing applications.
            applicationStore = ApplicationStore()

            # Create action and register to respond to discover and launch actions.
            action = HoudiniAction(applicationStore)
            action.register()

Now restart ftrack connect and open the Actions window again. It should now
display your available :term:`Houdini` applications including version number.

When clicking the icon the application still won't launch though. To fix this we
need to add an application launcher to the `launch` method.

To create a basic launcher which will handle starting applications with the 
ftrack API loaded and any selected task specified in the environment modify the
`__init__`, `register` and `launch` methods to look like this:
    
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

        def register(registry, **kw):
            '''Register action in Connect.'''
            
            # Create store containing applications.
            applicationStore = ApplicationStore()

            # Create a launcher with the store containing applications.
            launcher = ftrack_connect.application.ApplicationLauncher(
                applicationStore
            )

            # Create action and register to respond to discover and launch actions.
            action = HoudiniAction(applicationStore, launcher)
            action.register()

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

Once again restart ftrack connect to pick up the changes and open the Action
window. Now try to click the icon and :term:`Houdini` should start.

.. note:: 

    If you haven't been following along you can download the finished 
    hook :download:`example_houdini_hook.py </resource/example_houdini_hook.py>`.

When :term:`Houdini` is running you can try to use the ftrack API by opening the
build-in python console and type
    
    .. code-block:: python

        import ftrack
        print ftrack.getProjects()
