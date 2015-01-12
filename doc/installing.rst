..
    :copyright: Copyright (c) 2014 ftrack

.. _installing:

**********
Installing
**********

.. highlight:: bash

Pre-built packages are available for download for Windows and Mac at
https://www.ftrack.com/downloads

Alternatively, install using `pip <http://www.pip-installer.org/>`_::

    pip install git+https://bitbucket.org/ftrack/ftrack-connect.git

.. note::

    This project is not yet available on PyPi.

Building from source
====================

You can also build manually from the source for more control. First obtain a
copy of the source by either downloading the
`zipball <https://bitbucket.org/ftrack/ftrack-connect/get/master.zip>`_ or
cloning the public repository::

    git clone git@bitbucket.org:ftrack/ftrack-connect.git

Then you can build and install the package into your current Python
site-packages folder::

    python setup.py install

Alternatively, just build locally and manage yourself::

    python setup.py build

Building documentation from source
----------------------------------

To build the documentation from source::

    python setup.py build_sphinx

Then view in your browser::

    file:///path/to/ftrack-connect/build/doc/html/index.html

Running tests against the source
--------------------------------

With a copy of the source it is also possible to run the unit tests::

    python setup.py test

There are also interactive tests for many of the widgets that can be run
directly once you have configured your environment to include the built
package::

    python test/interactive/timer.py

Dependencies
============

* `Python <http://python.org>`_ >= 2.6, < 3
* `PySide <http://qt-project.org/wiki/PySide>`_ >= 1.2.2, < 2

  .. note::

      On Windows, PySide does not always put the required ``pyside-rcc``
      runtime in an accessible place. If you encounter build errors when
      installing, try adding the location of ``pyside-rcc`` to your ``PATH``::

      $ set "PATH=C:\Python27\Lib\site-packages\PySide\;%PATH%"

* `Riffle <https://github.com/4degrees/riffle>`_ >= 0.1.0, < 2
* ftrack Python API (Download from your ftrack server and make available on
  ``PYTHONPATH``)

Additional For building
-----------------------

* `pyScss <https://github.com/Kronuz/pyScss>`_ >= 1.2.0, < 2
* `Sphinx <http://sphinx-doc.org/>`_ >= 1.2.2, < 2
* `sphinx_rtd_theme <https://github.com/snide/sphinx_rtd_theme>`_ >= 0.1.6, < 1
* `Lowdown <https://bitbucket.org/ftrack/lowdown>`_ >= 0.1.0, < 1

Additional For testing
----------------------

* `Pytest <http://pytest.org>`_  >= 2.3.5
