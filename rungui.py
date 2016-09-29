#!/usr/bin/env python3

import sys

from PyQt4 import QtGui, QtCore

from gui import MainWindow

if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
