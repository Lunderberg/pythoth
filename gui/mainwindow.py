import os

from PyQt4 import uic, QtGui, QtCore
import numpy as np

from .data_frame import DataFrame
from .parameter_tab import ParameterTab
from .util import fill_placeholder, load_style
from backend.free_parameters import FreeParameters
from backend.formula import Formula
from backend.hist_data_set import HistDataSet

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
        self.formula = Formula(self.subexpressions)
        self.parameters = FreeParameters(formula=self.formula)

        self.data_set = self._gen_data()
        self.data_frame = DataFrame(data_set=self.data_set,
                                    parameters=self.parameters,
                                    formula=self.formula)
        fill_placeholder(self.ui.placeholder, self.data_frame)

        self.parameters = ParameterTab(parent=self, parameters=self.parameters)
        fill_placeholder(self.ui.parameters_box, self.parameters)

        self.ui.fit_button.clicked.connect(self.on_do_fit)

        self.formula.raw_text = 'A*exp(-(x-mu)**2/(2*sigma**2))'

    def _gen_data(self):
        import random
        counts = [sum(random.randint(1,6) for _ in range(5)) for _ in range(1000)]
        bin_content, bin_edges = np.histogram(counts)
        return HistDataSet(bin_edges, bin_content)

    def on_do_fit(self, *args):
        self.data_frame.fit()
