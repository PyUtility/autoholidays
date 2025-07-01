# -*- coding: utf-8 -*-
"""
Public API Facade for the ``autoholidays`` Package

This module is the stable, versioned public interface for the entire
``autoholidays`` package. Consumer code should import from here (or
from the top-level package namespace) rather than reaching into
internal sub-modules directly. That separation ensures internal
restructuring - moving classes, renaming files, or splitting modules
- never silently breaks call sites.
"""

from autoholidays.core import *  # noqa: F401, F403

__all__ = [
    "ENUMDays",
    "CreditDays",
    "PlanningCycle",
    "PersonConstruct",
]
