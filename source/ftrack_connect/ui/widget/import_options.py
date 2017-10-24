# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from QtExt import QtCore, QtWidgets, QtGui

from stacked_options import StackedOptionsWidget
from ftrack_connect.connector import FTAssetHandlerInstance


class Ui_ImportOptions(object):
    '''Import options UI.'''

    def setupUi(self, ImportOptions):
        '''Setup UI for *ImportOptions*.'''
        ImportOptions.setObjectName("ImportOptions")
        ImportOptions.resize(451, 16)
        self.verticalLayout = QtWidgets.QVBoxLayout(ImportOptions)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.optionsPlaceHolderLayout = QtWidgets.QHBoxLayout()
        self.optionsPlaceHolderLayout.setSizeConstraint(
            QtWidgets.QLayout.SetMinimumSize
        )
        self.optionsPlaceHolderLayout.setObjectName("optionsPlaceHolderLayout")
        self.verticalLayout.addLayout(self.optionsPlaceHolderLayout)

        self.retranslateUi(ImportOptions)
        QtCore.QMetaObject.connectSlotsByName(ImportOptions)

    def retranslateUi(self, ImportOptions):
        '''Translate text for *ImportOptions*.'''
        translate = QtWidgets.QApplication.translate(
            'ImportOptions', 'Form', None,
            QtWidgets.QApplication.UnicodeUTF8
        )

        ImportOptions.setWindowTitle(translate)


class ImportOptionsWidget(QtWidgets.QWidget):
    '''Import options widget.'''

    def __init__(self, parent, task=None, connector=None):
        '''Instansiate widget with *connector*.'''
        if not connector:
            raise ValueError(
                'Please provide a connector object for %s'.format(
                    self.__class__.__name__
                )
            )

        super(ImportOptionsWidget, self).__init__(parent)
        self.ui = Ui_ImportOptions()
        self.ui.setupUi(self)

        self.stackedOptionsWidget = StackedOptionsWidget(
            self, connector=connector
        )

        xml = """<?xml version="1.0" encoding="UTF-8" ?>
            <options>
                <assettype name="default">
                    <tab name="Options">
                        <row name="Import mode" accepts="maya">
                            <option type="radio" name="importMode">
                                <optionitem name="Reference" value="True"/>
                                <optionitem name="Import"/>
                            </option>
                        </row>
                        <row name="Preserve References" accepts="maya">
                            <option type="checkbox" name="mayaReference" value="True"/>
                        </row>
                        <row name="Add Asset Namespace" accepts="maya">
                            <option type="checkbox" name="mayaNamespace" value="False"/>
                        </row>
                    </tab>
                </assettype>
                {0}
            </options>
        """

        xmlExtraAssetTypes = ""
        assetHandler = FTAssetHandlerInstance.instance()
        assetTypesStr = sorted(assetHandler.getAssetTypes())
        for assetTypeStr in assetTypesStr:
            assetClass = assetHandler.getAssetClass(assetTypeStr)
            if hasattr(assetClass, 'importOptions'):
                xmlExtraAssetTypes += '<assettype name="' + assetTypeStr + '">'
                xmlExtraAssetTypes += assetClass.importOptions()
                xmlExtraAssetTypes += '</assettype>'

        xml = xml.format(xmlExtraAssetTypes)

        self.stackedOptionsWidget.initStackedOptions(xml)
        self.ui.optionsPlaceHolderLayout.addWidget(self.stackedOptionsWidget)

    @QtCore.Slot(str)
    def setStackedWidget(self, stackName):
        '''Set stacked widget page to *stackName*.'''
        self.stackedOptionsWidget.setCurrentPage(stackName)

    def getOptions(self):
        '''Return options.'''
        return self.stackedOptionsWidget.getOptions()
