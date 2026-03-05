# -*- encoding: utf-8 -*-

"""
An Utility ENUM & Pydantic Base Model for Leaves

The module defines a standard way to define a leave for an user. The
different functionality includes:

    * :class:`CompWeeklyLeave` - a process to define compulsary weekly
        leaves for an user. The defination allows to fetch the days
        which are holidays and in sync with other leaves can calculate
        long weekends.

The module uses the :mod:`pydantic` and :mod:`enum` for a structured
defination of leaves which can be extended to the API module.
"""

from pydantic import (
    Field,
    BaseModel,
    computed_field,
    field_validator
)

from autoholidays.utils.calender import ENUMDays, MonthDayConstruct


class CompWeeklyLeave(BaseModel):
    """
    Compulsory Weekly-Off Leave Schema/Construct Definition

    The weekly leave schema defines the days of the week when a user
    has a holiday. The days are typically Sunday and Saturday, and
    is same as the weekly off days for an organization.

    :type  days: set[ENUMDays]
    :param days: A set of :class:`ENUMDays` enum values representing
        the days of the week when a user has a holiday. The days are
        typically Sunday and Saturday, default value.

    :type  D#: tuple[bool]
    :param D#: A tuple of boolean values representing each week of a
        month if the weekly-off is available. For example, an user may
        have every alternate Saturday as a weekly-off, so we can
        set a tuple like :attr:`(True, False, True, False, True)`
        denoting 1st-, 3rd- and 5th-week of the month as weekly-off.
        Defaults to all true, that is everyday is considered.

    Example Usage
    -------------

    The weeklc construct is significantly useful to find if a particular
    day is a weekly-off day or not. For example:

    .. code-block:: python

        import datetime as dt
        import autoholidays as ah

        # let's define a day to simulate the leave
        cur_date = dt.date(2025, 5, 4)

        # let's define the weekly leave construct with defaults
        weekly = ah.utils.CompWeeklyLeave()
        dayset = set([day.value for day in weekly.days])

        # check for each day if it is a weekly-off day or not
        print(f"Weekly Off: {cur_date.weekday() in dayset}")
        >> Weekly Off: True

    To set an custom value for a user's compulsory weekly off, use
    the set dictionary expansion like:

    .. code-block:: python

        # setting values by using the enum name property
        weekly = ah.utils.CompWeeklyLeave(days={
            ah.utils.ENUMDays.SUNDAY
        })

        # setting values by using the enum value property
        weekly = ah.utils.CompWeeklyLeave(days = {
            ah.utils.ENUMDays(6)
        })

    Leave Days Calculation
    ----------------------

    The leave days considers the days of a week and calculates the
    required number of leaves to be availaed. The weekly construct now
    can be used to calculate the number of leaves excluding the weekly
    off days.

    .. code-block:: text

        S M T W T F S
        0 1 2 3 4 5 6
        0 1 1 1 1 1 0 # number of leaves required

    Considering the default weekly-off days, the number of leaves to
    be availed is 5 (Monday to Friday), excluding the weekly-off days.

    D# Naming Convention
    -------------------

    The D# naming convention is used to number the days for the ENUM
    :class:`ENUMDays` representing a valid day. The convention is used
    as :mod:`pydantic` does not allow (?) use of integer naming.

    The calander or related class should be able to handle the value
    :attr:`D#` by converting the name like:

    .. code-block:: python

        int("D#".replace("D", ""))

    Alternatively, the class can directly call the value of :attr:`D#`
    for a particular mapping ENUM class (todo).
    """

    days : set[ENUMDays] = {
        ENUMDays.SUNDAY,
        ENUMDays.SATURDAY
    }

    # for each week for a day <int("D#".replace("D", ""))> check
    # if the weekly off is valid, example every alternate Saturday
    D0 : tuple[bool] = Field(
        tuple([True] * 5),
        min_length = 5, # total 5 weeks in a month
        max_length = 5  # do not allow data leakage/force entry
    )
    D1 : tuple[bool] = Field(
        tuple([True] * 5),
        min_length = 5, # total 5 weeks in a month
        max_length = 5  # do not allow data leakage/force entry
    )
    D2 : tuple[bool] = Field(
        tuple([True] * 5),
        min_length = 5, # total 5 weeks in a month
        max_length = 5  # do not allow data leakage/force entry
    )
    D3 : tuple[bool] = Field(
        tuple([True] * 5),
        min_length = 5, # total 5 weeks in a month
        max_length = 5  # do not allow data leakage/force entry
    )
    D4 : tuple[bool] = Field(
        tuple([True] * 5),
        min_length = 5, # total 5 weeks in a month
        max_length = 5  # do not allow data leakage/force entry
    )
    D5 : tuple[bool] = Field(
        tuple([True] * 5),
        min_length = 5, # total 5 weeks in a month
        max_length = 5  # do not allow data leakage/force entry
    )
    D6 : tuple[bool] = Field(
        tuple([True] * 5),
        min_length = 5, # total 5 weeks in a month
        max_length = 5  # do not allow data leakage/force entry
    )


    @computed_field
    @property
    def day_values(self) -> list[int]:
        return [day.value for day in list(self.days)]


class LRBoundary(BaseModel):
    """
    Create a Leave Range (LR) Boundary for Various Usages
    """

    min_value : int = Field(0, ge = 0)
    max_value : int = Field(float("inf"), ge = 0)


