# -*- encoding: utf-8 -*-

"""
The core algorithms to find the optimal leaves for an user using
the information provided by the user and using minimal Python modules,
thus reducing overheads without compromising performance.

The algorithms defined here are all created to find the best possible
"long weekends" for a given user, where a "long weekend" is defined as
a period of weekly offs immediately followed by a regional holiday.
The function here extends the definition further by considering "long
weekend" as a combination of weekly offs and regional holidays with
minimum number of paid leaves.

For example, consider a ``W`` as weekly off, ``H`` and holiday as
``X`` as a working day, we can calculate long weekends as follows:

.. code-block:: text

    # 0 : Paid Leave Balance is not Deducted due to a Type of Holiday
    # 1 : Paid Leave Balance is Deducted as it is a Working Day

    S M T W T F S  S M T W T F S
    W X X X X X W  W X X X X X W  # CASE: A - Normal Schedule
    0 1 1 1 1 1 0  0 1 1 1 1 1 0  # Required Leaves = 10

    S M T W T F S  S M T W T F S
    W X X X X H W  W X X X X X W  # CASE: B(1) - Long Weekends
    0 1 1 1 1 0 0  0 1 1 1 1 1 0  # Required Leaves = 9

    S M T W T F S  S M T W T F S
    W X X H X X W  W X X X X X W  # CASE: B(2) - Not a Long Weekend
    0 1 1 0 1 1 0  0 1 1 1 1 1 0  # Required Leaves = 9

By traditional "long weekend" definition, we will consider CASE: B(1)
as a long weekend while CASE: B(2) is not. However, if we closely
look into the list, and put some constraint like only take two leave,
then considering ``-`` as a working day, we try to find the best
possible combination of long weekends as follows:

.. code-block:: text

    S M T W T F S  S M T W T F S
    W X X H X X W  W X X X X X W  # CASE: B(2) - (Adj.) Long Weekends
    - - - 0 1 1 0  0 - - - - - -  # Required Leaves = 2, Holidays = 5

Thus, both CASE: B(1) and CASE: B(2) are considered as long weekends,
as they provide the same number of holidays with the same number of
paid required leaves.
"""

import inspect
import datetime as dt

from typing import get_args, get_origin
from typing import List, Protocol, Dict, Any

class AHAlgorithms(Protocol):
    def __call__(self, dates : List[dt.date]) -> List[List[dt.date]]:
        ...


def register(name : str):
    """
    A function registration decorator that inherits the abstract
    protocol's ``AHAlgorithms.__call__`` method. Returns a function
    that can be used to register a new algorithm.
    """

    registry: Dict[str, AHAlgorithms] = {}

    def validate(value : Any, annotation : Any, name : str) -> None:
        """
        Validate the function signature post call of the decorator, as
        by default Python's type hints are not enforced at runtime.
        """

        args = get_args(annotation)
        origin = get_origin(annotation)

        if origin is list:
            if not isinstance(value, list):
                raise TypeError(
                    f"'{name}' must be a list, "
                    f"got {type(value).__name__!r}"
                )
            if args:
                for i, item in enumerate(value):
                    validate(item, args[0], f"{name}[{i}]")

        else:
            if not isinstance(value, annotation):
                raise TypeError(
                    f"'{name}' must be of Type {annotation.__name__}, "
                    f"got {type(value).__name__!r}"
                )

        return None


    def signature(function : AHAlgorithms) -> AHAlgorithms:
        """
        Inspect the signature, enforce valid signature of any instance
        function with the ``AHAlgorithms`` protocol.
        """

        current = inspect.signature(function)
        expected = inspect.Signature(
            parameters = [
                inspect.Parameter(
                    "dates", inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation = List[dt.date]
                )
            ],
            return_annotation = List[List[dt.date]]
        )

        if current != expected:
            raise TypeError("Invalid Signature for Algorithm")

        return function


    def decorator(function : AHAlgorithms) -> AHAlgorithms:
        validated = signature(function)
        hints = {
            k : v for k, v in
            inspect.signature(validated).parameters.items()
        }


        def wrapper(*args, **kwargs):
            bound = inspect.signature(validated).bind(*args, **kwargs)
            bound.apply_defaults()

            for name, value in bound.arguments.items():
                annotation = hints[name].annotation
                if annotation is not inspect.Parameter.empty:
                    validate(value, annotation, name)

            result = validated(*bound.args, **bound.kwargs)

            return_annotation = inspect.signature(
                validated
            ).return_annotation

            if return_annotation is not inspect.Parameter.empty:
                validate(result, return_annotation, "return value")

            return result

        registry[name] = wrapper
        return wrapper


    return decorator
