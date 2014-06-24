##############
ftrack connect
##############

Core for ftrack connect.

************
Installation
************

.. highlight:: bash

Installation is simple with `pip <http://www.pip-installer.org/>`_::

    $ pip install git+git@bitbucket.org:ftrack/ftrack-connect.git

.. note::

    This project is not yet available on PyPi.

Alternatively, you may wish to build manually from the source.

You can clone the public repository::

    $ git clone git@bitbucket.org:ftrack/ftrack-connect.git

Or download the
`zipball <https://bitbucket.org/ftrack/ftrack-connect/get/master.zip>`_

Once you have a copy of the source, you can embed it in your Python package,
or install it into your site-packages::

    $ python setup.py install

Dependencies
============

* `Python <http://python.org>`_ >= 2.6, < 3
* `PySide <http://qt-project.org/wiki/PySide>`_ >= 1.1.0, < 2

  .. note::

      On Windows, PySide does not always put the required ``pyside-rcc``
      runtime in an accessible place. If you encounter build errors when
      installing, try adding the location of ``pyside-rcc`` to your ``PATH``::

      $ set "PATH=C:\Python27\Lib\site-packages\PySide\;%PATH%"

* `pyScss <https://github.com/Kronuz/pyScss>`_ >= 1.2.0, < 2
* `Harmony <https://github.com/4degrees/harmony/>`_

For testing:

* `Pytest <http://pytest.org>`_  >= 2.3.5

*****
Usage
*****

Run the service::

    $ python -m ftrack_connect

*************
Documentation
*************

Full documentation can be found at https://doc.ftrack.com/ftrack-connect
