#!/usr/bin/env python3

from sympy.parsing.sympy_parser import parse_expr

import sympy
from sympy.core.function import AppliedUndef

def func_sub_single(expr, func_def, func_body):
    """
    Given an expression and a function definition,
    find/expand an instance of that function.

    Ex:
        linear, m, x, b = sympy.symbols('linear m x b')
        func_sub_single(linear(2, 1), linear(m, b), m*x+b) # returns 2*x+1
    """
    # Find the expression to be replaced, return if not there
    for unknown_func in expr.atoms(AppliedUndef):
        if unknown_func.func == func_def.func:
            replacing_func = unknown_func
            break
    else:
        return expr

    # Map of argument name to argument passed in
    arg_sub = {from_arg:to_arg for from_arg,to_arg in
               zip(func_def.args, replacing_func.args)}

    # The function body, now with the arguments included
    func_body_subst = func_body.subs(arg_sub)

    # Finally, replace the function call in the original expression.
    return expr.subs(replacing_func, func_body_subst)


def func_sub(expr, func_def, func_body):
    """
    Given an expression and a function definition,
    find/expand all instances of that function.

    Ex:
        linear, m, x, b = sympy.symbols('linear m x b')
        func_sub(linear(linear(2,1), linear(3,4)),
                 linear(m, b), m*x+b)               # returns x*(2*x+1) + 3*x + 4
    """
    if any(func_def.func==body_func.func for body_func in func_body.atoms(AppliedUndef)):
        raise ValueError('Function may not be recursively defined')

    while True:
        prev = expr
        expr = func_sub_single(expr, func_def, func_body)
        if prev == expr:
            return expr


def all_subs(expr, subexpressions):
    """
    Given an expression and a list of (symbol, expansion) pairs,
    apply all substitutions.

    Accepts arguments either as strings or as sympy expressions.

    If the symbol is a function to be expanded, expands as a function.
    """
    if isinstance(expr, str):
        expr = parse_expr(expr)

    for (symbol, expansion) in subexpressions:
        if isinstance(symbol, str):
            symbol = parse_expr(symbol)
        if isinstance(expansion, str):
            expansion = parse_expr(expansion)

        if isinstance(symbol, AppliedUndef):
            expr = func_sub(expr, symbol, expansion)
        else:
            expr = expr.subs(symbol, expansion)
    return expr
