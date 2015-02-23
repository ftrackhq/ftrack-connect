# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os

from PySide import QtCore, QtGui
import ftrack

from browse_tasks import BrowseTasksWidget
from ftrack_connect.connector import HelpFunctions
import browse_tasks_small_rc


class Ui_BrowseTasksSmall(object):

    def setupUi(self, BrowseTasksSmall):
        BrowseTasksSmall.setObjectName("BrowseTasksSmall")
        BrowseTasksSmall.resize(220, 49)
        self.verticalLayout = QtGui.QVBoxLayout(BrowseTasksSmall)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.shotLabel = QtGui.QLabel(BrowseTasksSmall)
        self.shotLabel.setMaximumSize(QtCore.QSize(75, 16777215))
        self.shotLabel.setObjectName("shotLabel")
        self.horizontalLayout.addWidget(self.shotLabel)
        self.browseTasksButton = QtGui.QPushButton(BrowseTasksSmall)
        self.browseTasksButton.setMinimumSize(QtCore.QSize(0, 27))
        self.browseTasksButton.setMaximumSize(QtCore.QSize(16777215, 27))
        self.browseTasksButton.setObjectName("browseTasksButton")
        self.horizontalLayout.addWidget(self.browseTasksButton)
        self.cancelButton = QtGui.QPushButton(BrowseTasksSmall)
        self.cancelButton.setEnabled(True)
        self.cancelButton.setMinimumSize(QtCore.QSize(0, 27))
        self.cancelButton.setMaximumSize(QtCore.QSize(16777215, 27))
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.homeButton = QtGui.QPushButton(BrowseTasksSmall)
        self.homeButton.setMinimumSize(QtCore.QSize(27, 27))
        self.homeButton.setMaximumSize(QtCore.QSize(16777215, 27))
        self.homeButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/home.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.homeButton.setIcon(icon)
        self.homeButton.setIconSize(QtCore.QSize(18, 18))
        self.homeButton.setObjectName("homeButton")
        self.horizontalLayout.addWidget(self.homeButton)
        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 4)
        self.horizontalLayout.setStretch(2, 4)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(BrowseTasksSmall)
        QtCore.QObject.connect(
            self.browseTasksButton, QtCore.SIGNAL("clicked()"),
            BrowseTasksSmall.showHideTree
        )
        QtCore.QObject.connect(
            self.cancelButton, QtCore.SIGNAL("clicked()"),
            BrowseTasksSmall.closeTree
        )
        QtCore.QObject.connect(
            self.homeButton, QtCore.SIGNAL("clicked()"),
            BrowseTasksSmall.goHome
        )
        QtCore.QMetaObject.connectSlotsByName(BrowseTasksSmall)

    def retranslateUi(self, BrowseTasksSmall):
        BrowseTasksSmall.setWindowTitle(QtGui.QApplication.translate(
            "BrowseTasksSmall", "Form", None, QtGui.QApplication.UnicodeUTF8)
        )
        self.shotLabel.setText(QtGui.QApplication.translate(
            "BrowseTasksSmall", "Shot: ", None, QtGui.QApplication.UnicodeUTF8)
        )
        self.browseTasksButton.setText(QtGui.QApplication.translate(
            "BrowseTasksSmall", "Select Task", None,
            QtGui.QApplication.UnicodeUTF8)
        )
        self.cancelButton.setText(QtGui.QApplication.translate(
            "BrowseTasksSmall", "Cancel", None, QtGui.QApplication.UnicodeUTF8)
        )


class BrowseTasksSmallWidget(QtGui.QWidget):
    clickedIdSignal = QtCore.Signal(str, name='clickedIdSignal')

    def __init__(self, parent, task=None, browseMode='Shot'):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_BrowseTasksSmall()
        self.ui.setupUi(self)
        self.showing = False
        self.parent = parent
        self.ui.cancelButton.hide()

        self.browseMode = browseMode
        self.initPaths()

        self.backgroundLabel = QtGui.QLabel()

        self.ui.browseTasksButton.setText(self.currentpath)

        self.browseTasksWidget = BrowseTasksWidget(
            parent, startId=self.currentId, browseMode=browseMode
        )
        self.browseTasksWidget.hide()
        QtCore.QObject.connect(self.browseTasksWidget.ui.BrowseTasksTreeView,
                               QtCore.SIGNAL("doubleClicked(QModelIndex)"),
                               self.showHideTree)
        self.topPosition = 0
        self.update()

    def initPaths(self):
        if self.browseMode == 'Shot':
            shot = ftrack.Shot(os.environ['FTRACK_SHOTID'])
            self.currentpath = HelpFunctions.getPath(shot)
            self.currentId = shot.getId()
            self.homeId = os.environ['FTRACK_SHOTID']
        else:
            task = ftrack.Task(os.environ['FTRACK_TASKID'])
            self.currentpath = HelpFunctions.getPath(task)
            self.currentId = task.getId()
            self.homeId = os.environ['FTRACK_TASKID']

    @QtCore.Slot()
    def showHideTree(self):
        if not self.showing:
            self.ui.cancelButton.show()

            windowWidth = self.width()
            windowHeight = self.parent.height()

            ypos = self.topPosition
            heigth = windowHeight - self.height() - self.topPosition

            self.browseTasksWidget.setGeometry(
                9, ypos + 6, windowWidth, heigth
            )
            self.browseTasksWidget.show()
            self.browseTasksWidget.raise_()

            self.showing = True
            self.ui.browseTasksButton.setText('Select')
        else:
            self.showing = False
            self.ui.cancelButton.hide()
            self.currentId = self.browseTasksWidget.getCurrentId()
            self.currentpath = self.browseTasksWidget.getCurrentPath()
            self.update()
            self.browseTasksWidget.hide()

    def update(self):
        if self.currentpath:
            self.ui.browseTasksButton.setText(self.currentpath + ' (change)')
            self.clickedIdSignal.emit(self.currentId)
            self.browseTasksWidget.hide()
        else:
            self.ui.browseTasksButton.setText('Select')

    @QtCore.Slot()
    def updateTask(self):
        self.initPaths()
        self.update()

    def setTopPosition(self, topInt):
        self.topPosition = topInt + self.height() - 7

    def setLabelText(self, textLabel):
        self.ui.shotLabel.setText(textLabel)

    def closeTree(self):
        self.showing = False
        self.ui.cancelButton.hide()
        self.browseTasksWidget.hide()
        self.ui.browseTasksButton.setText(self.currentpath + ' (change)')

    def goHome(self):
        self.initPaths()
        self.update()
