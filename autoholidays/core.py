# -*- encoding: utf-8 -*-

"""
The holiday planner uses necessary base models/construct functions
and finally strategizes an optimal holiday for a person or a group of
person based on different scenarios.
"""

import datetime as dt

from typing import List
from autoholidays.calendar_ import PlanningCycle

class AutoHoliday:
    def __init__(self, planning : PlanningCycle) -> None:
        self.planning = planning


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
