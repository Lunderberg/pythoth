import os

from PyQt4 import uic, QtGui, QtCore

from .util import fill_placeholder

class ParameterTab(QtGui.QTableWidget):
    def __init__(self, parameters, parent=None):
        super().__init__(parent)
        self.verticalHeader().hide()
        self.horizontalScrollBar().hide()

        self.parameters = parameters
        self.parameters.param_changed.connect(self.from_parameter_change)
        self.parameters.param_list_changed.connect(self.from_parameter_list_change)

        self.index_lookup = {}

    def from_parameter_list_change(self, parameters):
        self.clear()
        self.index_lookup = {}

        self.setRowCount(len(parameters))
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(['Parameter','Initial Value','Fitted Value'])
        for i,par in enumerate(parameters):
            label = QtGui.QLabel(par.name, self)
            self.setCellWidget(i,0,label)

            spinner = QtGui.QDoubleSpinBox(self)
            spinner.setMinimum(-1e99)
            spinner.setMaximum(1e99)
            spinner.editingFinished.connect(
                lambda par=par,spinner=spinner :
                self.on_initial_value_change(par,spinner)
            )
            self.setCellWidget(i,1,spinner)

            fitted = QtGui.QLabel('',self)
            self.setCellWidget(i,2,fitted)

            self.index_lookup[par.name] = i

            self.from_parameter_change(par)

    def from_parameter_change(self, par):
        i = self.index_lookup[par.name]
        self.cellWidget(i,0).setText(par.name)
        self.cellWidget(i,1).setValue(par.initial_value)
        self.cellWidget(i,2).setText(str(par.fitted_value))

    def resizeEvent(self, event):
        for i in range(self.columnCount()):
            self.setColumnWidth(i, self.width()/self.columnCount())
        super().resizeEvent(event)

    def on_initial_value_change(self, par, spinner):
        par.initial_value = spinner.value()
