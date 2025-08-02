# -*- encoding: utf-8 -*-

"""
A construct to represent calendar information, this will be used to
calculate and define the planning period and to identify different
holidays - paid, regional, etc.
"""

import datetime as dt

from typing import List
from pydantic import BaseModel, model_validator

from autoholidays.core.person import PersonConstruct


class PlanningCycle(BaseModel):
    """
    A planning cycle is a set of start and end date for planning
    optimal leave for the user(s) using the application. The cycle
    can be of any length, but it is recommended to have a single year
    that best suits all the ``persons`` for an optimal planning.

    :type  start, final: dt.date
    :param start, final: First and last date (inclusive) for the
        planning cycle.

    :type  persons: List[PersonConstruct]
    :param persons: A list of person(s) to plan for, uses the persons
        construct defined in :mod:`autoholidays.core.person`. Atleast
        one person is required for planning.
    """

    start : dt.date
    final : dt.date
    persons : List[PersonConstruct]


    @model_validator(mode = "after")
    def checkDates(self) -> 'PlanningCycle':
        assert self.start <= self.final, \
            "Start Date ≥ Final Date is Invalid"
        
        return self


    @property
    def allDates(self) -> List[dt.date]:
        return [
            self.start + dt.timedelta(days = days)
            for days in range((self.final - self.start).days + 1)
        ]
