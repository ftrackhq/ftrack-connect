# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

def is_webwidget_supported():
    ''' Return True if either QtWebEngine or QtWebKit is available.'''
    try:
        from QtExt import QtWebEngineWidgets
        return True
    except ImportError:
        pass

    try:
        from QtExt import QtWebKitWidgets
        return True
    except ImportError:
        pass

    return False
