# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import logging

from PySide import QtGui
from PySide import QtCore
import ftrack

import ftrack_connect.asynchronous
import ftrack_connect.error


class ActionItem(QtGui.QStandardItem):
    '''Represent an action item.'''

    def __init__(self, action=None):
        super(ActionItem, self).__init__()
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        if action is None:
            action = {}

        self.setData(action)
        self.setText(action.get('label', 'Action'))
        self.setIcon(QtGui.QIcon(QtGui.QPixmap(
            ':/ftrack/image/action/{0}'.format(action.get('icon', 'default'))
        )))
        self.setBackground(QtGui.QBrush(QtCore.Qt.white))
        self.setSizeHint(QtCore.QSize(80, 80))


class ActionListView(QtGui.QListView):
    '''Action list view.'''

    launchedAction = QtCore.Signal(dict, name='launchedAction')

    def __init__(self):
        '''Initiate a actions view.'''
        super(ActionListView, self).__init__()
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self.setViewMode(QtGui.QListView.IconMode)
        self.setWordWrap(True)
        self.setSpacing(10)
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)

        self.setModel(QtGui.QStandardItemModel(self))

        self.clicked.connect(self._onActionClicked)

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

    def _onActionClicked(self, currentIndex):
        '''Initiate a actions view.'''
        action = self.model().itemFromIndex(currentIndex).data()
        self.logger.debug('Action item clicked: {0}'.format(action))

        results = ftrack.EVENT_HUB.publish(
            ftrack.Event(
                topic='ftrack.action.launch',
                data=dict(
                    actionIdentifier=action.get('actionIdentifier'),
                    applicationIdentifier=action.get('applicationIdentifier'),
                    selection=action.get('selection', []),
                    actionData=action
                )
            ),
            synchronous=True
        )
        self.logger.debug('Launched action with result: {0}'.format(results))
        self.launchedAction.emit(action)


class Actions(QtGui.QWidget):
    '''Actions widget. Displays and runs actions with a selectable context.'''

    def __init__(self, parent=None):
        '''Initiate a actions view.'''
        super(Actions, self).__init__(parent)

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        # TODO: replace for actual combobox
        self._contextSelector = QtGui.QComboBox(self)
        self._contextSelector.addItem('Task 1', {'entityId': '0a2df934-ab42-11e2-9348-040101ad6201', 'entityType': 'task'})
        self._contextSelector.addItem('Task 2', {'entityId': 'da9807c2-7cd5-11e2-808f-f23c91df25eb', 'entityType': 'task'})

        self._contextSelector.currentIndexChanged.connect(
            self._contextSelectorChanged
        )
        self._contextSelector.setFixedHeight(100)
        layout.addWidget(self._contextSelector)

        self._recentSectionView = ActionListView()
        self._recentSectionView.setFixedHeight(100)
        self._recentSectionView.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )
        self._recentSectionView.launchedAction.connect(self._onActionLaunched)
        layout.addWidget(QtGui.QLabel('Recent'))
        layout.addWidget(self._recentSectionView)

        self._allSectionView = ActionListView()
        self._allSectionView.launchedAction.connect(self._onActionLaunched)
        layout.addWidget(QtGui.QLabel('All'))
        layout.addWidget(self._allSectionView)

    def _onActionLaunched(self, action):
        self._recentSectionView.model().appendRow(ActionItem(action))

    def _contextSelectorChanged(self, currentIndex):
        '''Load new actions when the context has changed'''
        context = self._contextSelector.itemData(currentIndex)
        self.logger.debug('Context changed: {0}'.format(context))
        self._allSectionView.model().clear()
        self._loadActionsForContext([context])

    def _updateActions(self, actions):
        '''Update actions to *actions*'''
        self._allSectionView.model().clear()
        for action in actions:
            self._allSectionView.model().appendRow(ActionItem(action))

    def _loadActionsForContext(self, context):
        '''Obtain new actions synchronously for *context*.'''
        results = ftrack.EVENT_HUB.publish(
            ftrack.Event(
                topic='ftrack.action.discover',
                data=dict(
                    selection=context
                )
            ),
            synchronous=True
        )
        discoveredActions = []
        for result in results:
            discoveredActions.extend(result.get('items', []))

        for action in discoveredActions:
            action['selection'] = context

        self.logger.debug('Discovered actions: {0}'.format(discoveredActions))
        self._updateActions(discoveredActions)

