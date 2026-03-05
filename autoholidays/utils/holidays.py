# -*- encoding: utf-8 -*-

"""
A Utility Base Model to define a Holiday
"""

import datetime as dt
from pydantic import Field, BaseModel

class HolidayConstruct(BaseModel):
    date : dt.date
    name : str = None
    priority : int = Field(0, ge = 0, le = 5)
