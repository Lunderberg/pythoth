#!/usr/bin/env python3

from ensure_venv import ensure_venv
ensure_venv(python='python3',requirements='requirements.txt', system_site_packages=True)

from enum import Enum

from func_sub import all_subs

import sympy
from sympy.core.function import AppliedUndef
from sympy.parsing.sympy_parser import parse_expr
import numpy as np
import scipy.optimize

class FitMethod(Enum):
    AutoDetect = 0
    LeastSquares = 1
    PoissonStat = 2

    @staticmethod
    def auto_detect(ydata):
        has_non_integer = any(int(y)!=y for y in ydata)
        if has_non_integer:
            return FitMethod.LeastSquares

        has_low_bin_counts = any(y<5 for y in ydata)
        if has_low_bin_counts:
            return FitMethod.PoissonStat
        else:
            return FitMethod.LeastSquares

class ErrorCalc(Enum):
    AutoDetect = 0
    AllEqualOne = 1
    SqrtCounts = 2

    @staticmethod
    def auto_detect(ydata):
        for y in ydata:
            if int(y) != y:
                return ErrorCalc.AllEqualOne
        else:
            return ErrorCalc.SqrtCounts

def fit(fit_function, xdata, ydata, errors=None,
        independent_var = sympy.symbol.Symbol('x'),
        fit_method = FitMethod.AutoDetect, error_calc = ErrorCalc.AutoDetect,
        subexpressions = None):
    """
    Given a fit function, fit the data given with that function.

    fit_function -- The function to be fit.
                    This may be a python function, a sympy expression, or a string.
                    Strings will be parsed as sympy expressions.
                    A python function should be passed an x value as first argument,
                       followed by each fit parameter,
                       and should return the y value of the fit.

    xdata -- The x coordinates of the data.

    ydata -- The y coordinates of the data.

    errors -- The uncertainties (sigma) of each point in the data.
              These are used only if performing a LeastSquares fit.
              If None, will be auto-generated according to error_calc.

    independent_var -- The independent variable of the fit, if given a sympy expression or string as fit_function
                       Defaults to using 'x'.

    fit_method -- The method by which to fit the data.
                  LeastSquares - Perform a linear least-squares fit
                  PoissonStat - Maximum likelihood method, assuming poisson statistics on each bin.
                  AutoDetect - Choose between LeastSquares and PoissonStat as necessary.
                               Will use PoissonStat if all bins are integer (likely to be binned data),
                               and has bins with bin content less than 5 (Gaussian assumption invalid).
                               Otherwise, will use LeastSquares.

    error_calc -- If errors is None when performing gaussian fit, the method by which to calculate the errors.
                  AllEqualOne - Assume uncertainties are all equal to one.
                  SqrtCounts - Use sqrt(ydata[i]) as errors[i].
                  AutoDetect - Choose between AllEqualOne and SqrtCounts as necessary.
                               Will use SqrtCounts if all bins are integer (likely to binned data).
                               Otherwise, will use AllEqualOne.

    subexpressions -- A list of (symbol, expansion) tuples.
                      Used to provide expansions for fit functions passed as strings or sympy expressions.
                      For example, (linear, m*x + b) will expand "linear" to "m*x + b".
                      Functions can also be provided, and will be expanded appropriately.
                      For example, (linear(m,b), m*x+b) will expand "linear(slope,offset)" to "slope*x + offset".
    """

    fit_function = normalize_fit_function(fit_function, subexpressions, independent_var)
    free_parameters = fit_function.__code__.co_varnames[1:]

    xdata = np.array(xdata)
    ydata = np.array(ydata)

    if fit_method == FitMethod.AutoDetect:
        fit_method = FitMethod.auto_detect(ydata)


    if fit_method == FitMethod.PoissonStat:
        raise NotImplementedError('Maximum-likelihood Poisson statistic not implemented')

    elif fit_method == FitMethod.LeastSquares:
        if errors is None:
            errors = generate_errors(ydata, error_calc)

        fitval, cov = scipy.optimize.curve_fit(fit_function, xdata, ydata,
                                               sigma=errors, absolute_sigma=True)
        print(fitval)
        print(cov)
        import IPython; IPython.embed()




def normalize_fit_function(fit_function, subexpressions, independent_var):
    # Convert string to sympy expression
    if isinstance(fit_function, str):
        fit_function = parse_expr(fit_function)

    # Convert sympy expression to function
    if isinstance(fit_function, tuple(sympy.core.all_classes)):
        if subexpressions is not None:
            fit_function = all_subs(fit_function, subexpressions)

        symbols = sorted(list(fit_function.free_symbols),
                         key=lambda sym:sym.name)

        # Move the independent variable to be first
        symbols.sort(key=lambda sym:sym!=independent_var)
        fit_function = sympy.lambdify(symbols, fit_function,
                                      dummify=False)

    return fit_function

def generate_errors(ydata, error_calc):
    if error_calc == ErrorCalc.AutoDetect:
        error_calc = ErrorCalc.auto_detect(ydata)

    if error_calc == ErrorCalc.AllEqualOne:
        return np.ones(len(ydata))
    elif error_calc == ErrorCalc.SqrtCounts:
        return np.sqrt(ydata)


if __name__=='__main__':
    #import IPython; IPython.embed()
    fit('a*x**2 + b*x + c',[1,2,3,4,5],[50,80,90,80,50],
        error_calc=ErrorCalc.AllEqualOne)
