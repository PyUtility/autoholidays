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
    def planOne(
        person : PersonConstruct,
        all_days : List[dt.date],
        spacing : int,
        length_range : Tuple[int, int]
    ) -> List[List[dt.date]]:
        """
        Plan the Optimal Holiday Breaks for a Single Person

        Uses dynamic programming with prefix-sum cost calculation to find
        the best set of holiday breaks for a single person. The algorithm
        maximises total consecutive days off while respecting spacing and
        length constraints and the available paid time off (PTO) budget.

        The approach mirrors the strategy used by holiday-optimizer.com:
        prefix sums allow O(1) PTO-cost queries for any date range, and
        a running-best DP table avoids re-scanning earlier states, giving
        an overall O(n x L) time complexity where ``n`` is the number of
        days in the planning cycle and ``L`` is ``max_len - min_len + 1``.

        :type  person: PersonConstruct
        :param person: A person construct whose ``holidays`` list already
            contains the merged set of public holidays and weekly off days
            (as produced by :meth:`__update_holidays__`).

        :type  all_days: List[dt.date]
        :param all_days: The complete ordered list of calendar dates in the
            planning cycle, typically ``self.cycle.allDays``.

        :type  spacing: int
        :param spacing: Minimum number of calendar days that must separate
            the end of one holiday break from the start of the next.

        :type  length_range: Tuple[int, int]
        :param length_range: The ``(min, max)`` inclusive range for the
            total number of days in a single holiday break (combining
            free days and PTO days).

        :rtype:  List[List[dt.date]]
        :return: An ordered list of holiday break blocks where each block
            is a list of consecutive calendar dates forming one optimal
            break. Returns an empty list when no valid plan exists.
        """

        free_days = set(person.holidays)
        min_len, max_len = length_range
        n = len(all_days)

        is_free = [1 if d in free_days else 0 for d in all_days]
        prefix = AutoHoliday.__prefix_free_days__(is_free)

        def pto_cost(i : int, j : int) -> int:
            return (j - i + 1) - (prefix[j + 1] - prefix[i])

        empty = (0, 0, [])

        def better(a : Tuple, b : Tuple) -> bool:
            return a[0] > b[0] or (a[0] == b[0] and a[1] < b[1])

        dp = [None] * (n + 1)
        dp[0] = empty
        best_up_to = [None] * (n + 1)
        best_up_to[0] = empty

        for j in range(n):
            for length in range(min_len, min(max_len, j + 1) + 1):
                i = j - length + 1
                pto = pto_cost(i, j)
                pta = AutoHoliday.__pta_at_date__(person, all_days[i])

                prev_idx = max(0, i - spacing)
                prev = best_up_to[prev_idx] if best_up_to[prev_idx] is not None else empty
                total_pto = prev[1] + pto

                if total_pto > pta:
                    continue

                candidate = (
                    prev[0] + length,
                    total_pto,
                    prev[2] + [list(all_days[i : j + 1])]
                )

                if dp[j + 1] is None or better(candidate, dp[j + 1]):
                    dp[j + 1] = candidate

            best_up_to[j + 1] = best_up_to[j]
            if dp[j + 1] is not None and (
                best_up_to[j] is None or better(dp[j + 1], best_up_to[j])
            ):
                best_up_to[j + 1] = dp[j + 1]

        return best_up_to[n][2] if best_up_to[n] is not None else []


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


    @staticmethod
    def __prefix_free_days__(is_free : List[int]) -> List[int]:
        """
        Build a Prefix-Sum Array over the Free-Day Indicator List

        Enables O(1) computation of the number of free (non-PTO) days
        within any date range ``[i, j]`` via
        ``prefix[j + 1] - prefix[i]``.

        :type  is_free: List[int]
        :param is_free: A binary array where ``1`` marks a free day
            (weekend or public holiday) and ``0`` marks a working day
            that requires a PTO deduction.

        :rtype:  List[int]
        :return: A prefix-sum array of length ``len(is_free) + 1`` where
            index ``k`` holds the cumulative count of free days in
            ``is_free[0 : k]``.
        """

        prefix = [0] * (len(is_free) + 1)
        for idx, v in enumerate(is_free):
            prefix[idx + 1] = prefix[idx] + v

        return prefix


    @staticmethod
    def __pta_at_date__(
        person : PersonConstruct,
        date : dt.date
    ) -> int:
        """
        Return the Cumulative PTO Balance Available on a Given Date

        Computes the total paid time off that a person may draw from on
        or before ``date`` by summing the opening balance and all credit
        entries whose credit date is on or before ``date``.

        :type  person: PersonConstruct
        :param person: A person construct with an opening balance and a
            list of :class:`CreditDays` entitlements.

        :type  date: dt.date
        :param date: The reference date used to filter credit entries.

        :rtype:  int
        :return: Total PTO days available (opening balance plus all
            credits whose ``date`` field is on or before ``date``).
        """

        return person.opening + sum(
            c.days for c in person.creditDays
            if c.date <= date
        )


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
