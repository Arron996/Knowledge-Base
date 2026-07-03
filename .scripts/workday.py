#!/usr/bin/env python3
"""Workday helpers: skip weekends and CN public holidays (incl.调休)."""

from __future__ import annotations

import argparse
from datetime import date, timedelta

try:
    from chinese_calendar import is_workday as _cn_is_workday

    def is_workday(d: date) -> bool:
        return bool(_cn_is_workday(d))

except ImportError:

    def is_workday(d: date) -> bool:
        return d.weekday() < 5


def prev_workday(from_date: date) -> date:
    """Last workday strictly before from_date."""
    d = from_date - timedelta(days=1)
    while not is_workday(d):
        d -= timedelta(days=1)
    return d


def week_workdays_through(anchor: date) -> list[date]:
    """ISO week Mon..anchor (inclusive), workdays only."""
    monday = anchor - timedelta(days=anchor.weekday())
    days: list[date] = []
    d = monday
    while d <= anchor:
        if is_workday(d):
            days.append(d)
        d += timedelta(days=1)
    return days


def main() -> None:
    parser = argparse.ArgumentParser(description="Workday calendar helpers")
    parser.add_argument("--prev", metavar="DATE", help="Previous workday before DATE (YYYY-MM-DD)")
    parser.add_argument("--is-workday", metavar="DATE", help="Print true/false for DATE")
    args = parser.parse_args()

    if args.prev:
        d = date.fromisoformat(args.prev)
        print(prev_workday(d).isoformat())
    elif args.is_workday:
        d = date.fromisoformat(args.is_workday)
        print("true" if is_workday(d) else "false")
    else:
        parser.print_help()
        raise SystemExit(1)


if __name__ == "__main__":
    main()
