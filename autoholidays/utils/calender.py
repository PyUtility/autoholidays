# -*- encoding: utf-8 -*-

"""
Utility Calender Function for Auto-Holidays Module

The calender is a special utility function and not to be confused with
the :mod:`calender` which have a different functionality. The defined
objects may/maynot be directly related to the python in-built
module which deals with calender days and calculations around it.
"""

import datetime as dt

from enum import Enum
from pydantic import Field, BaseModel, computed_field

from autoholidays.errors import InvalidDayNum

class ENUMDays(Enum):
    """
    ENUM for the Days of the Week

    The days of the week is zero-indexed and starts from Monday. The
    values are in-sync with the :mod:`datetime` module in Python, thus
    providing backward compatibility.

    .. code-block:: python

        ENUMDays.SUNDAY # get the object for Sunday

        # to get/search for a particular day, use:
        print(ENUMDays(2))
        >> ENUMDays.WEDNESDAY

    The enum provides to distinct useful methods - :attr:`.name` to
    get the name defined in the enum and :attr:`.value` to get the
    value associated with the enum.

    Once the enum is extended to other pydantic base models, we can
    directly use the value without field validation as the value is
    already validated by the enum.
    """

    MONDAY    = 0
    TUESDAY   = 1
    WEDNESDAY = 2
    THURSDAY  = 3
    FRIDAY    = 4
    SATURDAY  = 5
    SUNDAY    = 6


    @classmethod
    def __override_error__(cls, value) -> None:
        """
        Raise an Custom Error if the Value is not in Range
        """

        raise InvalidDayNum(
            "`%r` is not a Valid `%s`. Valid Values: `%s`" % (
                value,
                cls.__name__,
                ", ".join([str(day.value) for day in cls])
            )
        )


class MonthDayConstruct(BaseModel):
    """
    Create a Month-Day Constructor for Various Usages

    The construct allows to define the day and month without the year
    value. Thus, the class can be dynamically unpacked to the module
    :mod:`datetime` to iterate over a range of dynamic year value.
    """

    day : int = Field(ge = 1, le = 31)
    month : int = Field(ge = 1, le = 12)


class AnyCycle(BaseModel):
    """
    Create a Cycle Base Validation Model
    """

    s : MonthDayConstruct
    e : MonthDayConstruct

    year : int = dt.date.today().year


    @computed_field
    @property
    def start(self) -> dt.date:
        return dt.date(self.year, self.s.month, self.s.day)


    @computed_field
    @property
    def end(self) -> dt.date:
        return dt.date(
            self.year if self.s.month <= self.e.month else self.year + 1,
            self.e.month, self.e.day
        )

    @computed_field
    @property
    def duration(self) -> int:
        return (self.end - self.start).days
