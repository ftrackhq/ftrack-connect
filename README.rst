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

Once you have a copy of the source you can install it into your site-packages::

    $ python setup.py install

Or just build locally and manage yourself::

    $ python setup.py build

You can also build platform specific applications.

Windows::

    $ python setup.py py2exe

OSX::

    $ python setup.py py2app

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

Additional For testing
----------------------

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

*********************
Copyright and license
*********************

Copyright (c) 2014 ftrack

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this work except in compliance with the License. You may obtain a copy of the
License in the LICENSE.txt file, or at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

