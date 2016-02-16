# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

import webbrowser

from PySide import QtGui, QtCore, QtSvg
import ftrack_api.exception


class ConfigureScenario(QtGui.QWidget):
    '''Configure scenario widget.'''

    #: Signal to emit when configuration is completed.
    configuration_completed = QtCore.Signal()

    def __init__(self, session):
        '''Instantiate the configure scenario widget.'''
        super(ConfigureScenario, self).__init__()

        # Check if user has permissions to configure scenario.
        # TODO: Update this with an actual permission check once available in
        # the API.
        try:
            session.query(
                'Setting where name is "location_scenario" and '
                'group is "LOCATION"'
            ).one()
            can_configure_scenario = True
        except ftrack_api.exception.NoResultFoundError:
            can_configure_scenario = False

        layout = QtGui.QVBoxLayout()
        layout.addSpacing(0)
        layout.setContentsMargins(50, 0, 50, 0)
        self.setLayout(layout)

        layout.addSpacing(100)

        svg_renderer = QtSvg.QSvgRenderer(':ftrack/image/default/cloud-done')
        image = QtGui.QImage(50, 50, QtGui.QImage.Format_ARGB32)

        # Set the ARGB to 0 to prevent rendering artifacts.
        image.fill(0x00000000)

        svg_renderer.render(QtGui.QPainter(image))

        icon = QtGui.QLabel()
        icon.setPixmap(QtGui.QPixmap.fromImage(image))
        icon.setAlignment(QtCore.Qt.AlignCenter)
        icon.setObjectName('icon-label')
        layout.addWidget(icon)

        layout.addSpacing(50)

        label = QtGui.QLabel()
        label.setObjectName('regular-label')
        text = (
            'Hi there, Connect needs to be configured so that ftrack can '
            'store and track your files for you.'
        )

        if can_configure_scenario is False:
            text += (
                '<br><br> You do not have the required permission, please ask '
                'someone with access to system settings in ftrack to '
                'configure it before you proceed.'
            )

        label.setText(text)
        label.setContentsMargins(0, 0, 0, 0)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setWordWrap(True)

        # Min height is required due to issue when word wrap is True and window
        # being resized which cases text to dissapear.
        label.setMinimumHeight(100)

        label.setMinimumWidth(300)
        layout.addWidget(label, alignment=QtCore.Qt.AlignCenter)

        layout.addSpacing(20)

        configure_button = QtGui.QPushButton(text='Configure now')
        configure_button.setObjectName('primary')
        configure_button.clicked.connect(self._configure_location_scenario)
        configure_button.setMinimumHeight(40)
        configure_button.setMaximumWidth(125)

        dismiss_button = QtGui.QPushButton(text='Do it later')
        dismiss_button.clicked.connect(self._complete_configuration)
        dismiss_button.setMinimumHeight(40)
        dismiss_button.setMaximumWidth(125)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(dismiss_button)
        if can_configure_scenario:
            hbox.addSpacing(10)
            hbox.addWidget(configure_button)
        layout.addLayout(hbox)

        layout.addSpacing(20)

        label = QtGui.QLabel()
        label.setObjectName('lead-label')
        label.setText(
            'If you decide to do this later, some of the functionality in '
            'ftrack connect and applications started from connect may not '
            'work as expected.'
        )
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setWordWrap(True)

        # Min height is required due to issue when word wrap is True and window
        # being resized which cases text to dissapear.
        label.setMinimumHeight(100)

        label.setMinimumWidth(300)
        layout.addWidget(label, alignment=QtCore.Qt.AlignCenter)

        layout.addStretch(1)

        label = QtGui.QLabel()
        label.setObjectName('green-link')
        label.setText(
            '<a href="{0}/doc/glossary.html"> Learn more about location '
            'scenarios.'.format(session.server_url)
        )
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setOpenExternalLinks(True)
        layout.addWidget(label, alignment=QtCore.Qt.AlignCenter)
        layout.addSpacing(20)

        self._subscriber_identifier = session.event_hub.subscribe(
            'topic=ftrack.location-scenario.configure-done',
            self._complete_configuration
        )
        self._session = session

    def _complete_configuration(self, event=None):
        '''Finish configuration.'''
        self._session.event_hub.unsubscribe(self._subscriber_identifier)
        self.configuration_completed.emit()

    def _configure_location_scenario(self):
        '''Open browser window and go to the configuration page.'''
        webbrowser.open_new_tab(
            '{0}/#view=configure_location_scenario&itemId=newconfigure'.format(
                self._session.server_url
            )
        )