# -*- encoding: utf-8 -*-

"""
Capture and Define Custom Errors for Package
"""

class InvalidDayNum(ValueError):
    """
    Invalid Leave Days Error

    This error is raised when the leave days are not in the range of
    0-6, where 0 is Sunday and 6 is Saturday. The zerobased indexed is
    preserved to provide backward compatibility with the :mod:`calendar`
    module in Python.
    """

    pass
