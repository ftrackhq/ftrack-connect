..
    :copyright: Copyright (c) 2014 ftrack

.. _developing/hooks/get_applications:

***********************
ftrack.get-applications
***********************

The get-applications hook is triggered from the ftrack interface to request a 
list of available applications for launching. For more information, see 
:ref:`ftrack:using/connect/launch_application`.

The default hook is a placeholder and should be extended to include a complete
list of applications that can be launched.

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
                label='Mega Modeling 2014',
                applicationIdentifier='mega_modeling_2014'
            ),
            dict(
                type='separator'
            ),
            dict(
                label='2D Applications',
                items=[
                    dict(
                        label='Professional Painter',
                        applicationIdentifier='professional_painter'
                    ),
                    dict(
                        label='Cool Compositor v2',
                        applicationIdentifier='cc_v2',
                        applicationData=dict(
                            cc_plugins=['foo', 'bar'],
                        )
                    )
                ]
            )
        ]
    )

The response should be a dictionary with an ``items`` list. The list should
contain a dictionary for each menu item to be returned. Each item can have a
``type`` of ``heading``, ``separator`` or ``button``, where ``button`` is the
default and can be omitted. If an item contains a new ``items`` list, it will
be displayed as a submenu.

Applications
============

To add an application, add an item in the following format.

.. code-block:: python

    dict(
        label='Crazy Compositor v2',
        applicationIdentifier='cc_v2',
        applicationData=dict(
            cc_plugins=['foo', 'bar'],
        )
    )

The different options are:

``label``
    Used to display the application in the ftrack interface. 
``applicationIdentifier``
    Used to uniquely identify this application in the 
    :ref:`developing/hooks/launch_application` hook.
``applicationData`` 
    Optional and can contain any extra data you want to include in the event. 
    This data will be passed on to the 
    :ref:`developing/hooks/launch_application` hook.


Headings
========

To add a heading, use type ``heading`` and enter the text as ``label``.

.. code-block:: python

    dict(
        label='My applications',
        type='heading'
    )

Separators
==========

To add a separator, add an item with type ``separator``.

.. code-block:: python

    dict(
        type='separator'
    )

Nested menus
============

If an item contains an ``items`` list, it will be displayed as a submenu with
each item in the list forming an item in the submenu. The ``label`` will be
used as the text label for the submenu. You can have as many nested submenus as
you wish, but try to keep the depth to a maximum of three levels for usability.

.. code-block:: python

    dict(
        label='More items',
        items=[
            dict(
                label='Application X',
                applicationIdentifier='app_x'
            ),
            dict(
                label='Application Y',
                applicationIdentifier='app_y'
            )
        ]
    )

.. note::

    An item with an ``items`` array will always be displayed as a submenu,
    regardless of the presence of any ``type`` or ``applicationIdentifier``.

Default hook
============

.. literalinclude:: /../resource/hook/applications.py
    :language: python
    :pyobject: GetApplicationsHook
