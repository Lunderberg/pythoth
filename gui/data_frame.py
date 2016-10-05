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
    def __init__(self, formula, parameters, parent=None):
        super().__init__(parent)
        self._setup_ui()

        self.formula = formula
        self.formula.raw_formula_changed.connect(self.from_raw_formula_changed)
        self.formula.formula_changed.connect(self.from_formula_changed)

        self.parameters = parameters
        self.parameters.param_changed.connect(lambda *args:self.redraw())

        self._gen_data()
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

    def _gen_data(self):
        import random
        counts = [sum(random.randint(1,6) for _ in range(5)) for _ in range(1000)]
        self.ydata, self.xdata = np.histogram(counts)

    def set_data(self, xdata, ydata):
        self.xdata = np.array(xdata)
        self.ydata = np.array(ydata)
        self.redraw()

    def redraw(self):
        self.figure.clear()
        axes = self.figure.add_subplot(1,1,1)

        if len(self.xdata) == len(self.ydata):
            axes.plot(self.xdata, self.ydata)
        elif len(self.xdata) == len(self.ydata)+1:
            ydata = np.insert(self.ydata, 0, self.ydata[0])
            axes.step(self.xdata,ydata)

        self.plot_formula(axes)

        self.canvas.draw()

    def plot_formula(self, axes):
        low = self.xdata.min()
        high = self.xdata.max()
        N = 1000
        xfit = np.arange(low, high, (high-low)/N)

        yinitial = self.formula.apply(xfit, self.parameters, value_type='initial')
        if yinitial is not None:
            axes.plot(xfit,yinitial,color='red',linestyle='--')

        yfitted = self.formula.apply(xfit, self.parameters, value_type='fitted')
        if yfitted is not None:
            axes.plot(xfit,yfitted,color='red')

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

        if len(self.xdata) == len(self.ydata):
            xdata = self.xdata
        elif len(self.xdata) == len(self.ydata)+1:
            xdata = (self.xdata[:-1] + self.xdata[1:])/2

        fitvals, cov = scipy.optimize.curve_fit(func, xdata, self.ydata,
                                                p0=initial)

        for name,val in zip(param_names, fitvals):
            self.parameters[name].fitted_value = val
