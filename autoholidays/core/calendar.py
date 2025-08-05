# -*- encoding: utf-8 -*-

"""
A construct to represent calendar information, this will be used to
calculate and define the planning period and to identify different
holidays - paid, regional, etc.
"""

import datetime as dt

from typing import List, Dict
from pydantic import BaseModel, model_validator

from autoholidays.core.static import ENUMDays
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


    @property
    def personHolidays(self) -> Dict[int, List[dt.date]]:
        """
        Returns a list of leaves based on regional holidays (planned
        leaves) and week-offs as per the planning cycle. The dates
        are always unique and sorted in ascending order.
        """

        return {
            idx : sorted([
                day for day in person.holidays + self.weekoffs(
                    self.allDates, person.weekoff
                )
                if day >= self.start and day <= self.final
            ])
            for idx, person in enumerate(self.persons)
        }


    @model_validator(mode = "after")
    def checkDates(self) -> 'PlanningCycle':
        assert self.start <= self.final, \
            "Start Date ≥ Final Date is Invalid"
        
        return self


    @property
    def allDates(self) -> List[dt.date]:
        """
        Returns a list of all calendar dates between the start and
        the final date, i.e., the planning cycle.
        """

        return [
            self.start + dt.timedelta(days = days)
            for days in range((self.final - self.start).days + 1)
        ]


    @staticmethod
    def weekoffs(
        dates : List[dt.date], weekoffs : List[ENUMDays]
    ) -> List[dt.date]:
        """
        Returns a list of date in the current planning cycle where
        a person is entitled for a weekly off. This is a static
        function, thus allowing to calculate for each person on the
        fly. The function does not consider the planning cycle.

        :type  dates: List[dt.date]
        :param dates: A list of dates all dates in the planning cycle,
            typically this is always ``self.allDates`` property.

        :type  weekoffs: List[ENUMDays]
        :param weekoffs: A list of enumerated weekoffs, of type
            :class:`ENUMDays` that is used to calculate valid dates in
            the planning cycle.
        """

        return [
            date for date in dates if date.weekday() in [
                wk.value for wk in weekoffs
            ]
        ]
