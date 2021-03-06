#!/usr/bin/env python3

from .signal import Signal

class FreeParameters:
    def __init__(self, formula = None):
        self.param_changed = Signal()
        self.param_list_changed = Signal()

        self.all_vars = {}
        self.current_vars = []
        self.current_var_lookup = {}

        if formula is not None:
            formula.free_parameters_changed.connect(self.define_variables)


    def define_variables(self, var_list):
        self.current_vars = [self.get_or_make(var_name) for var_name in var_list]
        self.current_var_lookup = {par.name:par for par in self.current_vars}
        self.param_list_changed.emit(self)

    def initial_values(self):
        return {par.name:par.initial_value for par in self}

    def fitted_values(self):
        return {par.name:par.fitted_value for par in self}

    def get_or_make(self, key):
        try:
            return self.all_vars[key]
        except KeyError:
            self.all_vars[key] = FreeParameter(key, self.param_changed)
            return self.all_vars[key]

    def __iter__(self):
        return iter(self.current_vars)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.current_vars[key]
        elif isinstance(key, str):
            return self.current_var_lookup[key]
        else:
            raise TypeError('Index of FreeParameters must be int or str')

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
