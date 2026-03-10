# -*- encoding: utf-8 -*-

"""
To construct an efficient holiday planner, a set of calendar methods
are defined which is used as an utility functions to plan leaves.
"""

import datetime as dt

from enum import Enum
from typing import List

from pydantic import BaseModel, Field, model_validator

class ENUMDays(Enum):
    """
    The day of the week is always zero-indexed and starts from Monday,
    which provides a backward compatibility with :mod:`datetime`
    module. Simple usages are as follows:

    .. code-block:: python

        ENUMDays.SUNDAY # get the object representing Sunday

        # search is inbuilt, can be used as:
        print(ENUMDays(2))
        >> ENUMDays.WEDNESDAY

    The field is auto-validated using the ``enum.Enum`` class and
    raises value error when out of range.
    """

    MONDAY    = 0
    TUESDAY   = 1
    WEDNESDAY = 2
    THURSDAY  = 3
    FRIDAY    = 4
    SATURDAY  = 5
    SUNDAY    = 6


class CreditDays(BaseModel):
    """
    A :mod:`pydantic` base model to define leave credit days for
    the planning cycle. The credit days can then be passed to the
    :class:`PersonConstruct` class as a list of credit days, thus
    allowing arbitrary numbers of credit day types to be passed.
    """

    name : str = Field(..., description = "Name/Type of Leave")
    days : int = Field(..., gt = 0, description = "Number of Days")
    date : dt.date = Field(..., description = "Date of Leave Credit")


class PlanningCycle(BaseModel):
    """
    A default construct to represent a planning cycle. The planning
    cycle construct defines a start and final date and is fixed for
    all the members during a optimal holiday run. The construct is
    defined such that any length of period can be provided to find the
    best optimal holiday for the user(s).

    :type  start, final: dt.date
    :param start, final: First and last date (inclusive) for the
        planning cycle.
    """

    start : dt.date
    final : dt.date


    @model_validator(mode = "after")
    def validateCycle(self) -> "PlanningCycle":
        """
        Validate the planning cycle and raise an error if the final
        date is before the start date.
        """

        assert self.start <= self.final, \
            "Start Date ≥ Final Date is Invalid"

        return self


    @property
    def allDays(self) -> List[dt.date]:
        """
        Returns a list of all calendar dates between the start and
        the final date, i.e., the planning cycle.
        """

        return [
            self.start + dt.timedelta(days = days)
            for days in range((self.final - self.start).days + 1)
        ]


    @property
    def startOridinal(self) -> int:
        return self.start.toordinal()


    @property
    def finalOridinal(self) -> int:
        return self.final.toordinal()


    @property
    def allDaysOridinal(self) -> List[int]:
        return [day.toordinal() for day in self.allDays]
