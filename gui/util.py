from PyQt4 import QtGui

import matplotlib as mpl

def fill_placeholder(placeholder, widget):
    if placeholder.layout() is not None:
        QtGui.QWidget().setLayout(placeholder.layout())
    layout = QtGui.QVBoxLayout(placeholder)
    layout.addWidget(widget)
    placeholder.setLayout(layout)

def load_style():
    # # Alternatively, place this in the .matplotlibrc
    # lines.linewidth: 2
    # patch.linewidth: 2
    # axes.color_cycle: black, blue, green, red, cyan, magenta, yellow
    # axes.linewidth: 2
    # axes.labelsize: 18
    # xtick.major.size: 10
    # xtick.major.width: 2
    # ytick.major.size: 10
    # ytick.major.width: 2
    # xtick.labelsize: large
    # ytick.labelsize: large
    # figure.facecolor: white
    mpl.rc('lines', linewidth=2)
    mpl.rc('patch', linewidth=2)
    mpl.rc('axes',
                  color_cycle=['black','blue','green','red','cyan','magenta','yellow'],
                  linewidth=2,
                  labelsize=18)
    mpl.rc('xtick.major',width=2, size=10)
    mpl.rc('ytick.major',width=2, size=10)
    mpl.rc('xtick',labelsize='large')
    mpl.rc('ytick',labelsize='large')
    mpl.rc('figure', facecolor='white')

def clear_layout(layout):
    for i in reversed(range(layout.count())):
        widget_to_remove = layout.itemAt(i).widget()
        layout.removeWidget(widget_to_remove)
        widget_to_remove.setParent(None)
