#!/usr/bin/python3

# Template for creating PyQt applications

import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc


class MainWindow(qtw.QWidget):

    def __init__(self):
        
        super().__init__()

        # Main UI definitions

        self.subwidget = qtw.QWidget(
                                self, 
                                toolTip='This is my widget.',
                                cursor=qtc.Qt.ArrowCursor)

        self.label = qtw.QLabel('Hello from QLabel', self)
        self.label.margin = 10
        self.label.indent = 2
        self.label.wordWrap = True

        self.line_edit = qtw.QLineEdit('default value', self)
        self.line_edit.readOnly = False
        self.line_edit.placeholderText = 'type sth.'
        

        self.button = qtw.QPushButton(
                "Push Me",
                self,
                checkable=True,
                checked=True,
                shortcut=qtg.QKeySequence('Ctrl+p'))

        self.combobox = qtw.QComboBox(
                self,
                editable=True,
                insertPolicy=qtw.QComboBox.InsertAtTop)
        self.combobox.addItem('AA', 1)
        self.combobox.addItem('BB', 2)
        self.combobox.insertItem(2, 'CC', 3)

        self.spinbox = qtw.QSpinBox(
                self,
                value=12,
                maximum=100,
                minimum=10,
                prefix='$',
                suffix=' + Tax',
                singleStep=5)

        self.datetimebox = qtw.QDateTimeEdit(
                self,
                date=qtc.QDate.currentDate(),
                time=qtc.QTime(12, 30),
                calendarPopup=True,
                maximumDate=qtc.QDate(2030, 1, 1),
                minimumTime=qtc.QTime(17, 0),
                displayFormat='yyyy-MM-dd HH:mm')

        self.textedit = qtw.QTextEdit(
                self,
                acceptRichText=False,
                lineWrapMode=qtw.QTextEdit.FixedColumnWidth,
                lineWrapColumnOrWidth=25,
                placeholderText='Enter your shit here')


        # End Main UI Definitions

        self.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
