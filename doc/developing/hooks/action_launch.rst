..
    :copyright: Copyright (c) 2014 ftrack

.. _developing/hooks/launch_application:

********************
ftrack.action.launch
********************

The *action.launch* hook is triggered from the ftrack interface when a user
selects an action in the :guilabel:`Actions` menu. For more information
about launching applications from the web UI, see 
:ref:`ftrack:using/connect/launch_application`.

The list of applications is provided by the 
:ref:`developing/hooks/action_discover` :term:`hook`. The *action.discover*
hook provides a list of applications with ``applicationIdentifier``
and optionally ``applicationData``. These parameters are passed to this hook
and should be used to launch the correct application.

The default hook is a placeholder and should be extended to include correct
application commands.

Example event passed to hook::

    Event(
        topic='ftrack.action.launch',
        data=dict(
            applicationIdentifier='maya-2014',
            actionIdentifier='ftrack-connect-launch-applications-action',
            applicationData=dict(
                foo='bar'
            ),
            context=dict(
                selection=[
                    dict(
                        entityId='eb16970c-5fc6-11e2-bb9a-f23c91df25eb',
                        entityType='task'
                    )
                ]
            )
        )
    )

Expects reply data in the form::

    dict(
        success=True,
        message='maya-2014 launched successfully.'
    )

Default hook
============

.. literalinclude:: /../resource/hook/applications.py
    :language: python
    :pyobject: LaunchApplicationHook
