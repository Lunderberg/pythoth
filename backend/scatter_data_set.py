#!/usr/bin/env python3

from .signal import Signal

class ScatterDataSet:
    def __init__(self, xdata, ydata):
        if len(xdata) != len(ydata):
            raise ValueError("Length of xdata ({}) must equal length of ydata ({}).".format(
                len(xdata), len(ydata)))

        self.xdata = xdata
        self.ydata = ydata

        self.data_set_changed = Signal()

    def __len__(self):
        return len(self.xdata)

    def __getitem__(self, index):
        return ScatterDataPoint(self, index)

    def draw(self, axes):
        return axes.scatter(self.xdata, self.ydata)

    def update(self, drawn_obj):
        drawn_obj.set_xdata(self.xdata)
        drawn_obj.set_ydata(self.ydata)


class ScatterDataPoint:
    def __init__(self, data_set, i):
        self._data_set = data_set
        self._i = i

    @property
    def x(self):
        return self._data_set.xdata[self._i]

    @x.setter
    def x(self, val):
        self._data_set.xdata[self._i] = val
        self._data_set.data_set_changed.emit(self._data_set)

    @property
    def y(self):
        return self._data_set.ydata[self._i]

    @y.setter
    def y(self, val):
        self._data_set.ydata[self._i] = val
        self._data_set.data_set_changed.emit(self._data_set)
