..
    :copyright: Copyright (c) 2014 ftrack

***********************
ftrack.get-applications
***********************

The get-applications hook is triggered from the ftrack interface. The
default hook is a placeholder and should be extended to include a complete list 
of applications that can be launched.

Example event passed to hook::

    Event(
        topic='ftrack.get-applications',
        data=dict(
            context=dict(
                selection=[
                    dict(
                        entityId='eb16970c-5fc6-11e2-bb9a-f23c91df25eb',
                        entityType='task',
                    )
                ]
            )
        )
    )

Expects reply data in the form::

    dict(
        items=[
            dict(
                label='My applications',
                type='heading'
            ),
            dict(
                label='Maya 2014',
                applicationIdentifier='maya_2014'
            ),
            dict(
               type='separator'
            ),
            dict(
                label='2D applications',
                items=[
                    dict(
                        label='Premiere Pro CC 2014',
                        applicationIdentifier='pp_cc_2014'
                    ),
                    dict(
                        label='Premiere Pro CC 2014 with latest publish',
                        applicationIdentifier='pp_cc_2014',
                        applicationData=dict(
                            latest=True
                        )
                    )
                ]
            )
        ]
    )

Default hook
============

.. literalinclude:: /../resource/hook/applications.py
    :language: python
    :pyobject: GetApplicationsHook
