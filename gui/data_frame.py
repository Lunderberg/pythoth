import os

from PyQt4 import uic, QtGui, QtCore

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np

import sympy
from sympy.core.basic import Basic as SympyBasic

import scipy.optimize

from .util import fill_placeholder
from .latex_label import LatexLabel

Ui_DataFrame, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'dataframe.ui'))

class DataFrame(QtGui.QWidget):
    def __init__(self, data_set, formula, parameters, parent=None):
        super().__init__(parent)
        self._setup_ui()

        self.data_set = data_set
        self.data_set.data_set_changed.connect(self.from_data_set_changed)

        self.formula = formula
        self.formula.raw_formula_changed.connect(self.from_raw_formula_changed)
        self.formula.formula_changed.connect(self.from_formula_changed)

        self.parameters = parameters
        self.parameters.param_changed.connect(lambda *args:self.update())

        self.redraw()

    def _setup_ui(self):
        self.ui = Ui_DataFrame()
        self.ui.setupUi(self)

        self.ui.formula_input.textChanged.connect(self.on_text_changed)

        bg = self.palette().window().color()
        color = (bg.redF(), bg.greenF(), bg.blueF())
        self.figure = plt.figure(edgecolor=color, facecolor=color)
        self.canvas = FigureCanvas(self.figure)
        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.pan()
        toolbar.hide()

        fill_placeholder(self.ui.plot_holder, self.canvas)
        self.formula_display = LatexLabel()
        fill_placeholder(self.ui.formula_disp, self.formula_display)

    def from_data_set_changed(self, data_set):
        self.update()

    def redraw(self):
        self.figure.clear()
        self.axes = self.figure.add_subplot(1,1,1)

        self.drawn_data = self.data_set.draw(self.axes)
        self.draw_formula(self.axes)

        self.canvas.draw()

    def update(self):
        self.data_set.update(self.drawn_data)
        self.update_formula()
        self.canvas.draw()

    def draw_formula(self, axes):
        xfit, yinitial, yfit = self.fit_formula_data()
        self.initial_line = axes.plot(xfit, yinitial, color='red', linestyle='--')
        self.fitted_line = axes.plot(xfit, yfit, color='red')

    def update_formula(self):
        xfit, yinitial, yfit = self.fit_formula_data()
        self.initial_line[0].set_xdata(xfit)
        self.initial_line[0].set_ydata(yinitial)
        self.fitted_line[0].set_xdata(xfit)
        self.fitted_line[0].set_ydata(yfit)

    def fit_formula_data(self):
        low = self.data_set.xdata.min()
        high = self.data_set.xdata.max()
        N = 1000
        xfit = np.arange(low, high, (high-low)/N)

        yinitial = self.formula.apply(xfit, self.parameters, value_type='initial')
        if yinitial is None:
            yinitial = np.empty(xfit.shape)
            yinitial[:] = np.NAN

        yfit = self.formula.apply(xfit, self.parameters, value_type='fitted')
        if yfit is None:
            yfit = np.empty(xfit.shape)
            yfit[:] = np.NAN

        return xfit, yinitial, yfit


    def from_data_point_changed(self, data_point):
        self.update()

    def from_raw_formula_changed(self, text):
        if text != self.ui.formula_input.text():
            self.ui.formula_input.setText(text)

    def on_text_changed(self,*args):
        self.formula.raw_text = self.ui.formula_input.text()

    def from_formula_changed(self, formula):
        self.formula_display.latex_text = formula.latex

    def fit(self):
        func = self.formula.fit_function
        if not func:
            return

        param_names = func.__code__.co_varnames[1:]
        initial = [self.parameters[name].initial_value for name in param_names]

        fitvals, cov = scipy.optimize.curve_fit(func, self.data_set.xdata, self.data_set.ydata,
                                                p0=initial)

        for name,val in zip(param_names, fitvals):
            self.parameters[name].fitted_value = val
