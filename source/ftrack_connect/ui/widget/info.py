# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import os

from PySide import QtGui

from ftrack_connect.connector import PanelComInstance
from ftrack_connect.ui.widget.web_view import WebViewWidget
from ftrack_connect.ui.widget.header import HeaderWidget


class FtrackInfoDialog(QtGui.QDialog):

    def __init__(self, parent=None, connector=None):
        super(FtrackInfoDialog, self).__init__(parent=parent)
        self.connector = connector

        self.setMinimumWidth(400)
        self.setSizePolicy(
            QtGui.QSizePolicy(
                QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
            )
        )

        self.centralwidget = QtGui.QWidget(self)
        self.verticalMainLayout = QtGui.QVBoxLayout(self)
        self.horizontalLayout = QtGui.QHBoxLayout()

        shotId = os.getenv('FTRACK_SHOTID')
        taskId = os.getenv('FTRACK_TASKID', shotId)

        self.headerWidget = HeaderWidget(self)

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
        obj = self.connector.objectById(taskId)
        self.headerWidget.setTitle('Info panel')
        url = obj.getWebWidgetUrl('info', theme='tf')
        self.infoWidget.setUrl(url)

    def updateObj(self, taskId):
        self.setObject(taskId)
