..
    :copyright: Copyright (c) 2014 ftrack

******************
launch-application
******************

The launch-application hook is triggered from the ftrack interface. The
default hook is a placeholder and should be extended to include correct
application commands.

Parameters
==========

:event: The specific event being handled.
:applicationIdentifier: The identifier of the application.
:context: The application context.

.. literalinclude:: /../resource/hooks/launch_application.py
    :language: python
