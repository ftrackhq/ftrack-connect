# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import os
import getpass

from QtExt import QtWidgets

from ftrack_connect.connector import PanelComInstance
from ftrack_connect.ui.widget.web_view import WebViewWidget
from ftrack_connect.ui.widget import header


class FtrackInfoDialog(QtWidgets.QDialog):
    '''Info dialog class.'''

    def __init__(self, parent=None, connector=None):
        '''Instantiate info dialog class with *connector*.'''
        super(FtrackInfoDialog, self).__init__(parent=parent)
        self.connector = connector

        self.setMinimumWidth(400)
        self.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
            )
        )

        self.centralwidget = QtWidgets.QWidget(self)
        self.verticalMainLayout = QtWidgets.QVBoxLayout(self)
        self.horizontalLayout = QtWidgets.QHBoxLayout()

        shotId = os.getenv('FTRACK_SHOTID')
        taskId = os.getenv('FTRACK_TASKID', shotId)

        self.headerWidget = header.Header(getpass.getuser(), self)

        self.verticalMainLayout.addWidget(self.headerWidget)

        self.infoWidget = WebViewWidget(self.centralwidget)
        self.horizontalLayout.addWidget(self.infoWidget)
        self.verticalMainLayout.addLayout(self.horizontalLayout)

        self.setObjectName('ftrackInfo')
        self.setWindowTitle('ftrackInfo')

        self.homeTaskId = taskId

        self.setObject(taskId)

        panelComInstance = PanelComInstance.instance()
        panelComInstance.addInfoListener(self.updateObj)

    def setObject(self, taskId):
        '''Set object to *taskId*.'''
        obj = self.connector.objectById(taskId)
        url = obj.getWebWidgetUrl('info', theme='tf')
        self.infoWidget.setUrl(url)

    def updateObj(self, taskId):
        '''Update with *taskId*.'''
        self.setObject(taskId)
