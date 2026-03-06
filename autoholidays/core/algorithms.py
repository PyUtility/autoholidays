# -*- encoding: utf-8 -*-

"""
Actual algorithm definitions for calculation of planned leaves that
maximizes the leaves most efficiently.
"""

import datetime as dt

from typing import List
from autoholidays.core.signature import register

@register("extendedWeekends")
def extendedWeekends(dates : List[dt.date]) -> List[List[dt.date]]:
    """
    Given the holiday list, iteratively calculates the difference b/w
    each holiday and returns the list of extended weekend. An extended
    weekend is one where there is an immediate public holiday after
    a scheduled weekly off for a person.

    :type  dates: List[dt.date]
    :param dates: List of holidays (weekly off, public holidays, and
        any other types of entitlement) for a person.

    Return Values
    -------------

    :rtype:  List[List[dt.date]]
    :return: An iterable list of consecutive dates where each is one
        valid long weekend.
    
    Example of the functions return statement:

    .. code-block:: python

        [[2026-01-01], [2026-01-03, 2026-01-04], ...]

    The extended weekend can be used in further functions to find an
    optimal leave pattern over the planning year.
    """

    dates = [ date.toordinal() for date in dates ]

    groups = [[dates[0]]]
    for cur, nxt in zip(dates[:-1], dates[1:]):
        if (nxt - cur) <= 1:
            groups[-1].append(nxt)
        else:
            groups.append([nxt])

    return [
        [
            dt.datetime.fromordinal(date).date() for date in group
        ] for group in groups
    ]
