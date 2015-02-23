# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os

from PySide import QtCore, QtGui
import ftrack

from ftrack_connect.connector import HelpFunctions


class Ui_BrowseTasks(object):

    def setupUi(self, BrowseTasks):
        BrowseTasks.setObjectName("BrowseTasks")
        BrowseTasks.resize(946, 660)
        BrowseTasks.setAutoFillBackground(True)
        self.horizontalLayout = QtGui.QHBoxLayout(BrowseTasks)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.BrowseProjectComboBox = QtGui.QComboBox(BrowseTasks)
        self.BrowseProjectComboBox.setMaximumSize(QtCore.QSize(150, 30))
        self.BrowseProjectComboBox.setObjectName("BrowseProjectComboBox")
        self.verticalLayout.addWidget(self.BrowseProjectComboBox)
        self.BrowseTasksTreeView = QtGui.QTreeView(BrowseTasks)
        palette = QtGui.QPalette()
        self.BrowseTasksTreeView.setPalette(palette)
        self.BrowseTasksTreeView.setStyleSheet("")
        self.BrowseTasksTreeView.setEditTriggers(
            QtGui.QAbstractItemView.NoEditTriggers
        )
        self.BrowseTasksTreeView.setIndentation(10)
        self.BrowseTasksTreeView.setObjectName("BrowseTasksTreeView")
        self.BrowseTasksTreeView.header().setVisible(False)
        self.verticalLayout.addWidget(self.BrowseTasksTreeView)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(BrowseTasks)
        QtCore.QObject.connect(
            self.BrowseTasksTreeView, QtCore.SIGNAL("clicked(QModelIndex)"),
            BrowseTasks.updateAssetView
        )
        QtCore.QObject.connect(
            self.BrowseProjectComboBox,
            QtCore.SIGNAL("currentIndexChanged(QString)"),
            BrowseTasks.setProjectFilter
        )
        QtCore.QMetaObject.connectSlotsByName(BrowseTasks)

    def retranslateUi(self, BrowseTasks):
        BrowseTasks.setWindowTitle(QtGui.QApplication.translate(
            "BrowseTasks", "Form", None, QtGui.QApplication.UnicodeUTF8)
        )


class BrowseTasksItem(QtGui.QStandardItem):

    def __init__(self, text, version=False):
        QtGui.QStandardItem.__init__(self, text)
        self.version = version

    def __lt__(self, other):
        if self.version:
            return QtGui.QStandardItem.__lt__(self, other)
        else:
            return QtGui.QStandardItem.__lt__(self, other)


