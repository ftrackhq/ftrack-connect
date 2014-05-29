##############
ftrack connect
##############

Core for ftrack connect.

***********************
Development environment
***********************

Mac OS X
========

1. Make sure you have homebrew installed (http://brew.sh/)
2. Install PySide dependecies: ``brew install qt cmake``
3. Create & activate a new virtualenv (e.g. mkvirtualenv ftrack-connect)
4. Install PySide in your virtualenv: ``pip install -U PySide`` (This will take a while)
5. Install the ftrack-connect package: ``pip install .``
6. Run it: ``python -m ftrack_connect``.

*************
Documentation
*************

Full documentation can be found at https://doc.ftrack.com/ftrack-connect