# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

# Class for handling communication between panels
from PySide import QtCore


class PanelCommunicator(QtCore.QObject):
    publishProgressSignal = QtCore.Signal(int, name='publishProgressSignal')

    def __init__(self):
        super(PanelCommunicator, self).__init__()
        self.refListeners = []
        self.swiListeners = []
        self.infListeners = []

    def refreshListeners(self):
        for listener in self.refListeners:
            listener()

    def switchedShotListeners(self):
        for listener in self.swiListeners:
            listener()

    def infoListeners(self, taskId):
        for listener in self.infListeners:
            listener(taskId)

    def addRefreshListener(self, listener):
        self.refListeners.append(listener)

    def addSwitchedShotListener(self, listener):
        self.swiListeners.append(listener)

    def addInfoListener(self, listener):
        self.infListeners.append(listener)

    def emitPublishProgress(self, publishInt):
        self.publishProgressSignal.emit(publishInt)

    def setTotalExportSteps(self, steps):
        self.exportSteps = float(steps)
        self.stepsDone = float(0)

    def emitPublishProgressStep(self):
        self.stepsDone += 1.0
        progress = (self.stepsDone / self.exportSteps) * 100.0
        self.publishProgressSignal.emit(int(progress))

_panelCom = None


class PanelComInstance(object):
    def __init__(self):
        super(PanelComInstance, self).__init__()

    @staticmethod
    def instance():
        global _panelCom
        if not _panelCom:
            _panelCom = PanelCommunicator()
        return _panelCom
