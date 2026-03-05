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

__version__ = "v0.0.2.dev0"

# ? added init time options registrations from autoholidays.api
from autoholidays.api import *  # noqa: F403, E402

__all__ = [
    "ENUMDays",
    "CreditDays",
    "PlanningCycle",
    "PersonConstruct",
    "extendedWeekends"
]
