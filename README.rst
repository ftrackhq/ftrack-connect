##############
ftrack connect
##############

Core for ftrack connect.

***********************
Development environment
***********************

Mac OS X
========

Installing package and PySide
-----------------------------

1. Make sure you have homebrew installed (http://brew.sh/)
2. Install PySide dependecies: ``brew install qt cmake``
3. Create & activate a new virtualenv (https://virtualenv.pypa.io)
4. Install PySide in your virtualenv: ``pip install -U PySide`` (This will take a while)
5. Install the ftrack-connect package: ``pip install .``

Compile style and resource
--------------------------

1. Install Ruby and Compass (http://compass-style.org/install/)
2. Build with ``python build.py``

Run ftrack connect
------------------

1. ``python -m ftrack_connect``.

*************
Documentation
*************

Full documentation can be found at https://doc.ftrack.com/ftrack-connect
