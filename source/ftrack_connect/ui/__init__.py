# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

# Import QtSvg and QtXml to force load libraries needed to display
# SVG on Windows.
import os
from Qt import QtSvg
from Qt import QtXml


# Load UI resources such as icons.
from . import resource as _resource
from ftrack_connect import load_icons

fonts = os.path.join(os.path.dirname(__file__), '..', 'fonts')
load_icons(fonts)
