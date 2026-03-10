# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`autoholidays` (v0.0.2.dev1) is a Python package that optimally plans leave days by identifying strategic dates that maximize continuous break periods while minimizing leave usage. It uses an "iterative walk" algorithm over a shared planning cycle for one or more persons.

**Python:** 3.12+ | **Key deps:** `pydantic==2.12.5`, `holidays>=0.92` | **License:** MIT

---

## Project `.claude/` Directory

All project-specific Claude configuration lives under [.claude/](.claude/):

| File | Purpose |
|------|---------|
| [.claude/MEMORY.md](.claude/MEMORY.md) | Persistent project memory — read at session start |
| [.claude/agents/python.md](.claude/agents/python.md) | Python coding agent constraints (always apply when editing Python) |
| [.claude/agents/example.md](.claude/agents/example.md) | Reference test case + expected output table for validating `plan()` |

> All project memory and configuration must be stored under `.claude/` in this repository. Do **not** use the global user directory for this project.

---

## Python Coding Rules (from `.claude/agents/python.md`)

When editing any Python file in this project:
- Only update the specific section of code requested — do not modify unrelated sections
- Do not add inline comments unless absolutely necessary or explicitly asked
- Always test and validate using [.claude/agents/example.md](.claude/agents/example.md) as the reference case
- Run code using `venv/Scripts/python.exe` (the project's virtualenv)

---

## Development Commands

```bash
# Install package in editable mode (run from project root)
venv/Scripts/pip install -e .

# Run linting
venv/Scripts/python -m flake8 autoholidays/

# Build distribution
venv/Scripts/python -m build

# Run a quick validation using the reference example
venv/Scripts/python -c "
import holidays, datetime as dt, autoholidays as ah
persons = [
  ah.person.PersonConstruct(
    name='John Doe', holidays=holidays.IN(years=2026),
    creditDays=[
      ah.calendar.CreditDays(name='GL', days=9, date=dt.date(2026, 4, 1)),
      ah.calendar.CreditDays(name='PL', days=21, date=dt.date(2026, 4, 1))
    ]
  ),
  ah.person.PersonConstruct(
    name='Jane Doe', holidays=holidays.IN(years=2026),
    weekoff=[ah.calendar.ENUMDays.SUNDAY],
    creditDays=[
      ah.calendar.CreditDays(name='EL-Q2', days=9, date=dt.date(2026, 4, 1)),
    ]
  )
]
cycle = ah.calendar.PlanningCycle(start=dt.date(2026, 4, 1), final=dt.date(2026, 5, 31))
planner = ah.AutoHoliday(cycle=cycle, persons=persons)
result = planner.plan()
print([len(r) for r in result])  # Expected: [10, 15]
"
```

There is **no formal test suite** — CI only runs Flake8 linting. The reference case in [.claude/agents/example.md](.claude/agents/example.md) is the primary validation tool.

---

## Code Architecture

Strict dependency chain — changes cascade upward:

```
calendar.py  ←  person.py  ←  core.py  ←  __init__.py
```

### [`autoholidays/calendar.py`](autoholidays/calendar.py)
Foundational models:
- `ENUMDays` — `Enum` mapping weekday names to `datetime.weekday()` integers (Mon=0, Sun=6)
- `CreditDays` — Pydantic model: named leave credit of `days > 0` credited on a specific `date`
- `PlanningCycle` — Pydantic model: `start`/`final` date range (inclusive); validates `start <= final`; `allDays` property returns every date in range

### [`autoholidays/person.py`](autoholidays/person.py)
- `PersonConstruct` — Pydantic model: `name`, `holidays` (accepts `Dict[date, str]` from the `holidays` library or `List[date]`), `creditDays`, `requiredLeaves`, `opening` (opening balance), `weekoff` (defaults to Sat+Sun). The `sortedHolidays` validator deduplicates and sorts at construction time.

### [`autoholidays/core.py`](autoholidays/core.py) — Main algorithm
`AutoHoliday(cycle, persons)`:

1. **`__init__`** — calls `__update_holidays__` which merges each person's holidays with their eligible weekly offs (filtered to cycle window), replacing `person.holidays` in-place.
2. **`plan()`** — returns `List[List[dt.date]]` (approved leave dates per person):
   - Converts holidays to ordinals; builds sorted collective union across all persons
   - For each collective holiday: `walkLeft`/`walkRight` finds the full contiguous "off-day block"
   - Working days inside a block → candidate leave days per person (`ideal` dict)
   - Applies credit balance chronologically: balance incremented as `creditDays` dates are crossed; only approves when `balance > 0`; opening balance is **not applied** (known bug)
3. **`extendedWeekends(dates)`** — static; groups a date list into consecutive clusters (ordinal diff ≤ 1) → `Dict[int, List[dt.date]]`
4. **`weekOffs(dates, weekends)`** — static; filters a date list to those matching specified `ENUMDays`

### [`autoholidays/__init__.py`](autoholidays/__init__.py)
Exports `AutoHoliday` and `__version__ = "v0.0.2.dev1"`. The `autoholidays.api` import referenced in comments is **not yet implemented**.

---

## Known Issues and Required Improvements

### Bugs (silent correctness failures)

| # | Issue | Location |
|---|-------|----------|
| 1 | `PersonConstruct.opening` is never added to `balance` in `plan()` | [core.py:150](autoholidays/core.py#L150) |
| 2 | `requiredLeaves` is defined and documented but never consumed | [core.py:plan()](autoholidays/core.py#L50) |
| 3 | `collectiveHolidays` is a `list` used with `in` (O(n) per walk step, should be `set`) | [core.py:81,107](autoholidays/core.py#L81) |
| 4 | `__update_holidays__` concatenates weekoffs without deduplication | [core.py:258-263](autoholidays/core.py#L258) |
| 5 | `extendedWeekends([])` raises `IndexError` on empty input | [core.py:204](autoholidays/core.py#L204) |

### Code Quality

| # | Issue | Location |
|---|-------|----------|
| 7 | Typo: `"resilt"` should be `"result"` | [core.py:136](autoholidays/core.py#L136) |
| 8 | No test suite — only linting CI exists | `.github/workflows/linting.yml` |

### Optimization Opportunities

| # | Opportunity |
|---|-------------|
| 9 | Use `set` for `collectiveHolidays` for O(1) membership checks in walk loops |
| 10 | `PlanningCycle.allDays` is recomputed on every property access — no caching |
| 11 | No logging — add `logging` calls at block detection and balance update points |

### Missing Features (documented but unimplemented)

| # | Feature |
|---|---------|
| 12 | `requiredLeaves` constraint — algorithm should "club" these days with holidays |
| 13 | Multi-person coordination — persons are planned independently after collective union |

---

## Linting Configuration

Flake8 max line length: **88**. Ignored globally: `E203`, `E221`, `E251`, `E261`.
`__init__.py` additionally ignores: `F401`, `F403`, `F405`.

Always apply the **Python Code Formatting Skill** (`python-code-format`) when creating or modifying any Python file.
