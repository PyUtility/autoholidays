# -*- encoding: utf-8 -*-

"""
A person is an end user of the application, that uses the algorithms
to plan their leave. The person construct contains information about
the user to make leave planning decisions, for example number of
days off, entitlements, and constraints.
"""

import datetime as dt

from typing import List, Union
from holidays import HolidayBase
from pydantic import BaseModel, Field

from autoholidays.core.calendar import ENUMDays

class CreditDays(BaseModel):
    """
    A :mod:`pydantic` base model to define leave credit days for
    the planning cycle. The credit days can then be passed to the
    :class:`PersonConstruct` class as a list of credit days, thus
    allowing arbitary types number of credit days to be passed.
    """

    name : str = Field(..., description = "Name/Type of Leave")
    days : int = Field(..., ge = 0, description = "Number of Days")
    date : dt.date = Field(..., description = "Date of Leave Credit")


class PersonConstruct(BaseModel):
    """
    The person constuct is defined considering defualt attributes and
    properties which might be required to find the optimal holidays.
    A basic information about the person, leave cycle, entitlements,
    and constraints are included in this construct.

    :type  name: str
    :param name: A string value representing the name of the person,
        this can be anything and is not tracked.

    :type  holidays: List[dt.date]
    :param holidays: A list of holidays for the person, this can be
        any number of days in the planning cycle. If any value is
        provided outside the planning cycle then it is ignored. A
        value in both ``holidays`` and ``weekoff`` is considered only
        once, to get the ordered list of applicable holidays.

    :type  creditDays: List[CreditDays]
    :param creditDays: A list of days when leave is credited to the
        person. The name of the class is currently not used. If any
        value is provided outside the planning cycle then it is
        safely ignored by the planning algorithm.

    :type  requiredLeaves: List[dt.date]
    :param requiredLeaves: Days where the user requires compulsory
        leaves, this is a list of dates. The algorithm will try to
        club these days with holiday list for a better suggestion.

    :type  regionalHolidays: List[Union[dt.date, HolidayBase]]
    :param regionalHolidays: A list of regional holidays for the
        person, this can either be manually defined as a list of dates
        or a list of :class:`holidays.HolidayBase` objects; check
        https://pypi.org/project/holidays/ for more information.

    :type  opening: int
    :param opening: Opening leave balance for the person, defaults
        to 0 (zero days).

    :type  weekoff: List[ENUMDays]
    :param weekoff: List of weekly off for the person, defaults to
        [ENUMDays.SATURDAY, ENUMDays.SUNDAY]. Once defined, this days
        will be constant throughout the planning process, and will
        not deduct leave balance, when consumed.
    """

    name : str
    holidays : List[dt.date]
    creditDays : List[CreditDays]
    requiredLeaves : List[dt.date]
    regionalHolidays : List[Union[dt.date, HolidayBase]]

    opening : int = Field(
        0, ge = 0, description = "Opening Leave Balance"
    )

    weekoff : List[ENUMDays] = Field(
        [ENUMDays.SATURDAY, ENUMDays.SUNDAY],
        description = "List of Weekly Off Days"
    )
