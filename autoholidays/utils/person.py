# -*- encoding: utf-8 -*-

"""
A Utility Base Model to define a Person

A person is an end user who is going to consume the API to find the
best possible leave. The module provides the ability to find the best
possible combination for a single or a group of person, thus defining
a structured people's construct is essential.
"""

import datetime as dt

from pydantic import BaseModel

from autoholidays.utils.leaves import (
    CustomLeaves,
    CompWeeklyLeave
)

from autoholidays.utils.holidays import HolidayConstruct
from autoholidays.utils.calender import MonthDayConstruct, AnyCycle

class PersonConstruct(BaseModel):
    """
    Defination of a Enduser or a Person

    The person constuct is defined considering defualt attributes and
    properties which might be required to find the optimal holidays.

    The person construct should be defined as per the planning cycle,
    thus the year-month and days should be constant. This is because,
    for each cycle the holidays and type of leaves can differ, but
    we can create an extended class to track historic leaves - which
    is out of scope of this package and should be handled seperately.

    :type  name: str
    :param name: A string representing the name of the person, this
        can be anything can beused to save the object.

    :type  cycle: LeaveCycle
    :param cycle: A :class:`LeaveCycle` object which defines the
        leave planning cycle for a person.

    :type  comp_week_off: CompWeeklyLeave
    :param comp_week_off: A :class:`CompWeeklyLeave` object which
        defines the compulsary weekly leaves for a person.

    :type  custom_leaves: tuple[CustomLeaves]
    :param custom_leaves: A tuple of :class:`CustomLeaves` objects
        which defines the custom leaves for a person.

    :type  additional_holidays: tuple[HolidayConstruct]
    :param additional_holidays: A tuple of :class:`HolidayConstruct`
        objects which defines the additional holidays for a person
        for the given planning cycle. Check class attributes for field
        names and their descriptions.

    :type  required_leaves: tuple[HolidayConstruct]
    :param required_leaves: A tuple of :class:`HolidayConstruct`
        objects which defines the required leaves for a person
        for the given planning cycle. Check class attributes for field
        names and their descriptions. A required leave are the days
        where the person has to take a leave - and this will be an
        indicative/suggestion to the planner.
    """

    name : str
    cycle : AnyCycle = AnyCycle(
        s = MonthDayConstruct(day = 1, month = 1),
        e = MonthDayConstruct(day = 31, month = 12)
    )

    # now we can define the leaves for the person
    comp_week_off : CompWeeklyLeave = CompWeeklyLeave()
    custom_leaves : list[CustomLeaves] = list()

    # additional assigned holidays
    additional_holidays : list[HolidayConstruct] = list()

    # required leave on days
    required_leaves : list[HolidayConstruct] = list()
