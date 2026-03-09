# -*- encoding: utf-8 -*-

"""
The holiday planner uses necessary base models/construct functions
and finally strategizes an optimal holiday for a person or a group of
person based on different scenarios.
"""

import datetime as dt

from typing import List, Tuple, Dict

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


    def plan(self, strategy : str = "balanced") -> List[List[dt.date]]:
        """
        Plan optimal holidays for a group of person based on a
        planning strategy.

        :type  strategy: str
        :param strategy: A planning strategy that dustributes the
            holiday in a specific way. Defaults to ``balanced``
            approach - that mixes short and long holidays.
        """

        strategy = self.__validate_strategy__(strategy)

        spacing = self.spacing[strategy]
        lengthRange = self.length[strategy]
        return spacing, lengthRange


    @staticmethod
    def planOne(person : PersonConstruct) -> List[List[dt.date]]:
        """
        A static method that calculates the optimal holiday for a
        single person, then returns the list of holidays. The method
        can then be used extended to plan for a group of person.
        """

        extWk = {
            key : dict(length = len(value), dates = value)
            for key, value in AutoHoliday.extendedWeekends(
                person.holidays
            ).items()
        }

        # get space between two consecutive long weekends
        spaces = {
            (key, key + 1) : (
                extWk[key + 1]["dates"][0] - extWk[key]["dates"][-1]
            ).days for key in list(extWk.keys())[:-1]
        }

        # sort the extended weekends based on the length of days
        extWk = dict(sorted(
            extWk.items(), reverse = True,
            key = lambda x : x[1]["length"]
        ))

        # also sort the spaces based on the gaps between two weekends
        spaces = dict(sorted(spaces.items(), key = lambda x : x[1]))

        return extWk, spaces


    @property
    def spacing(self) -> int:
        """
        A good planner is one that tries to create a balanced holiday
        over the planning years and for this seperation (or space)
        between two holiday is essential. The attribute returns the
        space based on a given strategy.
        """

        return dict(balanced = 21)


    @property
    def length(self) -> Tuple[int, int]:
        """
        Set the minimum and maximum length of total holidays (that
        includes public holidays, weekly off and leave days) that an
        individual wish to avail at one single time.
        """

        return dict(balanced = (3, 15))


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
