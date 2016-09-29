import os

from PyQt4 import uic, QtGui, QtCore

from .data_frame import DataFrame
from .variable_tab import VariableTab
from .util import fill_placeholder, load_style

Ui_MainWindow, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'mainwindow.ui'))

load_style()

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.subexpressions = [
            ('gaus(height,mu,sigma)','height * exp(-(x-mu)**2/(2*sigma**2))'),
            ('gausn(area,mu,sigma)','area/sqrt(2*pi*sigma**2) * exp(-(x-mu)**2/(2*sigma**2))'),
            ('linear(slope,offset)','slope*x + offset'),
            ]

        self.dataframe = DataFrame(subexpressions=self.subexpressions)
        fill_placeholder(self.ui.placeholder, self.dataframe)
        self.dataframe.formulaChanged.connect(self.on_formula_change)

        self.variables = VariableTab()
        fill_placeholder(self.ui.variables_box, self.variables)

        self.dataframe.raw_formula = 'A*exp(-(x-mu)**2/(2*sigma**2))'

    def on_formula_change(self, new_formula):
        symbols = [sym.name for sym in new_formula.free_symbols]
        symbols.sort()
        if 'x' in symbols:
            symbols.remove('x')
        self.variables.define_variables(symbols)
