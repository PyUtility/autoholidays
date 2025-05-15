# -*- coding: utf-8 -*-

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
with open(os.path.join(os.path.dirname(__file__), "VERSION")) as fh:
    __version__ = fh.read().strip()

# ! let's check for package hard dependencies which must be available
hard_dependencies = ["pydantic"]
missing_dependencies = []

for dependency in hard_dependencies:
    try:
        __import__(dependency)
    except ImportError as err:
        missing_dependencies.append(err.name)

if missing_dependencies:
    raise ImportError(
        f"Missing hard dependencies: {missing_dependencies}."
    )

from autoholidays.api import *  # noqa: F403, E402

__all__ = [
    "ENUMDays",
    "CreditDays",
    "PersonConstruct",
]
