import os

from PyQt4 import uic, QtGui, QtCore

from .data_frame import DataFrame
from .variable_tab import VariableTab
from .util import fill_placeholder, load_style
from backend.free_parameters import FreeParameters

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
        self.parameters = FreeParameters()

        self.data_frame = DataFrame(parameters=self.parameters,
                                    subexpressions=self.subexpressions)
        fill_placeholder(self.ui.placeholder, self.data_frame)
        self.data_frame.formulaChanged.connect(self.on_formula_change)

        self.variables = VariableTab(parent=self, parameters=self.parameters)
        fill_placeholder(self.ui.variables_box, self.variables)
        self.variables.initialParamsChanged.connect(self.on_initial_params_change)

        self.ui.fit_button.clicked.connect(self.on_do_fit)

        self.data_frame.raw_formula = 'A*exp(-(x-mu)**2/(2*sigma**2))'

    def on_formula_change(self, new_formula):
        symbols = [sym.name for sym in new_formula.free_symbols]
        symbols.sort()
        if 'x' in symbols:
            symbols.remove('x')
        self.variables.define_variables(symbols)

        self.variables.initial_values()

    def on_initial_params_change(self, params):
        self.data_frame.params = params

    def on_do_fit(self, *args):
        self.data_frame.fit()
