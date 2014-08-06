# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtCore
import ftrack


class TopicThread(QtCore.QThread):
    '''Thread to listen on ftrack's topics hub.'''

    def run(self):
        '''Run the topic thread.'''
        ftrack.EVENT_HUB.wait()
