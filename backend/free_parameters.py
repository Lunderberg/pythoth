#!/usr/bin/env python3

from .signal import Signal

class FreeParameters:
    def __init__(self):
        self.param_changed = Signal()
        self.param_list_changed = Signal()

        self.all_vars = {}
        self.current_vars = []

    def define_variables(self, var_list):
        self.current_vars = [self[var_name] for var_name in var_list]
        self.param_list_changed.emit(self)

    def __getitem__(self, key):
        try:
            return self.all_vars[key]
        except KeyError:
            self.all_vars[key] = FreeParameter(key, self.param_changed)
            return self.all_vars[key]

    def __iter__(self):
        return iter(self.current_vars)

    def __len__(self):
        return len(self.current_vars)


class FreeParameter:
    def __init__(self, name, param_changed = None):
        self.name = name
        self.param_changed = param_changed
        self._initial_value = 1
        self._fitted_value = None

    @property
    def initial_value(self):
        return self._initial_value

    @initial_value.setter
    def initial_value(self, val):
        changed = (val != self._initial_value)
        self._initial_value = val
        if changed and self.param_changed is not None:
            self.param_changed.emit(self)

    @property
    def fitted_value(self):
        return self._fitted_value

    @fitted_value.setter
    def fitted_value(self, val):
        changed = (val != self._fitted_value)
        self._fitted_value = val
        if changed and self.param_changed is not None:
            self.param_changed.emit(self)
