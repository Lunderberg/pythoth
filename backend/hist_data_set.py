#!/usr/bin/env python3

from .signal import Signal

import numpy as np

class HistDataSet:
    def __init__(self, bin_edges, bin_content, loc='middle'):
        if len(bin_edges) != len(bin_content)+1:
            raise ValueError('Length of bin_edges ({}) must be one greater than length of bin_content ({})'.format(
                len(bin_edges), len(bin_content)))

        self.bin_edges = bin_edges
        self.bin_content = bin_content
        self.loc = loc

        self.data_set_changed = Signal()

    def __len__(self):
        return len(self.bin_content)

    def __getitem__(self, index):
        return HistDataPoint(self, index)

    @property
    def xdata(self):
        if self.loc=='left':
            return self.bin_edges[:-1]
        elif self.loc=='middle':
            return (self.bin_edges[:-1] + self.bin_edges[1:])/2.0
        elif self.loc=='right':
            return self.bin_edges[1:]
        else:
            raise ValueError("Bin location must be one of 'left', 'middle', or 'right'")

    @property
    def ydata(self):
        return self.bin_content

    def draw(self, axes):
        ydata = np.insert(self.bin_content, 0, self.bin_content[0])
        return axes.step(self.bin_edges, ydata)

    def update(self, drawn_obj):
        ydata = np.insert(self.bin_content, 0, self.bin_content[0])
        drawn_obj[0].set_xdata(self.bin_edges)
        drawn_obj[0].set_ydata(ydata)


class HistDataPoint:
    def __init__(self, data_set, i):
        self._data_set = data_set
        self._i = i

    @property
    def low_edge(self):
        return self._data_set.bin_edges[self._i]

    @low_edge.setter
    def low_edge(self, val):
        self._data_set.bin_edges[self._i] = val
        self._data_set.data_set_changed.emit(self._data_set)

    @property
    def high_edge(self):
        return self._data_set.bin_edges[self._i + 1]

    @high_edge.setter
    def high_edge(self, val):
        self._data_set.bin_edges[self._i + 1] = val
        self._data_set.data_set_changed.emit(self._data_set)

    @property
    def bin_content(self):
        return self._data_set.bin_content[self._i]

    @bin_content.setter
    def bin_content(self, val):
        self._data_set.bin_content[self._i] = val
        self._data_set.data_set_changed.smit(self._data_set)
