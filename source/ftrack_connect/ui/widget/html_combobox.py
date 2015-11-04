# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from PySide import QtGui, QtCore

import ftrack_connect.ui.widget.html_delegate


class HtmlComboBox(QtGui.QComboBox):
    '''Combo box that draws items with html.'''

    def __init__(self, formatter, *args, **kwargs):
        self.format = formatter
        super(HtmlComboBox, self).__init__(*args, **kwargs)
        self.setItemDelegate(
            ftrack_connect.ui.widget.html_delegate.HtmlDelegate(formatter)
        )

    def paintEvent(self, event):
        '''Handle paint *event*.'''
        itemData = self.itemData(self.currentIndex())

        if itemData:
            # Draw main control.
            painter = QtGui.QStylePainter(self)
            painter.setPen(self.palette().color(QtGui.QPalette.Text))

            option = QtGui.QStyleOptionComboBox()
            self.initStyleOption(option)
            painter.drawComplexControl(QtGui.QStyle.CC_ComboBox, option)

            # Get QTextDocument from delegate to use for painting HTML text.
            delegate = self.itemDelegate()
            document = delegate.getTextDocument(
                option, self.itemData(self.currentIndex())
            )

            style = painter.style()  # QtGui.QApplication.style()
            paint_context = QtGui.QAbstractTextDocumentLayout.PaintContext()

            text_rectangle = style.subElementRect(
                QtGui.QStyle.SE_ComboBoxFocusRect, option, self
            )

            painter.save()
            painter.translate(text_rectangle.topLeft())
            painter.setClipRect(text_rectangle.translated(
                -text_rectangle.topLeft())
            )
            document.documentLayout().draw(painter, paint_context)
            painter.restore()

        else:
            super(HtmlComboBox, self).paint(event)

    def sizeHint(self):
        '''Returns the size needed to display the item.'''
        option = QtGui.QStyleOptionComboBox()
        self.initStyleOption(option)

        data = self.itemData(self.currentIndex())

        # Get QTextDocument from delegate to use for calculating size hint.
        delegate = self.itemDelegate()
        document = delegate.getTextDocument(option, data)

        # Adjust the size to fix issue occurring on windows.
        size = QtCore.QSize(
            document.idealWidth(), document.size().height() + 5
        )

        return size
