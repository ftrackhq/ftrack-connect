from PySide import QtGui
from PySide import QtXml
from ftrack_connect_nuke import ftrackConnector


class StackedOptionsWidget(QtGui.QStackedWidget):
    def __init__(self, parent, task=None, connector=None):
        super(StackedOptionsWidget, self).__init__(parent)
        if not connector:
            raise ValueError('Please provide a connector object for %s' % self.__class__.__name__)
        
        self.xmlstring = None
        self.connector = connector

        if self.connector.getConnectorName() == 'nuke':
            p = self.palette()
            currentColor = p.color(QtGui.QPalette.Window)
            p.setBrush(QtGui.QPalette.Window, QtGui.QBrush(currentColor.lighter(175)))
            self.setPalette(p)
            
    def resetOptions(self, xmlstring):
        widgetCount = self.count()
        for i in reversed(range(widgetCount)):
            widget = self.widget(i)
            self.removeWidget(widget)
            del widget
            
        self.initStackedOptions(xmlstring)
       
    def initStackedOptions(self, xmlstring, fromFile=False):
        self.stackedIndex = dict()
        self.stackedOptions = dict()
        doc = QtXml.QDomDocument("optionsDocument")
        if fromFile:
            pass
        else:
            doc.setContent(xmlstring)
        assetTypeElements = doc.elementsByTagName('assettype')

        assetTypePages = dict()
        connectorName = self.connector.getConnectorName()
        maxRowCount = 0
        for i in range(assetTypeElements.length()):
            assetTypePages[i] = QtGui.QWidget()
            assetTypePages[i].setObjectName('page' + str(i))
            assetTypeElement = assetTypeElements.item(i).toElement()

            mainLayout = QtGui.QVBoxLayout()
            mainLayout.setContentsMargins(0, 0, 0, 0)
            mainLayout.setSpacing(0)
            assetTypePages[i].setLayout(mainLayout)

            assetTypeName = assetTypeElement.attribute('name')
            self.stackedIndex[assetTypeName] = i
            self.stackedOptions[assetTypeName] = []

            tabElements = assetTypeElement.elementsByTagName('tab')
            if tabElements.length() > 0:
                tabWidget = QtGui.QTabWidget()
                mainLayout.addWidget(tabWidget)

                for j in range(tabElements.length()):
                    tab = QtGui.QWidget()
                    tabLayout = QtGui.QVBoxLayout()
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
                            rowLayout, optionsCount = self.parseRow(rowElement, connectorName, mainLayout, assetTypeName)
                            if rowLayout:
                                rowCount += optionsCount
                                tabLayout.addLayout(rowLayout)
                        maxRowCount = max(rowCount, maxRowCount)
                        tabWidget.addTab(tab, tabName)

                    spacerItem3 = QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
                    tabLayout.addItem(spacerItem3)

            self.addWidget(assetTypePages[i])

    def getOptions(self):
        currentOptions = dict()
        for child in self.currentWidget().findChildren(QtGui.QDoubleSpinBox):
            currentOptions[child.objectName()] = float(child.value())
        for child in self.currentWidget().findChildren(QtGui.QCheckBox):
            currentOptions[child.objectName()] = bool(child.checkState())
        for child in self.currentWidget().findChildren(QtGui.QLineEdit):
            currentOptions[child.objectName()] = child.text()
        for child in self.currentWidget().findChildren(QtGui.QComboBox):
            currentOptions[child.objectName()] = child.currentText()
        for child in self.currentWidget().findChildren(QtGui.QRadioButton):
            if child.isChecked():
                currentOptions[child.objectName()] = child.text()

        return currentOptions

    def parseRow(self, rowElement, connectorName, mainLayout, assetTypeName):
        accepts = rowElement.attribute('accepts')
        acceptsSplit = accepts.split(',')
        if accepts == '' or connectorName in acceptsSplit:
            rowLayout = QtGui.QHBoxLayout()
            rowName = rowElement.attribute('name')
            rowEnabled = rowElement.attribute('enabled')

            optionLabel = QtGui.QLabel(rowName)
            optionLabel.setFixedWidth(160)
            rowLayout.addWidget(optionLabel)

            if rowEnabled == 'False':
                enabled = False
                optionLabel.setEnabled(False)
            else:
                enabled = True

            optionElements = rowElement.elementsByTagName('option')
            optionsCount = self.parseOptions(rowLayout, optionElements, assetTypeName, enabled)

            return rowLayout, optionsCount
        else:
            return None, 0

    def parseOptions(self, rowLayout, optionElements, assetTypeName, enabled):
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
            
            # Float setting by Phil @ NHB 
            if optionType == 'float':
                floatBox = QtGui.QDoubleSpinBox()
                floatBox.setEnabled(enabled)
                floatBox.setObjectName(optionName)
                floatBox.setSingleStep(0.1)
                floatBox.setValue(float(optionValue))
                rowLayout.addWidget(floatBox)
                optionsCount = 1

            if optionType == 'checkbox':
                checkBox = QtGui.QCheckBox()
                checkBox.setEnabled(enabled)
                checkBox.setChecked(bool(optionValue))
                checkBox.setObjectName(optionName)
                rowLayout.addWidget(checkBox)
                optionsCount = 1

            if optionType == 'string':
                textBox = QtGui.QLineEdit()
                textBox.setEnabled(enabled)
                textBox.setText(optionValue)
                textBox.setObjectName(optionName)
                rowLayout.addWidget(textBox)
                optionsCount = 1

            if optionType == 'combo':
                comboBox = QtGui.QComboBox()
                comboBox.setEnabled(enabled)
                optionitemElements = optionElement.elementsByTagName('optionitem')
                for t in range(optionitemElements.length()):
                    optionitemElement = optionitemElements.item(t).toElement()
                    optionitemValue = optionitemElement.attribute('name')
                    comboBox.addItem(optionitemValue)

                comboBox.setObjectName(optionName)
                rowLayout.addWidget(comboBox)
                optionsCount = optionitemElements.length()

            if optionType == 'radio':
                radioWidget = QtGui.QWidget()
                radioLayout = QtGui.QVBoxLayout()
                radioLayout.setSpacing(1)
                radioWidget.setLayout(radioLayout)
                optionitemElements = optionElement.elementsByTagName('optionitem')
                for t in range(optionitemElements.length()):
                    optionitemElement = optionitemElements.item(t).toElement()
                    optionitemValue = optionitemElement.attribute('value')
                    optionitemName = optionitemElement.attribute('name')
                    radioButton = QtGui.QRadioButton(optionitemName)
                    if bool(optionitemValue):
                        radioButton.setChecked(True)
                    radioLayout.addWidget(radioButton)
                    radioButton.setEnabled(enabled)

                    radioButton.setObjectName(optionName)
                rowLayout.addWidget(radioWidget)
                optionsCount = optionitemElements.length()
        return optionsCount

    def setCurrentPage(self, pageName):
        if pageName in self.stackedIndex:
            newIndex = self.stackedIndex[pageName]
        else:
            newIndex = self.stackedIndex['default']
            pageName = 'default'

        if newIndex == self.currentIndex():
            self.setCurrentIndex(0)

        self.setCurrentIndex(newIndex)
        self.currentStack = pageName
