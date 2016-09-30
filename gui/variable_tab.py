import os

from PyQt4 import uic, QtGui, QtCore

from .util import fill_placeholder

class VariableTab(QtGui.QTableWidget):
    initialParamsChanged = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalHeader().hide()
        self.horizontalScrollBar().hide()

        self.all_variables = {}

    def define_variables(self, var_list):
        self.clear()
        self.setRowCount(len(var_list))
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(['Parameter','Initial Value','Fitted Value'])
        for i,var_name in enumerate(var_list):
            label = QtGui.QLabel(var_name, self)
            self.setCellWidget(i,0,label)

            spinner = QtGui.QDoubleSpinBox(self)
            spinner.setMinimum(-1e99)
            spinner.setMaximum(1e99)
            spinner.valueChanged.connect(self.on_value_change)
            self.setCellWidget(i,1,spinner)

            fitted = QtGui.QLabel('',self)
            self.setCellWidget(i,2,fitted)

    def initial_values(self):
        output = {}
        for i in range(self.rowCount()):
            par_name = self.cellWidget(i,0).text()
            par_value = self.cellWidget(i,1).value()
            output[par_name] = par_value
        return output

    def fitted_values(self, values):
        for i in range(self.rowCount()):
            par_name = self.cellWidget(i,0).text()
            value_cell = self.cellWidget(i,2)
            try:
                value_cell.setText(str(values[par_name]))
            except KeyError:
                value_cell.setText('')
    fitted_values = property(fset=fitted_values)


    def _get_entry(self, var_name):
        try:
            return self.var_entries[var_name]
        except KeyError:
            self.var_entries[var_name] = VariableEntry(symbol=var_name)
            return self.var_entries[var_name]

    def resizeEvent(self, event):
        for i in range(self.columnCount()):
            self.setColumnWidth(i, self.width()/self.columnCount())
        super().resizeEvent(event)

    def on_value_change(self, *args):
        self.initialParamsChanged.emit(self.initial_values())



class VariableEntry:
    def __init__(self, symbol):
        self.symbol = symbol
        self.initial = 0
        self.lower_bound = None
        self.upper_bound = None
        self.fitted_val = None
