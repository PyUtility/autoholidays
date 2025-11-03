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
    dates = [ date.toordinal() for date in dates ]

    groups = [[dates[0]]]
    for cur, nxt in zip(dates[:-1], dates[1:]):
        if (nxt - cur) <= 1:
            groups[-1].append(nxt)
        else:
            groups.append([nxt])

    return [
        [ dt.datetime.fromordinal(date) for date in group ]
        for group in groups
    ]
