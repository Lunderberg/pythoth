#!/usr/bin/env python

from .signal import Signal

import sympy
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.sympy_tokenize import TokenError
from sympy.core.basic import Basic as SympyBasic

import numpy as np

from .substitutions import all_subs

class Formula:
    def __init__(self, subexpressions):
        self.raw_formula_changed = Signal()
        self.formula_changed = Signal()
        self.free_parameters_changed = Signal()
        self.subexpressions = subexpressions

        self._raw_text = ''
        self.valid_text = None

    @property
    def raw_text(self):
        return self._raw_text

    @raw_text.setter
    def raw_text(self, val):
        self._raw_text = val
        self.raw_formula_changed.emit(val)
        if self.is_valid(val):
            self.valid_text = val
            self.formula_changed.emit(self)
            self.free_parameters_changed.emit(self.free_params)

    def is_valid(self, raw_formula):
        try:
            parse_expr(raw_formula)
            return True
        except (SyntaxError, TokenError):
            return False

    @property
    def formula(self):
        if not self.valid_text:
            return None

        parsed = parse_expr(self.valid_text)
        if self.subexpressions:
            parsed = all_subs(parsed, self.subexpressions)

        return parsed

    @property
    def all_params(self):
        formula = self.formula
        if formula is None:
            return None

        return sorted((sym.name for sym in formula.free_symbols),
                      key=lambda name:name != 'x')

    @property
    def free_params(self):
        formula = self.formula
        if formula is None:
            return None

        return sorted(sym.name for sym in formula.free_symbols if sym.name!='x')

    @property
    def fit_function(self):
        formula = self.formula
        if formula is None:
            return None

        return sympy.lambdify(self.all_params, formula, dummify=False, modules=np)

    @property
    def latex(self):
        formula = self.formula
        if formula:
            return '${}$'.format(sympy.latex(formula))
        else:
            return ''