class CustomLeaveConstraint(BaseModel):
    """
    Allow to Put a Constraint on the Custom Leave Days
    
    The constraint is a advanced usage, that helps to put limitations
    on the custom leave days. For example, many organization do not
    allow to take a leave on a particular day of the week, or a
    particular day of the month. Another example of a constraint
    could be that an organization only not allow to take a particular
    leave n-times a year also maybe limiting the number of days.

    :type  limit_days: set[int]
    :param limit_days: A set of integers representing the days of the
        week where the user is not allowed to take a leave. Defaults
        to None (unconstrined).

    :type  avail_limit: tuple[int]
    :param avail_limit: A tuple of two integers representing the
        minimum and maximum number of days the user can take a leave.
        Defaults to (0, float("inf")) (unconstrained).

    :type  avail_limit_per_cycle: tuple[int]
    :param avail_limit_per_cycle: A tuple of two integers
        representing the minimum and maximum number of days the user
        can take a leave in a cycle. Defaults to (0, float("inf"))
        (unconstrained).

    :type  limit_to_dates: set[MonthDayConstruct]
    :param limit_to_dates: A set of dates where the leave is applicable,
        for example in case of an optional holiday which must be the
        same as a public holiday for the country.
    """

    limit_days : set[ENUMDays] = set()

    # allow to put a boundary of leave, like PL >= 4 days at a time
    # or, PL can be applied only twice a year (or a cycle)
    avail_limit : LRBoundary = LRBoundary()
    avail_limit_per_cycle : LRBoundary = LRBoundary()

    # only valid for the a set of days
    limit_to_dates : set[MonthDayConstruct] = set()


class CustomLeaves(BaseModel):
    """
    A Custom Leaves Schema Base Model Construct Definition

    A custom leave is any type of a named leave that a user can take,
    based on the organization policy. Various attributes are associated
    with a leave giving the flexibility of dynamic calculation and
    advanced usages like constraints, etc.

    :type  name: str
    :param name: A string representing the name of the custom leave.
        The name should be a valid string and should not be empty.

    :type  max_balance: int
    :param max_balance: The maximum balance of the leave on for the
        given cycle. Defaults to float("inf"), i.e., no limit.

    :type  n_credit_md: list[MonthDayConstruct]
    :param n_credit_md: A list of :class:`MonthDayConstruct` objects
        representing the credit days for the leave. Defaults to
        [MonthDayConstruct(day = 1, month = 1)].

    :type  n_expiry_md: list[MonthDayConstruct]
    :param n_expiry_md: A list of :class:`MonthDayConstruct` objects
        representing the expiry days for the leave. Defaults to
        [MonthDayConstruct(day = 31, month = 12)].

    :type  n_credit_balance: list[int]
    :param n_credit_balance: A list of integers representing the credit
        balance for each credit day. Defaults to [24], i.e., 24 leaves
        to be credited on dt.date(year, 1, 1).

    :type  carry_forward_balance: int
    :param carry_forward_balance: The attribute is applicable for
        leaves that can be carry forwarded to the next cycle, else
        ignored. Defaults to 0. The number represents the amount of
        leaves an user wish to carry forward to the next cycle. This
        attribute is particularly helpful in case of multi-cycle or
        over-lapping cycle leaves.

    :type  constraints: CustomLeaveConstraint
    :param constraints: A :class:`CustomLeaveConstraint` object which
        provides advanced capabilities to plan leave. Check the parent
        class for default values.

    Carry Forward Leaves
    --------------------

    The carry forward leaves maybe useful when a user plans for more
    than one cycle, or there is an overlapping cycle between more than
    one user in planing cycle.

    .. code-block:: text

        PERSON A : Leave Cycle = dt.date(year, 1, 1) to dt.date(year, 12, 31)
        PERSON B : Leave Cycle = dt.date(year, 4, 1) to dt.date(year + 1, 3, 31)

    We can observe that there is an overlapping cycle for the two user
    when comparing two leave different leave cycle. Thus, if we are
    planning for the period - we may want to preserve the carry
    forward leaves to make a better planning.
    """

    name : str

    # number of max. leave balance that can be accumulated in a cycle
    max_balance : int = Field(float("inf"), ge = 0)

    # credit and expiry dates, dt.date object only
    n_credit_md : list[MonthDayConstruct] = [MonthDayConstruct(day = 1, month = 1)]
    n_expiry_md : list[MonthDayConstruct] = [MonthDayConstruct(day = 31, month = 12)]

    # set credit values for each leave credit day
    n_credit_balance : list[int] = Field(
        [24],
        min_length = len(n_credit_md),
        max_length = len(n_credit_md)
    )

    # for leaves with carry forward (cf), add desired cf balance
    carry_forward_balance : int = Field(0, ge = 0)

    # ? advanced usage, add leave constraints, all defaults in class
    constraints : CustomLeaveConstraint = CustomLeaveConstraint()


    @computed_field
    @property
    def shortname(self) -> str:
        """
        A Short Name for the Custom Leave
        
        The short name is an abbreviation of the custom leave name.
        The short name is auto calculated from the custom leave name
        by getting the first letter of each word in the name.
        """

        return "".join([word[0] for word in self.name.split()]).upper()


    @field_validator("n_credit_balance")
    @classmethod
    def __validate_credit_balance__(cls, values : list[int]) -> list[int]:
        assert min(values) >= 0, f"All of {values} must be non-negative"
