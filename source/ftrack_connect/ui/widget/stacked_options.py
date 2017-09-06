# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack
import sys

from QtExt import QtWidgets, QtXml, QtGui


class StackedOptionsWidget(QtWidgets.QStackedWidget):
    '''Stacked options widget.'''

    def __init__(self, parent, task=None, connector=None):
        '''Instansiate stacked options widget with *connector*.'''
        super(StackedOptionsWidget, self).__init__(parent)
        if not connector:
            raise ValueError(
                'Please provide a connector object for {0}'.format(
                    self.__class__.__name__
                )
            )

        self.xmlstring = None
        self.connector = connector

        if self.connector.getConnectorName() == 'nuke':
            p = self.palette()
            currentColor = p.color(QtGui.QPalette.Window)
            p.setBrush(
                QtGui.QPalette.Window, QtGui.QBrush(currentColor.lighter(175))
            )
            self.setPalette(p)

    def resetOptions(self, xmlstring):
        '''Reset options to *xmlstring*.'''
        widgetCount = self.count()
        for i in reversed(range(widgetCount)):
            widget = self.widget(i)
            self.removeWidget(widget)
            del widget

        self.initStackedOptions(xmlstring)

    def initStackedOptions(self, xmlstring, fromFile=False):
        '''Initiate stacked options widget with *xmlstring*.'''
        self.stackedIndex = dict()
        self.stackedOptions = dict()
        doc = QtXml.QDomDocument('optionsDocument')
        if fromFile:
            pass
        else:
            doc.setContent(xmlstring)
        assetTypeElements = doc.elementsByTagName('assettype')

        assetTypePages = dict()
        connectorName = self.connector.getConnectorName()
        maxRowCount = 0
        for i in range(assetTypeElements.length()):
            assetTypePages[i] = QtWidgets.QWidget()
            assetTypePages[i].setObjectName('page' + str(i))
            assetTypeElement = assetTypeElements.item(i).toElement()

            mainLayout = QtWidgets.QVBoxLayout()
            mainLayout.setContentsMargins(0, 0, 0, 0)
            mainLayout.setSpacing(0)
            assetTypePages[i].setLayout(mainLayout)

            assetTypeName = assetTypeElement.attribute('name')
            self.stackedIndex[assetTypeName] = i
            self.stackedOptions[assetTypeName] = []

            tabElements = assetTypeElement.elementsByTagName('tab')
            if tabElements.length() > 0:
                tabWidget = QtWidgets.QTabWidget()
                mainLayout.addWidget(tabWidget)

                for j in range(tabElements.length()):
                    tab = QtWidgets.QWidget()
                    tabLayout = QtWidgets.QVBoxLayout()
                    tabLayout.setSpacing(2)
                    tab.setLayout(tabLayout)
                    tabElement = tabElements.item(j).toElement()
                    tabName = tabElement.attribute('name')
                    tabEnabled = tabElement.attribute('enabled')

                    if tabEnabled == 'False':
                        tab.setEnabled(False)

                    accepts = tabElement.attribute('accepts')
                    acceptsSplit = accepts.split(',')
                    if accepts == '' or connectorName in acceptsSplit:
                        rowElements = tabElement.elementsByTagName('row')
                        rowCount = 0
                        for k in range(rowElements.length()):
                            rowElement = rowElements.item(k).toElement()
                            rowLayout, optionsCount = self.parseRow(
                                rowElement, connectorName, mainLayout,
                                assetTypeName
                            )
                            if rowLayout:
                                rowCount += optionsCount
                                tabLayout.addLayout(rowLayout)
                        maxRowCount = max(rowCount, maxRowCount)
                        tabWidget.addTab(tab, tabName)

                    spacerItem3 = QtWidgets.QSpacerItem(
                        1, 1, QtWidgets.QSizePolicy.Minimum,
                        QtWidgets.QSizePolicy.Expanding
                    )
                    tabLayout.addItem(spacerItem3)

            self.addWidget(assetTypePages[i])

    def getOptions(self):
        '''Return options.'''
        currentOptions = dict()
        for child in self.currentWidget().findChildren(QtWidgets.QDoubleSpinBox):
            currentOptions[child.objectName()] = float(child.value())
        for child in self.currentWidget().findChildren(QtWidgets.QCheckBox):
            currentOptions[child.objectName()] = bool(child.checkState())
        for child in self.currentWidget().findChildren(QtWidgets.QLineEdit):
            currentOptions[child.objectName()] = child.text()
        for child in self.currentWidget().findChildren(QtWidgets.QComboBox):
            currentOptions[child.objectName()] = child.currentText()
        for child in self.currentWidget().findChildren(QtWidgets.QRadioButton):
            if child.isChecked():
                currentOptions[child.objectName()] = child.text()

        return currentOptions

    def parseRow(self, rowElement, connectorName, mainLayout, assetTypeName):
        '''Parse xml *rowElement*.'''
        accepts = rowElement.attribute('accepts')
        acceptsSplit = accepts.split(',')
        if accepts == '' or connectorName in acceptsSplit:
            rowLayout = QtWidgets.QHBoxLayout()
            rowName = rowElement.attribute('name')
            rowEnabled = rowElement.attribute('enabled')

            optionLabel = QtWidgets.QLabel(rowName)
            optionLabel.setFixedWidth(160)
            rowLayout.addWidget(optionLabel)

            if rowEnabled == 'False':
                enabled = False
                optionLabel.setEnabled(False)
            else:
                enabled = True

            optionElements = rowElement.elementsByTagName('option')
            optionsCount = self.parseOptions(
                rowLayout, optionElements, assetTypeName, enabled
            )

            return rowLayout, optionsCount
        else:
            return None, 0

    def parseOptions(self, rowLayout, optionElements, assetTypeName, enabled):
        '''Parse options.'''
        optionsCount = 0
        for k in range(optionElements.length()):
            optionElement = optionElements.item(k).toElement()
            optionType = optionElement.attribute('type')
            optionValue = optionElement.attribute('value')
            if optionValue == 'True':
                optionValue = True
            elif optionValue == 'False':
                optionValue = False
            optionName = optionElement.attribute('name')
            self.stackedOptions[assetTypeName].append(optionName)

            if optionType == 'float':
                floatBox = QtWidgets.QDoubleSpinBox()
                floatBox.setEnabled(enabled)
                floatBox.setObjectName(optionName)
                floatBox.setSingleStep(0.1)
                floatBox.setMaximum(sys.maxint)
                floatBox.setMinimum(-sys.maxint)
                floatBox.setValue(float(optionValue))
                rowLayout.addWidget(floatBox)
                optionsCount = 1

            if optionType == 'checkbox':
                checkBox = QtWidgets.QCheckBox()
                checkBox.setEnabled(enabled)
                checkBox.setChecked(bool(optionValue))
                checkBox.setObjectName(optionName)
                rowLayout.addWidget(checkBox)
                optionsCount = 1

            if optionType == 'string':
                textBox = QtWidgets.QLineEdit()
                textBox.setEnabled(enabled)
                textBox.setText(optionValue)
                textBox.setObjectName(optionName)
                rowLayout.addWidget(textBox)
                optionsCount = 1

            if optionType == 'combo':
                comboBox = QtWidgets.QComboBox()
                comboBox.setEnabled(enabled)
                optionitemElements = optionElement.elementsByTagName(
                    'optionitem')
                for t in range(optionitemElements.length()):
                    optionitemElement = optionitemElements.item(t).toElement()
                    optionitemValue = optionitemElement.attribute('name')
                    comboBox.addItem(optionitemValue)

                comboBox.setObjectName(optionName)
                rowLayout.addWidget(comboBox)
                optionsCount = optionitemElements.length()

            if optionType == 'radio':
                radioWidget = QtWidgets.QWidget()
                radioLayout = QtWidgets.QVBoxLayout()
                radioLayout.setSpacing(1)
                radioWidget.setLayout(radioLayout)
                optionitemElements = optionElement.elementsByTagName(
                    'optionitem'
                )
                for t in range(optionitemElements.length()):
                    optionitemElement = optionitemElements.item(t).toElement()
                    optionitemValue = optionitemElement.attribute('value')
                    optionitemName = optionitemElement.attribute('name')
                    radioButton = QtWidgets.QRadioButton(optionitemName)
                    if bool(optionitemValue):
                        radioButton.setChecked(True)
                    radioLayout.addWidget(radioButton)
                    radioButton.setEnabled(enabled)

                    radioButton.setObjectName(optionName)
                rowLayout.addWidget(radioWidget)
                optionsCount = optionitemElements.length()
        return optionsCount

    def setCurrentPage(self, pageName):
        '''Set current page to *pageName*.'''
        if pageName in self.stackedIndex:
            newIndex = self.stackedIndex[pageName]
        else:
            newIndex = self.stackedIndex['default']
            pageName = 'default'

        if newIndex == self.currentIndex():
            self.setCurrentIndex(0)

        self.setCurrentIndex(newIndex)
        self.currentStack = pageName
