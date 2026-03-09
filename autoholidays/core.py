# -*- encoding: utf-8 -*-

"""
The holiday planner uses necessary base models/construct functions
and finally strategizes an optimal holiday for a person or a group of
person based on different scenarios.
"""

import warnings
import datetime as dt

from typing import List

from autoholidays.person import PersonConstruct
from autoholidays.calendar import PlanningCycle, ENUMDays

class AutoHoliday:
    """
    A class to plan an optimal holiday for a person or a group of
    person. The class is initialized with a planning cycle, set of
    person(s), and a strategy to plan the holiday.

    :type  persons: List[PersonConstruct]
    :param persons: A list of person(s) to plan for, uses the persons
        construct defined in :mod:`autoholidays.person`. At least,
        one person is required for planning.

    :type  planning: PlanningCycle
    :param planning: A fixed planning cycle which is same across all
        the person(s) to plan holidays.

    :type  strategy: str
    :param strategy: A planning strategy that dustributes the holiday
        in a specific way. Defaults to ``balanced`` approach - that
        mixes short and long holidays.
    """

    def __init__(
        self,
        persons : List[PersonConstruct],
        planning : PlanningCycle,
        strategy : str = "balanced"
    ) -> None:
        self.planning = planning

        self.persons = self.__validate_holidays__(persons)
        self.strategy = self.__validate_strategy__(strategy)
        return persons


    @staticmethod
    def extendedWeekends(dates : List[dt.date]) -> List[List[dt.date]]:
        """
        Given a list of days, iteratively calculate the difference
        between consecutive days and returns a list of days that can
        be clubbed together. This method is particularly helpful in
        identification of extended weekends (weekly off, that is
        immediately followed by a public holiday).

        :type  dates: List[dt.date]
        :param dates: List of holidays (weekly off, public holidays,
            and any other types of entitlement) for a person.

        Return Values
        -------------

        :rtype:  List[List[dt.date]]
        :return: An iterable list of consecutive dates where each is
            one valid long weekend.
        
        Example of the functions return statement:

        .. code-block:: python

            [[2026-01-01], [2026-01-03, 2026-01-04], ...]

        An extended weekend, if utilized correctly, can provide a set
        of optimal holidays without the need to use a leave.
        """

        dates = [ date.toordinal() for date in dates ]

        groups = [[dates[0]]]
        for cur, nxt in zip(dates[:-1], dates[1:]):
            if (nxt - cur) <= 1:
                groups[-1].append(nxt)
            else:
                groups.append([nxt])

        return [
            [
                dt.datetime.fromordinal(date).date() for date in group
            ] for group in groups
        ]


    @staticmethod
    def weekOffs(
        dates : List[dt.date], weekends : List[ENUMDays]
    ) -> List[dt.date]:
        """
        Returns a list of date in the current planning cycle where
        a person is entitled for a weekly off. This is a static
        function, thus allowing to calculate for each person on the
        fly. The function does not consider the planning cycle.

        :type  dates: List[dt.date]
        :param dates: A list of all dates in the planning cycle,
            typically this is always ``self.allDates`` property.

        :type  weekoffs: List[ENUMDays]
        :param weekoffs: A list of enumerated weekoffs, of type
            :class:`ENUMDays` that is used to calculate valid dates in
            the planning cycle.
        """

        return [
            date for date in dates if date.weekday() in [
                wk.value for wk in weekends
            ]
        ]


    def __validate_strategy__(self, strategy : str) -> str:
        """
        Validate the strategy value based on the list of valid
        strategies. The function raises an assertion error if the
        strategy is invalid. The following types of strategies are
        available:

            * balanced: A strategy that mixes short and long holidays
                to provide a balanced holiday plan for the person(s).
        """

        valid = ["balanced"]
        assert strategy in valid, f"Invalid Strategy: {strategy}"

        return strategy


    def __validate_holidays__(
        self,
        persons : List[PersonConstruct]
    ) -> List[PersonConstruct]:
        """
        Validate the list of holidays for the person(s) and returns
        valid days, this is helpful in case of invalid holidays, i.e.,
        any holiday that is falling outside of the planning cycle.
        """

        start, final = self.planning.start, self.planning.final
        for person in persons:
            current = person.holidays
            updated = [
                holiday for holiday in person.holidays
                if holiday >= start and holiday <= final
            ]

            if current != updated:
                warnings.warn(f"Holiday's Updated for {person.name}")
                person.holidays = sorted(updated)
            else:
                person.holidays = sorted(current)

