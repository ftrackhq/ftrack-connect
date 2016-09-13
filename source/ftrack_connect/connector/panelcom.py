# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

# Class for handling communication between panels
from QtExt import QtCore, QtGui

#: TODO: Rewrite this to use ftrack events instead.


class PanelCommunicator(QtCore.QObject):
    '''Communcator widget used to broadcast events between plugin dialogs.'''

    publishProgressSignal = QtCore.Signal(int, name='publishProgressSignal')

    def __init__(self):
        '''Initialise panel.'''
        super(PanelCommunicator, self).__init__()

        self.refListeners = []
        self.swiListeners = []
        self.infListeners = []

    def refreshListeners(self):
        '''Call all refresh listeners.'''
        for listener in self.refListeners:
            listener()

    def switchedShotListeners(self):
        '''Call all shot listeners.'''
        for listener in self.swiListeners:
            listener()

    def infoListeners(self, taskId):
        '''Call all info listeners with *taskId*.'''
        for listener in self.infListeners:
            listener(taskId)

    def addRefreshListener(self, listener):
        '''Add refresh *listener*.'''
        self.refListeners.append(listener)

    def addSwitchedShotListener(self, listener):
        '''Add switch shot *listener*.'''
        self.swiListeners.append(listener)

    def addInfoListener(self, listener):
        '''Add info *listener*.'''
        self.infListeners.append(listener)

    def emitPublishProgress(self, publishInt):
        '''Emit publish progress with *publishInt*.'''
        self.publishProgressSignal.emit(publishInt)

    def setTotalExportSteps(self, steps):
        '''Set total export *steps*.'''
        self.exportSteps = float(steps)
        self.stepsDone = float(0)

    def emitPublishProgressStep(self):
        '''Emit publish progress step.'''
        self.stepsDone += 1.0
        progress = (self.stepsDone / self.exportSteps) * 100.0
        self.publishProgressSignal.emit(int(progress))

# Variable to hold the global singleton.
_panelCom = None


class PanelComInstance(object):
    '''Global singleton.'''

    def __init__(self):
        '''Initialise global singleton.'''
        super(PanelComInstance, self).__init__()

    @staticmethod
    def instance():
        '''Return singleton instance.'''
        global _panelCom
        if not _panelCom:
            _panelCom = PanelCommunicator()
        return _panelCom
