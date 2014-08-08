..
    :copyright: Copyright (c) 2014 ftrack

*************************
ftrack.launch-application
*************************

The launch-application hook is triggered from the ftrack interface. The
default hook is a placeholder and should be extended to include correct
application commands.

Example event passed to hook::

    Event(
        topic='ftrack.launch-application',
        data=dict(
            applicationIdentifier='maya-2014',
            context=dict(
                selection=[
                    dict(
                        entityId='eb16970c-5fc6-11e2-bb9a-f23c91df25eb',
                        entityType='task',
                    )
                ],
                user=dict(
                    id='e1dc0534-a573-11e3-9614-080027331d71'
                )
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

.. literalinclude:: /../resource/hook/launch_application.py
    :language: python
