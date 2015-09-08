# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import logging
import json

from PySide import QtGui
from PySide import QtCore
import ftrack

import ftrack_connect.asynchronous
import ftrack_connect.error
import ftrack_connect.session

from ftrack_connect.ui.widget import (action_item, flow_layout, entity_selector)


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
    RECENT_ACTIONS_LENGTH = 20

    def __init__(self, parent=None):
        '''Initiate a actions view.'''
        super(Actions, self).__init__(parent)

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        self._session = ftrack_connect.session.get_session()

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        self._currentUserId = None
        self._recentActions = []
        self._actions = []

        self._entitySelector = entity_selector.EntitySelector()
        self._entitySelector.setFixedHeight(50)
        self._entitySelector.entityChanged.connect(
            self._onEntityChanged
        )
        layout.addWidget(QtGui.QLabel('Select action context'))
        layout.addWidget(self._entitySelector)

        self._recentLabel = QtGui.QLabel('Recent')
        layout.addWidget(self._recentLabel)
        self._recentSection = ActionSection(self)
        self._recentSection.setFixedHeight(100)
        self._recentSection.launchedAction.connect(self._onActionLaunched)
        layout.addWidget(self._recentSection)

        self._allLabel = QtGui.QLabel('Discovering actions..')
        self._allLabel.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self._allLabel)
        self._allSection = ActionSection(self)
        self._allSection.launchedAction.connect(self._onActionLaunched)
        layout.addWidget(self._allSection)

        self._loadActionsForContext([])
        self._updateRecentActions()

    def _onActionLaunched(self, action):
        '''On action launched, save action and add it to top of list.'''
        self._addRecentAction(action['label'])
        self._moveToFront(self._recentActions, action['label'])
        self._updateRecentSection()

    def _onEntityChanged(self, entity):
        '''Load new actions when the context has changed'''
        context = []
        try:
            context = [{
                'entityId': entity.get('entityId'),
                'entityType': entity.get('entityType'),
            }]
            self.logger.debug(u'Context changed: {0}'.format(context))
        except Exception:
            self.logger.debug(u'Invalid entity: {0}'.format(entity))

        self._recentSection.clear()
        self._allSection.clear()
        self._loadActionsForContext(context)

    def _updateRecentSection(self):
        '''Clear and update actions in recent section.'''
        self._recentSection.clear()
        recentActions = []
        for recentAction in self._recentActions:
            for action in self._actions:
                if action[0]['label'] == recentAction:
                    recentActions.append(action)

        if recentActions:
            self._recentSection.addActions(recentActions)
            self._recentLabel.show()
            self._recentSection.show()
        else:
            self._recentLabel.hide()
            self._recentSection.hide()

    def _updateAllSection(self):
        '''Clear and update actions in all section.'''
        self._allSection.clear()
        if self._actions:
            self._allSection.addActions(self._actions)
            self._allLabel.setAlignment(QtCore.Qt.AlignLeft)
            self._allLabel.setText('All actions')
        else:
            self._allLabel.setAlignment(QtCore.Qt.AlignCenter)
            self._allLabel.setText(
                '<h2 style="font-weight: normal">No actions found</h2>'
                '<p>Try another selection or add some actions.</p>'
            )

    @ftrack_connect.asynchronous.asynchronous
    def _updateRecentActions(self):
        '''Retrieve and update recent actions.'''
        self._recentActions = self._getRecentActions()
        self._updateRecentSection()

    def _getCurrentUserId(self):
        '''Return current user id.'''
        if not self._currentUserId:

            user = self._session.query(
                'User where username="{0}"'.format(self._session.api_user)
            ).one()
            self._currentUserId = user['id']

        return self._currentUserId

    def _getRecentActions(self):
        '''Retrieve recent actions from the server.'''

        metadata = self._session.query(
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
        recentActions = self._getRecentActions()
        self._moveToFront(recentActions, actionLabel)
        recentActions = recentActions[:self.RECENT_ACTIONS_LENGTH]
        encodedRecentActions = json.dumps(recentActions)

        self._session.ensure('Metadata', {
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
             if result:
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
