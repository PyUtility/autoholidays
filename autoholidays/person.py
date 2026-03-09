# -*- encoding: utf-8 -*-

"""
A person is an end user of the application that uses the algorithms
to plan their leave. The person construct contains information about
the user to make leave planning decisions, for example number of
days off, entitlements, and constraints.
"""

import datetime as dt

from typing import List, Union, Dict
from pydantic import BaseModel, Field, field_validator

from autoholidays.calendar import ENUMDays
from autoholidays.calendar import CreditDays


class PersonConstruct(BaseModel):
    """
    The person construct is defined considering default attributes and
    properties which might be required to find the optimal holidays.
    A basic information about the person, leave cycle, entitlements,
    and constraints are included in this construct.

    :type  name: str
    :param name: A string value representing the name of the person,
        this can be anything and is not tracked.

    :type  holidays: Union[List[dt.date], Dict[dt.date, str]]
    :param holidays: A list of holidays for the person, this can be
        any number of days in the planning cycle. If any value is
        provided outside the planning cycle then it is ignored. A
        value in both ``holidays`` and ``weekoff`` is considered only
        once, to get the ordered list of applicable holidays. The
        holiday can also be passed using :mod:`holidays` module, check
        https://pypi.org/project/holidays/ for more information.

    :type  creditDays: List[CreditDays]
    :param creditDays: A list of days when leave is credited to the
        person. The name of the class is currently not used. If any
        value is provided outside the planning cycle then it is
        safely ignored by the planning algorithm.

    :type  requiredLeaves: List[dt.date]
    :param requiredLeaves: Days where the user requires compulsory
        leaves, this is a list of dates. The algorithm will try to
        club these days with the holiday list for a better suggestion;
        defaults to empty list, meaning no priority.

    :type  opening: int
    :param opening: Opening leave balance for the person, defaults
        to ``0`` (zero days).

    :type  weekoff: List[ENUMDays]
    :param weekoff: List of weekly off for the person, defaults to
        [ENUMDays.SATURDAY, ENUMDays.SUNDAY]. Once defined, this days
        will be constant throughout the planning process, and will
        not deduct leave balance, when consumed.
    """

    name : str

    holidays : Union[List[dt.date], Dict[dt.date, str]] = Field(
        ..., description = "List of Holidays"
    )

    creditDays : List[CreditDays]
    requiredLeaves : List[dt.date] = Field(
        [], description = "List of Required Leaves"
    )

    opening : int = Field(
        0, ge = 0, description = "Opening Leave Balance"
    )

    weekoff : List[ENUMDays] = Field(
        [ENUMDays.SATURDAY, ENUMDays.SUNDAY],
        description = "List of Weekly Off Days"
    )


    @field_validator("holidays", mode = "before")
    @classmethod
    def sortedHolidays(
        cls, value : Union[List[dt.date], Dict[dt.date, str]]
    ) -> List[dt.date]:
        """
        Return a list of entitled leaves for the person, the function
        ensures that the values are always a list of unique dates.
        """

        value = list(set(value)) if isinstance(value, list) else \
            list(set(value.keys()))
        
        return sorted(value)
