# -*- encoding: utf-8 -*-

"""
The holiday planner uses necessary base models/construct functions
and finally strategizes an optimal holiday for a person or a group of
person based on different scenarios.
"""

import datetime as dt

from typing import List, Tuple, Dict, Set
from itertools import pairwise, chain

from autoholidays.person import PersonConstruct
from autoholidays.calendar import PlanningCycle, ENUMDays

class AutoHoliday:
    """
    A class to plan an optimal holiday for a person or a group of
    person. The class is initialized with a planning cycle, set of
    person(s), and a strategy to plan the holiday.

    :type  cycle: PlanningCycle
    :param cycle: A fixed planning cycle which is same across all the
        person(s) to plan holidays.

    :type  persons: List[PersonConstruct]
    :param persons: A list of person(s) to plan for, uses the persons
        construct defined in :mod:`autoholidays.person`. At least,
        one person is required for planning.
    """

    def __init__(
        self,
        cycle : PlanningCycle,
        persons : List[PersonConstruct],
    ) -> None:
        """
        Initialization method that captures the planning cycle, and
        the person(s) to plan optimal holidays. The initialization
        class is so defined that different types of strategy can be
        tested using the ``plan`` method and the user can finally
        choose the one that suits them the best.
        """

        self.cycle = cycle
        self.persons = self.__update_holidays__(persons)


    def plan(self) -> List[List[dt.date]]:
        """
        Plan optimal holidays for a group of person based on a
        planning strategy, uses dynamic programming to iterate over
        the holidays. The function returns a list of list of holidays
        ideal for all the person(s).
        """

        start, final = self.cycle.start, self.cycle.final
        startOrdinal, finalOrdinal = list(map(
            lambda date: date.toordinal(), [start, final]
        ))

        # convert the holiday list into a set of values; can use union
        individualHolidays = [
            set([day.toordinal() for day in person.holidays])
            for person in self.persons
        ]
        collectiveHolidays = sorted(set().union(*individualHolidays))

        def walkLeft(hOrd : int) -> int:
            """
            Given an ideal ordinal date from the collective holidays
            of all the individual(s), walks to the left to find the
            start of its surrounding off-day block. Opposite function
            is ``walkRight`` which iterates on the right side.
            """
            dOrd = hOrd - 1

            while (
                (dOrd >= startOrdinal) and
                (dOrd not in collectiveHolidays)
            ):
                dOrd -= 1

            if dOrd < startOrdinal:
                return startOrdinal

            while (
                ((dOrd - 1) >= startOrdinal) and
                ((dOrd - 1) in collectiveHolidays)
            ):
                dOrd -= 1

            return dOrd

        def walkRight(hOrd : int) -> int:
            """
            Given an ideal ordinal date from the collective holidays
            of all the individual(s), walks to the right to find the
            end of its surrounding off-day block. Opposite function
            is ``walkLeft`` which iterates on the left side.
            """
            dOrd = hOrd + 1

            while (
                (dOrd <= finalOrdinal) and
                (dOrd not in collectiveHolidays)
            ):
                dOrd += 1

            if dOrd > finalOrdinal:
                return finalOrdinal

            while (
                ((dOrd + 1) <= finalOrdinal) and
                ((dOrd + 1) in collectiveHolidays)
            ):
                dOrd += 1

            return dOrd

        # ! create an ideal list of holidays from individual walks
        ideal : Dict[int, Set[int]] = {
            idx : set() for idx in range(len(self.persons))
        }

        for day in collectiveHolidays:
            left, right = walkLeft(day), walkRight(day)
            
            for idx in range(len(self.persons)):
                ideal[idx].update(
                    dOrd for dOrd in range(left, right + 1)
                    if dOrd not in individualHolidays[idx]
                )

        # ! calculate the final return resilt iterable
        result : List[List[dt.date]] = []
        for idx in range(len(self.persons)):
            person = self.persons[idx]

            scheduled = [
                dt.datetime.fromordinal(dOrd).date()
                for dOrd in sorted(ideal[idx])
            ]

            credits = sorted([
                (cd.date, cd.days) for cd in person.creditDays
            ], key = lambda x : x[0])

            balance, creditIndex = 0, 0

            approved : List[dt.date] = []
            for day in scheduled:
                while (
                    (creditIndex < len(credits)) and
                    credits[creditIndex][0] <= day
                ):
                    balance += credits[creditIndex][1]
                    creditIndex += 1

                if balance > 0:
                    approved.append(day)
                    balance -= 1

            result.append(approved)

        return result


    @staticmethod
    def extendedWeekends(
        dates : List[dt.date]
    ) -> Dict[int, List[dt.date]]:
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

        return {
            idx : [
                dt.datetime.fromordinal(date).date() for date in group
            ] for idx, group in enumerate(groups)
        }


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


    def __update_holidays__(
        self,
        persons : List[PersonConstruct]
    ) -> List[PersonConstruct]:
        """
        Validate the list of holidays for the person(s) and returns
        valid days which is a combination of all the weekly off the
        individual is eligible for, and all the public holidays that
        is available.
        """

        start, final = self.cycle.start, self.cycle.final
        for person in persons:
            updated = [
                holiday for holiday in person.holidays
                if holiday >= start and holiday <= final
            ] + self.weekOffs(self.cycle.allDays, person.weekoff)

            person.holidays = sorted(updated)

        return persons
