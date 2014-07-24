..
    :copyright: Copyright (c) 2014 ftrack

.. _launching:

*********************
Launching the service
*********************

ftrack connect revolves around a core service that runs locally on your machine.
Once you have the main package :ref:`installed <installing>`, you can run an
instance of the service by opening a terminal and executing the following:

.. code-block:: bash

    python -m ftrack_connect

.. note::

    To see all available launch options (including changing the theme and
    logging verbosity) use:

    .. code-block:: bash

        python -m ftrack_connect --help

Once the service is launched, the main window will appear and you will also
notice an ftrack icon in your task bar.

Windows:

.. image:: /image/windows_service.png

Mac:

.. image:: /image/mac_service.png

The service will then continue to run in the background even if you close all
the windows.

To reopen a window or exit the service, use the popup menu that appears by
:kbd:`right clicking` on the icon.

.. image:: /image/service_menu.png
