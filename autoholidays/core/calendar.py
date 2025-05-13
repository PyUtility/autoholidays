# -*- encoding: utf-8 -*-

"""
A construct to represent calendar information, this will be used to
calculate and define the planning period and to identify different
holidays - paid, regional, etc.
"""

from enum import Enum

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
