from ftrack_connect.qt import QtCore, QtWidgets, QtGui


class WidgetList(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(WidgetList, self).__init__(parent=parent)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.tablewidget = QtWidgets.QListWidget()
        self.tablewidget.itemChanged.connect(self._set_state)
        layout.addWidget(self.tablewidget)

    def add_plugins(self, plugins):
        for plugin_name, plugin_object in plugins.items():
            new_item = QtWidgets.QListWidgetItem(plugin_name)
            new_item.setData(QtCore.Qt.UserRole, plugin_object)
            new_item.setFlags(new_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            new_item.setCheckState(QtCore.Qt.Checked)
            self.tablewidget.addItem(new_item)

    def _set_state(self, item):
        connect_widget = item.data(QtCore.Qt.UserRole)
        # hide / show tab containing the plugin.
        connect_widget.parent().parent().setVisible(item.checkState())
