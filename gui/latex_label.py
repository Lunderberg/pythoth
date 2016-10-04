from PyQt4 import QtGui, QtCore

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from .util import fill_placeholder

class LatexLabel(QtGui.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        bg = self.palette().window().color()
        color = (bg.redF(), bg.greenF(), bg.blueF())
        self.figure = plt.figure(edgecolor=color, facecolor=color)
        self.canvas = FigureCanvas(self.figure)
        fill_placeholder(self, self.canvas)

        self.text = self.figure.suptitle('',
                                         x=0.5, y=0.5,
                                         horizontalalignment='center',
                                         verticalalignment='center',
                                         fontsize=36
                                     )

        self.latex_text = ''

    @property
    def latex_text(self):
        return self._latex_text

    @latex_text.setter
    def latex_text(self, val):
        self._latex_text = val

        self.text.set_text(val)
        self.adjust_text_size()
        self.canvas.draw()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_text_size()

    def adjust_text_size(self):
        bounds = self.text.get_window_extent(self.canvas.get_renderer())
        if bounds.width != 0 and bounds.height != 0:
            scaling = min(self.canvas.width()/bounds.width,
                          self.canvas.height()/bounds.height)
            self.text.set_fontsize(self.text.get_fontsize()*scaling)
