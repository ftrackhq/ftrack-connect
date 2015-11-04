# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

from PySide import QtGui, QtCore


class HtmlDelegate(QtGui.QStyledItemDelegate):
    '''Delegate to render Html.'''

    def __init__(self, formatter, *args, **kwargs):
        '''Initialise delegate with html *formatter*.'''
        self.format = formatter

        super(HtmlDelegate, self).__init__(*args, **kwargs)

    def getTextDocument(self, option, item_data):
        '''Return QTextDocument based on *option* and *item_data*.'''
        document = QtGui.QTextDocument()
        document.setHtml(self.format(item_data))
        document.setTextWidth(option.rect.width())

        return document

    def paint(self, painter, option, index):
        '''Override paint method.'''
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)

        if options.widget is None:
            style = QtGui.QApplication.style()
        else:
            style = options.widget.style()

        # Get QTextDocument to use for painting HTML text.
        data = index.data(role=QtCore.Qt.UserRole)
        document = self.getTextDocument(option, data)

        options.text = ''

        # Draw the element with the provided painter with the style
        # options specified by option
        style.drawControl(QtGui.QStyle.CE_ItemViewItem, options, painter)

        paint_context = QtGui.QAbstractTextDocumentLayout.PaintContext()

        # If item state is selected by mouse over change the highlight color.
        if options.state & QtGui.QStyle.State_Selected:
            paint_context.palette.setColor(
                QtGui.QPalette.Text,
                options.palette.color(
                    QtGui.QPalette.Active, QtGui.QPalette.HighlightedText
                )
            )

        # Get paint rectangle in screen coordinates
        text_rectangle = style.subElementRect(
            QtGui.QStyle.SE_ItemViewItemText, options
        )

        # Adjust the rectangle to fix issue occurring on windows.
        text_rectangle.adjust(+5, 0, -5, 0)

        painter.save()
        painter.translate(text_rectangle.topLeft())
        painter.setClipRect(
            text_rectangle.translated(-text_rectangle.topLeft())
        )
        document.documentLayout().draw(painter, paint_context)
        painter.restore()

    def sizeHint(self, option, index):
        '''Returns the size needed to display the item.'''
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)

        data = index.data(role=QtCore.Qt.UserRole)
        document = self.getTextDocument(option, data)

        return QtCore.QSize(document.idealWidth(), document.size().height())