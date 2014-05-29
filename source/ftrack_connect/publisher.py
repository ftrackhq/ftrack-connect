# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'prototype.ui'
#
# Created: Wed May 28 23:11:37 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

import prototype_rc


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(656, 893)
        Dialog.setStyleSheet("* {\n"
"    font: 10pt \"Roboto Light\";\n"
"}\n"
"\n"
"QDialog {\n"
"    background-color: white;\n"
"}\n"
"\n"
"QTabBar\n"
"{\n"
"    qproperty-drawBase: 0;\n"
"\n"
"}\n"
"\n"
"QTabWidget::tab-bar {\n"
"    alignment: center;\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"    color: #999;\n"
"    border: none;\n"
"    background-color: transparent;\n"
"     padding: 10px;\n"
"    padding-bottom: 20px;\n"
"    margin-top: 40px;\n"
"    font-size: 12pt;\n"
"    width: 100px;\n"
"}\n"
"\n"
"QTabBar::tab:selected {\n"
"    color: #000;\n"
"}\n"
"\n"
"QTabWidget::pane {\n"
"    border-top: 2px solid #dadada;\n"
"    border-bottom: 2px solid #dadada;\n"
"    background-color: #eeeeee;\n"
"}\n"
"\n"
"QLineEdit {\n"
"    color: #999;\n"
"    padding: 5px;\n"
"    padding-left: 10px;    \n"
"    border: 1px solid #CECECE;\n"
"    border-radius: 2px;\n"
"}\n"
"\n"
"\n"
"QComboBox {\n"
"    color: #999;\n"
"    selection-background-color: #78879b;\n"
"    background-color: #fff;\n"
"    border: 1px solid #CECECE;\n"
"    border-radius: 2px;\n"
"    padding: 5px;\n"
"    padding-left: 10px;    \n"
"}\n"
"\n"
"QComboBox::drop-down\n"
"{\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 15px;\n"
"    margin-right: 15px;\n"
"    border-width: 0px;\n"
"}\n"
"\n"
"QComboBox::down-arrow\n"
"{\n"
"    image: url(:/prototype/arrowDown);\n"
"    width: 10px;\n"
"}\n"
"\n"
"QPushButton {\n"
"    background-color: #6690FF;\n"
"    color: white;\n"
"    border-radius: 2px;\n"
"    padding: 5px;\n"
"    padding-right: 15px;\n"
"    padding-left: 15px;\n"
"    border: 1px solid #597EDF;\n"
"}\n"
"\n"
"#dropZone {\n"
"    border: 2px dashed #ccc;\n"
"}\n"
"\n"
"#dropZone QLabel  {\n"
"    color: #999;\n"
"    font-size: 12pt;\n"
"    font-weight: 100;\n"
"}\n"
"\n"
"#options {\n"
"    background-color: #fafafa;\n"
"    padding: 15px;\n"
"    margin-top: 16px;\n"
"}\n"
"\n"
"#serverName {\n"
"    color: #9a9a9a;\n"
"}\n"
"\n"
"#serverStatus {\n"
"    background-color: #6aac00;\n"
"    color: white;\n"
"    border-radius: 2px;\n"
"    padding: 3px;\n"
"    min-width: 100px;\n"
"    qproperty-alignment: AlignCenter;\n"
"}\n"
"\n"
"#upArrowMarker {\n"
"}\n"
"")
        self.verticalLayout_2 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidget = QtGui.QTabWidget(Dialog)
        self.tabWidget.setIconSize(QtCore.QSize(0, 0))
        self.tabWidget.setUsesScrollButtons(False)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setContentsMargins(15, 15, 15, 15)
        self.verticalLayout.setObjectName("verticalLayout")
        self.dropZone = QtGui.QFrame(self.tab_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dropZone.sizePolicy().hasHeightForWidth())
        self.dropZone.setSizePolicy(sizePolicy)
        self.dropZone.setMinimumSize(QtCore.QSize(0, 150))
        self.dropZone.setFrameShape(QtGui.QFrame.StyledPanel)
        self.dropZone.setFrameShadow(QtGui.QFrame.Raised)
        self.dropZone.setObjectName("dropZone")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.dropZone)
        self.verticalLayout_4.setSpacing(10)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtGui.QLabel(self.dropZone)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_2 = QtGui.QPushButton(self.dropZone)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        self.pushButton_2.setFlat(False)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_3.addWidget(self.pushButton_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem1)
        self.verticalLayout.addWidget(self.dropZone)
        self.lineEdit = QtGui.QLineEdit(self.tab_2)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.lineEdit_2 = QtGui.QLineEdit(self.tab_2)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.verticalLayout.addWidget(self.lineEdit_2)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.upArrowMarker = QtGui.QLabel(self.tab_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.upArrowMarker.sizePolicy().hasHeightForWidth())
        self.upArrowMarker.setSizePolicy(sizePolicy)
        self.upArrowMarker.setMaximumSize(QtCore.QSize(40, 15))
        self.upArrowMarker.setText("")
        self.upArrowMarker.setPixmap(QtGui.QPixmap(":/prototype/upArrowMarker"))
        self.upArrowMarker.setScaledContents(True)
        self.upArrowMarker.setAlignment(QtCore.Qt.AlignCenter)
        self.upArrowMarker.setMargin(0)
        self.upArrowMarker.setIndent(-1)
        self.upArrowMarker.setObjectName("upArrowMarker")
        self.horizontalLayout_5.addWidget(self.upArrowMarker)

        # self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.options = QtGui.QFrame(self.tab_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.options.sizePolicy().hasHeightForWidth())
        self.options.setSizePolicy(sizePolicy)
        self.options.setFrameShape(QtGui.QFrame.StyledPanel)
        self.options.setFrameShadow(QtGui.QFrame.Raised)
        self.options.setObjectName("options")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.options)
        self.verticalLayout_3.setSpacing(7)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.typeLabel = QtGui.QLabel(self.options)
        self.typeLabel.setObjectName("typeLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.typeLabel)
        self.typeComboBox = QtGui.QComboBox(self.options)
        self.typeComboBox.setObjectName("typeComboBox")
        self.typeComboBox.addItem("")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.typeComboBox)
        self.linkToLabel = QtGui.QLabel(self.options)
        self.linkToLabel.setObjectName("linkToLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.linkToLabel)
        self.linkToLineEdit = QtGui.QLineEdit(self.options)
        self.linkToLineEdit.setObjectName("linkToLineEdit")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.linkToLineEdit)
        self.versionNameLabel = QtGui.QLabel(self.options)
        self.versionNameLabel.setObjectName("versionNameLabel")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.versionNameLabel)
        self.versionNameLineEdit = QtGui.QLineEdit(self.options)
        self.versionNameLineEdit.setObjectName("versionNameLineEdit")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.versionNameLineEdit)
        self.versionLabel = QtGui.QLabel(self.options)
        self.versionLabel.setObjectName("versionLabel")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.versionLabel)
        self.versionLineEdit = QtGui.QLineEdit(self.options)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.versionLineEdit.sizePolicy().hasHeightForWidth())
        self.versionLineEdit.setSizePolicy(sizePolicy)
        self.versionLineEdit.setMinimumSize(QtCore.QSize(50, 0))
        self.versionLineEdit.setMaximumSize(QtCore.QSize(50, 16777215))
        self.versionLineEdit.setObjectName("versionLineEdit")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.versionLineEdit)
        self.descriptionLabel = QtGui.QLabel(self.options)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.descriptionLabel)
        self.descriptionLineEdit = QtGui.QLineEdit(self.options)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.descriptionLineEdit.sizePolicy().hasHeightForWidth())
        self.descriptionLineEdit.setSizePolicy(sizePolicy)
        self.descriptionLineEdit.setMinimumSize(QtCore.QSize(0, 100))
        self.descriptionLineEdit.setObjectName("descriptionLineEdit")
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.descriptionLineEdit)
        self.locationLabel = QtGui.QLabel(self.options)
        self.locationLabel.setObjectName("locationLabel")
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.locationLabel)
        self.locationComboBox = QtGui.QComboBox(self.options)
        self.locationComboBox.setObjectName("locationComboBox")
        self.locationComboBox.addItem("")
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.locationComboBox)
        self.verticalLayout_3.addLayout(self.formLayout)
        self.verticalLayout.addWidget(self.options)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pushButton = QtGui.QPushButton(self.tab_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setFlat(False)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_4.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.tabWidget.addTab(self.tab_4, "")
        self.tab_5 = QtGui.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.tabWidget.addTab(self.tab_5, "")
        self.verticalLayout_2.addWidget(self.tabWidget)
        self.frame_3 = QtGui.QFrame(Dialog)
        self.frame_3.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame_3)
        self.horizontalLayout.setSpacing(7)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.serverName = QtGui.QLabel(self.frame_3)
        self.serverName.setObjectName("serverName")
        self.horizontalLayout.addWidget(self.serverName)
        self.serverStatus = QtGui.QLabel(self.frame_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.serverStatus.sizePolicy().hasHeightForWidth())
        self.serverStatus.setSizePolicy(sizePolicy)
        self.serverStatus.setObjectName("serverStatus")
        self.horizontalLayout.addWidget(self.serverStatus)
        self.verticalLayout_2.addWidget(self.frame_3)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Publisher", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("Dialog", "Tasks", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Drop files here", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("Dialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit.setText(QtGui.QApplication.translate("Dialog", "destruction-siteA-v004", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_2.setText(QtGui.QApplication.translate("Dialog", "destruction-siteA-v004-turntable", None, QtGui.QApplication.UnicodeUTF8))
        self.typeLabel.setText(QtGui.QApplication.translate("Dialog", "Type", None, QtGui.QApplication.UnicodeUTF8))
        self.typeComboBox.setItemText(0, QtGui.QApplication.translate("Dialog", "Geometry", None, QtGui.QApplication.UnicodeUTF8))
        self.linkToLabel.setText(QtGui.QApplication.translate("Dialog", "Link To", None, QtGui.QApplication.UnicodeUTF8))
        self.linkToLineEdit.setText(QtGui.QApplication.translate("Dialog", "Piggy / Environment / siteA", None, QtGui.QApplication.UnicodeUTF8))
        self.versionNameLabel.setText(QtGui.QApplication.translate("Dialog", "Version Name", None, QtGui.QApplication.UnicodeUTF8))
        self.versionNameLineEdit.setText(QtGui.QApplication.translate("Dialog", "destruction-siteA-v004", None, QtGui.QApplication.UnicodeUTF8))
        self.versionLabel.setText(QtGui.QApplication.translate("Dialog", "Version", None, QtGui.QApplication.UnicodeUTF8))
        self.versionLineEdit.setText(QtGui.QApplication.translate("Dialog", "1", None, QtGui.QApplication.UnicodeUTF8))
        self.descriptionLabel.setText(QtGui.QApplication.translate("Dialog", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.locationLabel.setText(QtGui.QApplication.translate("Dialog", "Location", None, QtGui.QApplication.UnicodeUTF8))
        self.locationComboBox.setItemText(0, QtGui.QApplication.translate("Dialog", "Reference only", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Dialog", "Publish", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("Dialog", "Publish", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("Dialog", "Review", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QtGui.QApplication.translate("Dialog", "Timesheet", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QtGui.QApplication.translate("Dialog", "Inbox", None, QtGui.QApplication.UnicodeUTF8))
        self.serverName.setText(QtGui.QApplication.translate("Dialog", "https://dev.ftrackapp.com", None, QtGui.QApplication.UnicodeUTF8))
        self.serverStatus.setText(QtGui.QApplication.translate("Dialog", "ONLINE", None, QtGui.QApplication.UnicodeUTF8))


class Publisher(QtGui.QDialog):

    def __init__(self, parent=None):
        super(Publisher, self).__init__(parent)
        self.ui =  Ui_Dialog()
        self.ui.setupUi(self)

    def resizeEvent(self, *args, **kwargs):
        super(Publisher, self).resizeEvent(*args, **kwargs)
        size = args[0].size()

        self.ui.upArrowMarker.move(
            (size.width() - self.ui.upArrowMarker.width()) / 2,
            288
        )