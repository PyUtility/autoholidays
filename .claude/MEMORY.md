# Project Memory: autoholidays

## Project Identity
- Package: `autoholidays` v0.0.2.dev1 (Development/Planning stage)
- Python 3.12+, MIT License, published to PyPI
- Single maintainer: @ZenithClown
- Active branch convention: `patch/<description>-gh#<issue>`

## Key File Paths
- `autoholidays/core.py` — Main algorithm (`AutoHoliday` class, ~266 lines)
- `autoholidays/calendar.py` — `ENUMDays`, `CreditDays`, `PlanningCycle`
- `autoholidays/person.py` — `PersonConstruct` Pydantic model
- `autoholidays/__init__.py` — Exports `AutoHoliday`, sets `__version__`
- `.flake8` — max-line-length=88, ignores E203/E221/E251/E261

## Architecture
Dependency chain: `calendar.py ← person.py ← core.py ← __init__.py`

`AutoHoliday.plan()` algorithm:
1. Build collective union of all persons' holiday ordinals
2. For each collective holiday: walkLeft/walkRight to find the off-day block boundary
3. Non-holiday days inside blocks → candidate leave days (per person)
4. Apply credit balance chronologically; approve only when balance > 0
5. Return approved dates per person

## Critical Bugs (as of March 2026)
1. `PersonConstruct.opening` balance is NEVER applied in `plan()` — silently ignored
2. `PersonConstruct.requiredLeaves` is NEVER used in `plan()` — silently ignored
3. `collectiveHolidays` is a sorted list but checked with `in` (O(n) per lookup) — should be a `set`
4. `__update_holidays__` does not deduplicate weekoffs with existing holidays
5. `extendedWeekends([])` crashes with IndexError on empty input

## Resolved Issues
- `.flake8` previously referenced non-existent `autoholidays/api.py` — that entry was removed from `per-file-ignores`

## User Preferences
- Always use the Python Code Formatting Skill before writing/editing Python files
- Follow Flake8 config: max 88 chars, ignore E203/E221/E251/E261
- No test suite exists yet — tests are a major improvement area