class BrowseTasksWidget(QtGui.QWidget):
    clickedIdSignal = QtCore.Signal(str, name='clickedIdSignal')

    def __init__(self, parent, task=None, startId=None, browseMode='Shot'):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_BrowseTasks()
        self.ui.setupUi(self)
        self.parentIds = []

        self.browseMode = browseMode
        self.showShots = True

        self.currentPath = None

        if startId:
            self.startId = startId
            self.setStartId(startId)
        else:
            self.startId = None

        self.ui.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.ui.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.currentId = None

        self.ui.BrowseTasksViewModel = QtGui.QStandardItemModel()

        self.ui.BrowseTasksSelectionModel = QtGui.QItemSelectionModel(
            self.ui.BrowseTasksViewModel
        )

        self.ui.BrowseProjectComboBoxModel = QtGui.QStandardItemModel()
        self.ui.BrowseProjectComboBox.setModel(
            self.ui.BrowseProjectComboBoxModel
        )

        itemProjCombo = BrowseTasksItem('Show All')
        itemProjCombo.id = ''
        itemProjCombo.type = 'show'

        self.ui.BrowseProjectComboBoxModel.appendRow(itemProjCombo)

        projects = ftrack.getProjects()
        filterOnThis = ''
        projects = sorted(projects, key=lambda a: a.getName().lower())
        for proj in projects:
            projName = '[' + proj.getName() + '] ' + proj.getFullName()
            projId = proj.getId()
            projType = 'show'

            itemProj = BrowseTasksItem(projName)
            itemProj.id = projId
            itemProj.type = projType

            self.ui.BrowseTasksViewModel.appendRow(itemProj)

            itemProjCombo = BrowseTasksItem(projName)
            itemProjCombo.id = projId
            itemProjCombo.type = projType

            self.ui.BrowseProjectComboBoxModel.appendRow(itemProjCombo)

            shot = ftrack.Task(os.environ['FTRACK_SHOTID'])
            proj_root = shot.getProject().getName()

            if proj_root == proj.getName():
                self.ui.BrowseProjectComboBox.setCurrentIndex(
                    self.ui.BrowseProjectComboBoxModel.rowCount() - 1)
                filterOnThis = projName

        self.setProjectFilter(filterOnThis)

        self.ui.BrowseTasksTreeView.setModel(self.ui.BrowseTasksViewModel)
        self.ui.BrowseTasksTreeView.setSelectionModel(
            self.ui.BrowseTasksSelectionModel
        )
        self.ui.BrowseTasksTreeView.setSortingEnabled(False)

        if startId:
            self.currentId = startId

    @QtCore.Slot(QtCore.QModelIndex, bool)
    def updateAssetView(self, modelindex, updateCurrentPath=True):
        clickedItem = self.ui.BrowseTasksViewModel.itemFromIndex(modelindex)
        expand = None
        select = None

        if clickedItem.type == 'show':
            clickedTask = ftrack.Project(clickedItem.id)
        elif clickedItem.type == 'task':
            clickedTask = ftrack.Task(clickedItem.id)
        elif clickedItem.type == 'asset':
            clickedTask = ftrack.Asset(clickedItem.id)
        elif clickedItem.type == 'asset_version':
            clickedTask = ftrack.AssetVersion(clickedItem.id)
        elif clickedItem.type == 'assettake':
            clickedTask = ftrack.Component(clickedItem.id)
        else:
            pass
        try:
            clickedObjectType = clickedTask.getObjectType()
        except:
            clickedObjectType = 'Unset'

        if not clickedItem.hasChildren():
            childList = []

            if clickedItem.type in ['show', 'task']:
                if clickedObjectType != 'Sequence' or self.showShots:
                    children = clickedTask.getChildren()

                    expand, select, expandItem, selectItem, retchildList = self.getTreeChildren(
                        clickedItem, children
                    )
                    childList += retchildList

                    if self.browseMode == 'Task':
                        tasks = clickedTask.getTasks()
                        expandTask, selectTask, expandItemTask, selectItemTask, retchildList = self.getTreeChildren(
                            clickedItem, tasks
                        )
                        childList += retchildList

                        if not expand:
                            expandItem = expandItemTask
                            expand = expandTask

                        if not select:
                            selectItem = selectItemTask
                            select = selectTask

            if len(childList) > 0:
                sortedchildlist = sorted(
                    childList, key=lambda a: a.text().lower()
                )
                clickedItem.appendColumn(sortedchildlist)

        self.ui.BrowseTasksTreeView.setModel(self.ui.BrowseTasksViewModel)
        self.ui.BrowseTasksTreeView.expand(modelindex)

        self.currentId = clickedItem.id
        if expand:
            self.updateAssetView(
                self.ui.BrowseTasksViewModel.indexFromItem(expandItem)
            )
        elif select:
            sortIndex = self.ui.BrowseTasksViewModel.indexFromItem(selectItem)
            self.ui.BrowseTasksSelectionModel.select(
                sortIndex,
                QtGui.QItemSelectionModel.Clear |
                QtGui.QItemSelectionModel.Select
            )
            self.currentId = self.startId
            self.clickedIdSignal.emit(self.startId)
            task = ftrack.Task(self.startId)
            self.currentPath = HelpFunctions.getPath(task)
        else:
            if updateCurrentPath == True:
                self.currentPath = HelpFunctions.getPath(clickedTask)
                self.clickedIdSignal.emit(clickedItem.id)

    def getTreeChildren(self, clickedItem, children):
        expand = None
        select = None
        expandItem = None
        selectItem = None
        childList = []
        if len(children) > 0:
            childList = list()
            for child in children:
                if clickedItem.type == 'asset':
                    childName = 'v' + str(child.getVersion()).zfill(4)
                else:
                    childName = child.getName()
                    if childName == '':
                        continue
                itemChild = BrowseTasksItem(str(childName))
                itemChild.id = child.getId()

                try:
                    itemChild.type = child.get('entityType')
                except:
                    itemChild.type = 'asset_version'
                    itemChild.version = True
                if itemChild.id != clickedItem.id:
                    childList.append(itemChild)
                    if itemChild.id in self.parentIds:
                        expand = itemChild.id
                        expandItem = itemChild
                    elif itemChild.id == self.startId:
                        select = itemChild.id
                        selectItem = itemChild
        return expand, select, expandItem, selectItem, childList

    @QtCore.Slot(str)
    def setProjectFilter(self, projectfilter):
        if projectfilter == 'Show All':
            projectfilter = ''

        rowCount = self.ui.BrowseTasksViewModel.rowCount()
        for i in range(rowCount):
            tableItem = self.ui.BrowseTasksViewModel.item(i, 0)
            rootItem = self.ui.BrowseTasksViewModel.invisibleRootItem().index()

            if projectfilter not in tableItem.text():
                showMe = True
            else:
                showMe = False
            self.ui.BrowseTasksTreeView.setRowHidden(i, rootItem, showMe)

        foundItems = self.ui.BrowseTasksViewModel.findItems(projectfilter)
        if len(foundItems) > 0:
            for item in foundItems:
                self.updateAssetView(item.index(), updateCurrentPath=False)

    def getCurrentId(self):
        return self.currentId

    def getCurrentPath(self):
        return self.currentPath
        try:
            task = ftrack.Task(self.currentId)
            shotpath = task.getName()
            taskParents = task.getParents()

            for parent in taskParents:
                shotpath = parent.getName() + '.' + shotpath

            self.currentPath = shotpath
            return self.currentPath
        except:
            return None

    def setStartId(self, fid):
        shot = ftrack.Task(fid)
        parents = shot.getParents()
        self.parentIds = [x.getId() for x in parents]

    def setShowTasks(self, val):
        if val == True:
            self.browseMode = 'Task'
        else:
            self.browseMode = 'Shot'

    def setShowShots(self, val):
        self.showShots = val
