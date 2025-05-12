# -*- encoding: utf-8 -*-

"""
AutoHolidays - A Powerful Algorithm to Plan Optimized Holidays
==============================================================

``AutoHolidays`` is an intelligent Python package that optimizes leave
planning by analyzing leave balances, weekends, public holidays, and
custom constraints. It calculates strategic combinations to maximize
continuous breaks while minimizing leave usage. Designed for
individuals and teams, it supports coordinated planning and adapts to
diverse organizational policies and regional calendars.
"""

import os

# ? package follows https://peps.python.org/pep-0440/
__version__ = open(
    os.path.join(os.path.dirname(__file__), "VERSION"), "r"
).read().strip()
