import os

from PyQt4 import uic, QtGui, QtCore

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

import sympy
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.sympy_tokenize import TokenError
from sympy.core.basic import Basic as SympyBasic

from .util import fill_placeholder
from .latex_label import LatexLabel
from backend.substitutions import all_subs

Ui_DataFrame, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'dataframe.ui'))

class DataFrame(QtGui.QWidget):
    formulaChanged = QtCore.pyqtSignal(SympyBasic)

    def __init__(self, parent=None, subexpressions=None):
        super().__init__(parent)
        self.ui = Ui_DataFrame()
        self.ui.setupUi(self)

        self.subexpressions = subexpressions

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

        self._draw_plot()

    def _draw_plot(self):
        import random
        self.figure.clear()
        axes = self.figure.add_subplot(1,1,1)
        axes.hist([sum(random.randint(1,6) for _ in range(5)) for _ in range(1000)],
                  histtype='step')
        self.figure.tight_layout()
        self.canvas.draw()

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
            print('Error parsing:',e)
            return None

        if self.subexpressions:
            parsed = all_subs(parsed, self.subexpressions)

        return parsed

    def on_text_changed(self,*args):
        formula = self.formula
        if formula is not None:
            self.formulaChanged.emit(formula)
            self.formula_display.latex_text = '${}$'.format(sympy.latex(formula))
