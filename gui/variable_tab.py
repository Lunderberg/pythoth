import os

from PyQt4 import uic, QtGui, QtCore

from .util import fill_placeholder, clear_layout
from .latex_label import LatexLabel

class VariableTab(QtGui.QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_variables = {}

    def define_variables(self, var_list):
        self.clear()
        for var_name in var_list:
            item = QtGui.QListWidgetItem(var_name)
            self.addItem(item)

    def _get_entry(self, var_name):
        try:
            return self.var_entries[var_name]
        except KeyError:
            self.var_entries[var_name] = VariableEntry(symbol=var_name)
            return self.var_entries[var_name]


class VariableEntry:
    def __init__(self, symbol):
        self.symbol = symbol
        self.initial = 0
        self.lower_bound = None
        self.upper_bound = None
        self.fitted_val = None
