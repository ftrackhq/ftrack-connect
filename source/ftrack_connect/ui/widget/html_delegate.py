# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from PySide import QtGui, QtCore


class HtmlDelegate(QtGui.QStyledItemDelegate):
    '''Delegate to render Html.'''

    def __init__(self, formatter, *args, **kwargs):
        '''Initialise delegate with html *formatter*.'''
        self.format = formatter

        super(HtmlDelegate, self).__init__(*args, **kwargs)

    def paint(self, painter, option, index):
        '''Override paint method.'''
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)

        if options.widget is None:
            style = QtGui.QApplication.style()
        else:
            style = options.widget.style()

        doc = QtGui.QTextDocument()

        data = index.data(role=QtCore.Qt.UserRole)
        doc.setHtml(self.format(data))

        doc.adjustSize()

        options.text = ''
        style.drawControl(QtGui.QStyle.CE_ItemViewItem, options, painter)

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

        if options.state & QtGui.QStyle.State_Selected:
            ctx.palette.setColor(
                QtGui.QPalette.Text,
                options.palette.color(
                    QtGui.QPalette.Active, QtGui.QPalette.HighlightedText
                )
            )

        text_rectangle = style.subElementRect(
            QtGui.QStyle.SE_ItemViewItemText, options
        )

        # Fix offset issue occurring on windows.
        text_rectangle.adjust(+5, 0, -5, 0)

        painter.save()
        painter.translate(text_rectangle.topLeft())
        painter.setClipRect(
            text_rectangle.translated(-text_rectangle.topLeft())
        )
        doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        '''Returns the size needed to display the item.'''
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)

        doc = QtGui.QTextDocument()

        data = index.data(role=QtCore.Qt.UserRole)
        doc.setHtml(self.format(data))

        doc.adjustSize()

        return QtCore.QSize(doc.idealWidth(), doc.size().height())
