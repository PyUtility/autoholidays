# -*- encoding: utf-8 -*-

"""
A Core Auto-Holiday Planning
"""

import datetime as dt
import datetime_ as dt_

from autoholidays.utils.calender import AnyCycle
from autoholidays.utils.person import PersonConstruct

class LeavePlanner:
    def __init__(
        self,
        period : AnyCycle,
        persons : list[PersonConstruct]
    ) -> None:
        self.start, self.end = period.start, period.end
        
        # a list of persons, this should be defined and passed
        # holiday construct are person wise, add them while defining
        self.persons = persons


    @property
    def calender(self) -> list:
        """
        Return the Calender of Dates from Start to End of Planning

        The property uses :mod:`datetime_` to get all the dates from
        start to end of planning days. The iterable list can then be
        extended to various other properties or methods to find and
        derive optimal result for the year.
        """

        return list(dt_.date_range(start = self.start, end = self.end))


    @property
    def plan_duration(self) -> int:
        """
        Return the Total No. of Days between Start and End
        """

        return (self.end - self.start).days


    @property
    def paid_holidays(self) -> dict[list]:
        """
        Returns a List of Paid Holidays per Person

        Each person has a set of weekly holidays and additional state
        holidays. The property returns an iterable of holidays for
        each defined person by returning an unique set of days sorted
        in ascending order. The key of the dictionary is same as the
        person :attr:`Person.name` attribute.
        """

        holidays = {
            person.name : dict(
                comp_week_off = [
                    date for date in self.calender
                    if date.weekday() in person.comp_week_off.day_values
                ],
                additional_holidays = [
                    holiday.date for holiday in person.additional_holidays
                ]
            )
            for person in self.persons
        }

        return {
            k : v | dict(
                unique = sorted(list(set(
                    v["comp_week_off"] + v["additional_holidays"]
                ))),
                nunique = len(sorted(list(set(
                    v["comp_week_off"] + v["additional_holidays"]
                ))))
            )
            for k, v in holidays.items()
        }


    @property
    def verbose_paid_holidays(self) -> dict:
        """
        Return a Verbose of Total Paid Holiday for Each Person
        """

        return {
            person.name : dict(
                total = self.paid_holidays[person.name]["nunique"],
                ratio = round(
                    self.paid_holidays[person.name]["nunique"] / self.plan_duration,
                    5
                )
            )
            for person in self.persons
        }


    def long_weekends(
        self,
        tolerance : int = 0,
        verbose : bool = True,
        **kwargs
    ) -> dict:
        """
        Get a List of Extended Weekends for the Plan Duration

        The long (or an extended) weekend is coined when there is a
        paid holiday immediately before or after the weekends. The long
        weekends gives a long vacation without taking a day off, or
        with a minimum number of leave we get a long vacation.

        For example, considering a :attr:`H` as holiday and :attr:`W`
        as weekend, we can showcase the long weekends as:

        .. code-block:: text

            S M T W T F S  S M T W T F S
            W X X X X X W  W X X X X X W  # CASE: A - Normal Schedule
            0 1 1 1 1 1 0  0 1 1 1 1 1 0  # Required Leaves = 10

            S M T W T F S  S M T W T F S
            W X X X X H W  W X X X X X W  # CASE: A - Long Weekends
            0 1 1 1 1 0 0  0 1 1 1 1 1 0  # Required Leaves = 9
            

        :type  tolerance: int
        :param tolerance: An integer representing the number of days
            in-between to be considered a long weekend. Defaults to 0.

        :type  verbose: bool
        :param verbose: Print a dictionary of additional informations,
            like total long weekends to screen. Defaults to True.
        
        Tolerance Level
        ---------------

        The tolerance is the number of days in-between a week-off and
        a paid holiday to be considered for a long-weekend. To explain,
        we can consider the following example:

        .. code-block:: python

            li = [1, 2, 3, 5, 6, 9, 10] # ordinals of dates

            model = ... # leave planner module
            print(model.long_weekends()) # immediate numbers
            >> [[1, 2, 3], [5, 6], [9, 10]

            print(model.long_weekends(tolerance = 1))
            >> [[1, 2, 3, 5, 6], [9, 10]]
        
        Return Value
        ------------

        The function internally converts the date to an ordinal value
        to calculate the long weekends. The result is returned as a
        dictionary of list of lists. The key is same as the person name
        and the value is the list of lists of long weekend ranges.

        :rtype:  dict
        :return: A dictionary of person and list of lists of long
            weekend ranges.
        """

        ordinals = {
            person : [date.toordinal() for date in values["unique"]]
            for person, values in self.paid_holidays.items()
        }

        # keyword arguments, define min_toleralce - only for verbose
        min_count = kwargs.get("min_count", 2)
        values_in_subgroups = kwargs.get("values_in_subgroups", False)

        weekends = {person.name : None for person in self.persons}

        for person in self.persons:
            person = person.name
            groups = [[ordinals[person][0]]]

            ordinal_ = ordinals[person]
            for cur, nxt in zip(ordinal_, ordinal_[1:]):
                if (nxt - cur) <= tolerance + 1:
                    groups[-1].append(nxt)
                else:
                    groups.append([nxt])

            groups = [
                [dt.datetime.fromordinal(date).date() for date in group]
                for group in groups
            ]

            subgroups = {
                f"VACATION #{str(idx + 1).zfill(3)}" : dict(
                    start = group[0], end = group[-1],
                    duration = (group[-1] - group[0]).days + 1,
                    values = \
                        list(dt_.date_range(group[0], group[-1]))
                        if values_in_subgroups else None
                )
                for idx, group in enumerate(groups)
                if len(group) >= min_count
            }

            weekends[person] = dict(
                groups = groups,
                subgroups = subgroups
            )

            if verbose:
                print(f"VERBOSE: Long Weekend({person})")
                print(f"  >> No. of Long Weekends = {len(groups):,}")
                print(f"  >> #LW (#Days >= {min_count}) = {len(subgroups):,}")

        return weekends
