import os

from PyQt4 import uic, QtGui, QtCore

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np

import sympy
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.sympy_tokenize import TokenError
from sympy.core.basic import Basic as SympyBasic

import scipy.optimize

from .util import fill_placeholder
from .latex_label import LatexLabel
from backend.substitutions import all_subs

Ui_DataFrame, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'dataframe.ui'))

class DataFrame(QtGui.QWidget):
    formulaChanged = QtCore.pyqtSignal(SympyBasic)

    def __init__(self, parameters, parent=None, subexpressions=None):
        super().__init__(parent)
        self._setup_ui()

        self.subexpressions = subexpressions

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

        fit_function = self.fit_function
        if fit_function is None:
            return

        initial_params = {par.name:par.initial_value for par in self.parameters}
        yinitial = [fit_function(x=x,**initial_params) for x in xfit]
        axes.plot(xfit,yinitial,color='red',linestyle='--')

        fitted_params = {par.name:par.fitted_value for par in self.parameters}
        if all(val!=None for val in fitted_params.values()):
            yfitted = [fit_function(x=x,**fitted_params) for x in xfit]
            axes.plot(xfit,yfitted,color='red')


    @property
    def raw_formula(self):
        return self.ui.formula_input.text()

    @raw_formula.setter
    def raw_formula(self, val):
        self.ui.formula_input.setText(val)

    @property
    def formula(self):
        if not self.raw_formula:
            return None

        try:
            parsed = parse_expr(self.raw_formula)
        except (SyntaxError, TokenError) as e:
            return None

        if self.subexpressions:
            parsed = all_subs(parsed, self.subexpressions)

        return parsed

    @property
    def fit_function(self):
        formula = self.formula
        if formula is None:
            return None

        symbols = sorted(list(formula.free_symbols),
                         key=lambda sym:sym.name!='x')
        return sympy.lambdify(symbols, formula, dummify=False, modules=np)

    @property
    def free_params(self):
        formula = self.formula
        if formula is None:
            return None

        return sorted(sym.name for sym in formula.free_symbols if sym.name!='x')

    def on_text_changed(self,*args):
        formula = self.formula
        if formula is not None:
            self.parameters.define_variables(self.free_params)
            self.formula_display.latex_text = '${}$'.format(sympy.latex(formula))

    def fit(self):
        func = self.fit_function
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
