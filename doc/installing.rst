..
    :copyright: Copyright (c) 2014 ftrack

.. _installing:

**********
Installing
**********

.. highlight:: bash

Pre-built packages are available for download for Windows, Linux and Mac from
the `Integrations webpage <https://www.ftrack.com/portfolio/connect>`_.

The pre-built packages includes integrations for various applications:

    *   3DS Max
    *   Hiero
    *   Maya
    *   Nuke
    *   Nuke Studio
    *   Hiero
    *   Hiero Player
    *   RV
    *   Houdini
    *   Adobe Creative Cloud
    *   Adobe Photoshop
    *   Adobe Illustrator
    *   Adobe AfterEffects
    *   Adobe Premier Pro
    *   Cinema 4D

.. note::

    Alternative installation methods require technical knowledge.

Building from git repository
============================

Alternatively, install using `pip <http://www.pip-installer.org/>`_:

.. code-block:: none

    $ pip install git+https://bitbucket.org/ftrack/ftrack-connect.git


.. warning::

    When installing through pip, the default hooks will not be properly installed as part of the package,
    but they'll instead be installed on the root of the interpreter eg:

    C:\Python27\ftrack_connect_resource\hook

    Before starting connect please ensure the path is added to your

    * **FTRACK_EVENT_PLUGIN_PATH**

    environment variable.


Building from source
====================

You can also build manually from the source for more control. First obtain a
copy of the source by either downloading the
`zipball <https://bitbucket.org/ftrack/ftrack-connect/get/master.zip>`_ or
cloning the public repository:


.. code-block:: none

    $ git clone git@bitbucket.org:ftrack/ftrack-connect.git


Then you can build and install the package into your current Python
site-packages folder:


.. code-block:: none

    $ python setup.py install


Alternatively, just build locally and manage yourself:

.. code-block:: none

    $ python setup.py build


Is also possible to build live developmnet version using either:

.. code-block:: none

    $ python setup.py build_ext --inplace


Building documentation from source
----------------------------------

To build the documentation from source:

.. code-block:: none

    $ python setup.py build_sphinx


Then view in your browser::

    file:///path/to/ftrack-connect/build/doc/html/index.html

Running tests against the source
--------------------------------

With a copy of the source it is also possible to run the unit tests:

.. code-block:: none

    $ python setup.py test


There are also interactive tests for many of the widgets that can be run
directly once you have configured your environment to include the built
package:


.. code-block:: none

    $ python test/interactive/timer.py


Dependencies
============

* `Python <http://python.org>`_ >= 2.6, < 3
* `PySide <http://qt-project.org/wiki/PySide>`_ >= 1.2.2, < 2

  .. note::

      On Windows and Osx, PySide does not always put the required ``pyside-rcc``
      runtime in an accessible place. If you encounter build errors when
      installing, try adding the location of ``pyside-rcc`` to your ``PATH``::

      $ set "PATH=C:\Python27\Lib\site-packages\PySide\;%PATH%"

* `Riffle <https://github.com/4degrees/riffle>`_ >= 0.1.0, < 2W
* `QtExt <https://bitbucket.org/ftrack/qtext>`_ >= 0.2.2

Additional For building
-----------------------

* `pyScss <https://github.com/Kronuz/pyScss>`_ >= 1.2.0, < 2
* `Sphinx <http://sphinx-doc.org/>`_ >= 1.2.2, < 2
* `sphinx_rtd_theme <https://github.com/snide/sphinx_rtd_theme>`_ >= 0.1.6, < 1
* `Lowdown <https://bitbucket.org/ftrack/lowdown>`_ >= 0.1.0, < 1

Additional For testing
----------------------

* `Pytest <http://pytest.org>`_  >= 2.3.5
