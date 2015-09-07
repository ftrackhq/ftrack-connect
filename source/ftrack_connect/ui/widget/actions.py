# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import logging
import json

from PySide import QtGui
from PySide import QtCore
import ftrack

import ftrack_connect.asynchronous
import ftrack_connect.error
import ftrack_connect.shared_session

from ftrack_connect.ui.widget import (action_item, flow_layout)


class ActionSection(flow_layout.ScrollingFlowWidget):
    '''Action list view.'''

    launchedAction = QtCore.Signal(dict, name='launchedAction')

    def clear(self):
        '''Remove all actions from section.'''
        items = self.findChildren(action_item.ActionItem)
        for item in items:
            item.setParent(None)

    def addActions(self, actions):
        '''Add *actions* to section'''
        for item in actions:
            actionItem = action_item.ActionItem(item, parent=self)
            actionItem.launchedAction.connect(self._onActionLaunched)
            self.addWidget(actionItem)

    def _onActionLaunched(self, action):
        '''Forward launchedAction signal.'''
        self.launchedAction.emit(action)


class Actions(QtGui.QWidget):
    '''Actions widget. Displays and runs actions with a selectable context.'''

    RECENT_METADATA_KEY = 'ftrack_recent_actions'

    def __init__(self, parent=None):
        '''Initiate a actions view.'''
        super(Actions, self).__init__(parent)

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        self._currentUserId = None
        self._recentActions = []
        self._actions = []

        # TODO: replace for actual combobox
        self._contextSelector = QtGui.QComboBox(self)
        self._contextSelector.addItem('Task 1', {'entityId': '0a2df934-ab42-11e2-9348-040101ad6201', 'entityType': 'task'})
        self._contextSelector.addItem('Task 2', {'entityId': 'da9807c2-7cd5-11e2-808f-f23c91df25eb', 'entityType': 'task'})

        self._contextSelector.currentIndexChanged.connect(
            self._contextSelectorChanged
        )
        self._contextSelector.setFixedHeight(100)
        layout.addWidget(self._contextSelector)

        self._recentSection = ActionSection(self)
        self._recentSection.setFixedHeight(100)
        self._recentSection.launchedAction.connect(self._onActionLaunched)
        layout.addWidget(QtGui.QLabel('Recent'))
        layout.addWidget(self._recentSection)

        self._allSection = ActionSection(self)
        self._allSection.launchedAction.connect(self._onActionLaunched)
        layout.addWidget(QtGui.QLabel('All'))
        layout.addWidget(self._allSection)

        self._updateRecentActions()

    def _onActionLaunched(self, action):
        '''On action launched, save action and add it to top of list.'''
        self._addRecentAction(action['label'])
        self._moveToFront(self._recentActions, action['label'])
        self._updateRecentSection()

    def _contextSelectorChanged(self, currentIndex):
        '''Load new actions when the context has changed'''
        context = self._contextSelector.itemData(currentIndex)
        self.logger.debug('Context changed: {0}'.format(context))
        self._recentSection.clear()
        self._allSection.clear()
        self._loadActionsForContext([context])

    def _updateRecentSection(self):
        '''Clear and update actions in recent section.'''
        self._recentSection.clear()
        recentActions = []
        for recentAction in self._recentActions:
            for action in self._actions:
                if action[0]['label'] == recentAction:
                    recentActions.append(action)

        self._recentSection.addActions(recentActions)

    def _updateAllSection(self):
        '''Clear and update actions in all section.'''
        self._allSection.clear()
        self._allSection.addActions(self._actions)

    @ftrack_connect.asynchronous.asynchronous
    def _updateRecentActions(self):
        '''Retrieve and update recent actions.'''
        self._recentActions = self._getRecentActions()
        self._updateRecentSection()

    def _getCurrentUserId(self):
        '''Return current user id.'''
        if not self._currentUserId:
            session = ftrack_connect.shared_session.get_shared_session()
            user = session.query(
                'User where username="{0}"'.format(session.api_user)
            ).one()
            self._currentUserId = user['id']

        return self._currentUserId

    def _getRecentActions(self):
        '''Retrieve recent actions from the server.'''
        session = ftrack_connect.shared_session.get_shared_session()

        metadata = session.query(
            'Metadata where key is "{0}" and parent_type is "User" '
            'and parent_id is "{1}"'.format(
                self.RECENT_METADATA_KEY, self._getCurrentUserId()
            )
        ).first()

        recentActions = []
        if metadata:
            try:
                recentActions = json.loads(metadata['value'])
            except ValueError as error:
                self.logger.warning(
                    'Error parsing metadata: {0}'.format(metadata)
                )
        return recentActions

    def _moveToFront(self, itemList, item):
        '''Prepend or move *item* to front of *itemList*.'''
        try:
            itemList.remove(item)
        except ValueError:
            pass
        itemList.insert(0, item)

    @ftrack_connect.asynchronous.asynchronous
    def _addRecentAction(self, actionLabel):
        '''Add *actionLabel* to recent actions, persisting the change.'''
        session = ftrack_connect.shared_session.get_shared_session()

        recentActions = self._getRecentActions()
        self._moveToFront(recentActions, actionLabel)
        encodedRecentActions = json.dumps(recentActions)
        session.ensure('Metadata', {
            'parent_type': 'User',
            'parent_id': self._getCurrentUserId(),
            'key': self.RECENT_METADATA_KEY,
            'value': encodedRecentActions
        }, identifying_keys=['parent_type', 'parent_id', 'key'])

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

        # Flatten structure
        discoveredActions = []
        for result in results:
            discoveredActions.extend(result.get('items', []))

        # Sort actions by label
        groupedActions = []
        for action in discoveredActions:
            action['selection'] = context
            added = False
            for groupedAction in groupedActions:
                if action['label'] == groupedAction[0]['label']:
                    groupedAction.append(action)
                    added = True

            if not added:
                groupedActions.append([action])

        # Sort actions by label
        groupedActions = sorted(
            groupedActions,
            key=lambda groupedAction: groupedAction[0]['label'].lower()
        )

        self.logger.debug('Discovered actions: {0}'.format(groupedActions))
        self._actions = groupedActions
        self._updateRecentSection()
        self._updateAllSection()
