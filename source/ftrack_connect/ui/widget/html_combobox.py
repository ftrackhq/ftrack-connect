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

            # Draw custom item.
            doc = QtGui.QTextDocument()
            doc.setHtml(self.format(itemData))

            style = painter.style()  # QtGui.QApplication.style()
            ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

            rect = style.subElementRect(
                QtGui.QStyle.SE_ComboBoxFocusRect, option, self
            )
            doc.setTextWidth(option.rect.width())
            painter.save()
            painter.translate(rect.topLeft())
            painter.setClipRect(rect.translated(-rect.topLeft()))
            doc.documentLayout().draw(painter, ctx)
            painter.restore()

        else:
            super(HtmlComboBox, self).paint(event)

    def sizeHint(self):
        '''Returns the size needed to display the item.'''
        option = QtGui.QStyleOptionComboBox()
        self.initStyleOption(option)

        doc = QtGui.QTextDocument()

        itemData = self.itemData(self.currentIndex())
        doc.setHtml(self.format(itemData))
        doc.setTextWidth(option.rect.width())
        size = QtCore.QSize(
            doc.idealWidth(), doc.size().height() + 5
        )

        return size
