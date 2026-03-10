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


    def plan(
        self,
        spacing : int = 17,
        lengthRange : Tuple[int, int] = (3, 15)
    ) -> List[List[dt.date]]:
        """
        Plan optimal holidays for a group of person based on a
        planning strategy, uses dynamic programming to iterate over
        the holidays. The function returns a list of list of holidays
        ideal for all the person(s).

        :type  spacing: int
        :param spacing: A parameter to control and spread the holidays
            over the planning cycle by limiting the minimum number of
            days between two consecutive days for all individual(s).
            Defaults to 17, i.e., atleast 17 days gap between the two
            consecutive holidays, unless there is a extended holiday.

        :type  lengthRange: Tuple[int, int]
        :param lengthRange: A tuple of minimum and maximum number of
            days for a holiday, defaults to (3, 15).
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
        collectiveHolidaysSet = set().union(*individualHolidays)
        collectiveHolidays = sorted(collectiveHolidaysSet)

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
                (dOrd not in collectiveHolidaysSet)
            ):
                dOrd -= 1

            if dOrd < startOrdinal:
                return startOrdinal

            while (
                ((dOrd - 1) >= startOrdinal) and
                ((dOrd - 1) in collectiveHolidaysSet)
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
                (dOrd not in collectiveHolidaysSet)
            ):
                dOrd += 1

            if dOrd > finalOrdinal:
                return finalOrdinal

            while (
                ((dOrd + 1) <= finalOrdinal) and
                ((dOrd + 1) in collectiveHolidaysSet)
            ):
                dOrd += 1

            return dOrd

        # ! collect unique off-day blocks from all collective holidays
        blockSet : Set[Tuple[int, int]] = set()
        for day in collectiveHolidays:
            blockSet.add((walkLeft(day), walkRight(day)))

        # ! filter blocks by lengthRange span and spacing gap constraints
        minLen, maxLen = lengthRange
        approvedBlocks : List[Tuple[int, int]] = []
        lastRight : int = startOrdinal - spacing - 1

        for left, right in sorted(blockSet):
            span = right - left + 1
            if span < minLen or span > maxLen:
                continue
            if left < lastRight + spacing:
                continue
            approvedBlocks.append((left, right))
            lastRight = right

        # ! calculate the final return result iterable
        return [
            [
                dt.datetime.fromordinal(dOrd).date()
                for dOrd in range(left, right + 1)
            ]
            for left, right in approvedBlocks
        ]


    @staticmethod
    def calculateLeaveDays(
        person : PersonConstruct,
        holidays : List[List[dt.date]]
    ) -> int:
        """
        Calculate the Number of Leave Days Required by a Person.

        Iterates over all days in each approved holiday block and
        counts the days that are not already covered by the person's
        existing public holidays or weekly offs. The result is the
        number of leave days the person must consume to enjoy the
        full off-period.

        :type  person: PersonConstruct
        :param person: The person construct for whom the leave days
            are to be calculated, using the construct defined in
            :mod:`autoholidays.person`.

        :type  holidays: List[List[dt.date]]
        :param holidays: A list of approved holiday blocks, typically
            the return value of :func:`plan`, where each inner list
            contains all calendar dates in one off-period block.

        :rtype:  int
        :return: Total number of leave days the person needs to take
            across all provided holiday blocks.
        """

        personHolidaySet = set(day.toordinal() for day in person.holidays)
        return sum(
            1 for block in holidays
            for day in block
            if day.toordinal() not in personHolidaySet
        )


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
