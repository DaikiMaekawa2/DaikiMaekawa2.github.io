#!/usr/bin/env python3
"""Derive the track-record floors in _data/stats.yml from the finance ledger.

    python3 scripts/ledger_stats.py           # report only
    python3 scripts/ledger_stats.py --write   # raise floors in stats.yml

Only aggregate counts derived from PUBLIC fields (event_id, venue_id, start,
end, and the trading dates in daily_sales.csv) are read. No financial
column is ever read and no venue name is printed, so output is safe to paste.

Floors only ever go UP: the ledger starts in 2026, while the site's figures
also cover earlier work, so a ledger total below the current floor never
lowers it.

The ledger can lag behind operations (an event run before its row is added
to events.csv). Trading days in daily_sales.csv that fall outside their
event's date range are reported as LEDGER GAPS so they can be fixed in the
finance repo; they are not counted until then.

Set NYANMESHI_FINANCE_DIR to point at a different finance repo checkout.
"""

import csv
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent
FINANCE_DIR = Path(os.environ.get(
    "NYANMESHI_FINANCE_DIR",
    "/home/common/nyanmeshi_business_materials/nyanmeshi_finance",
))
EVENTS_CSV = FINANCE_DIR / "data" / "events.csv"
SALES_CSV = FINANCE_DIR / "data" / "daily_sales.csv"
STATS_YML = SITE_DIR / "_data" / "stats.yml"

# stats.yml label -> how its floor is derived from the ledger totals
ROUND_TO = {"Stall-days served": 10, "Event venues served": 5}


def ledger_totals(today):
    events = {}
    with open(EVENTS_CSV, newline="") as f:
        for row in csv.DictReader(f):
            try:
                start = date.fromisoformat(row["start"].strip())
                end = date.fromisoformat(row["end"].strip())
            except (KeyError, ValueError):
                continue
            events[row["event_id"].strip()] = (start, end, (row.get("venue_id") or row["event_id"]).strip(),
                                               row["venue_type"].strip())
    started = {k: v for k, v in events.items() if v[0] <= today}
    totals = {
        "Activations staged": len(started),
        "Stall-days served": sum((min(e, today) - s).days + 1 for s, e, _, _ in started.values()),
        "Event venues served": len({v for _, _, v, _ in started.values()}),
    }
    formats = Counter(t for _, _, _, t in started.values())

    gaps = defaultdict(set)
    if SALES_CSV.exists():
        with open(SALES_CSV, newline="") as f:
            for row in csv.DictReader(f):
                d = (row.get("date") or "")[:10]
                ev = (row.get("event_id") or "").strip()
                if not d:
                    continue
                span = events.get(ev)
                if span is None or not (span[0].isoformat() <= d <= span[1].isoformat()):
                    gaps[ev or "(no event_id)"].add(d)
    return totals, formats, gaps


def main():
    if not EVENTS_CSV.exists():
        sys.exit(f"events.csv not found at {EVENTS_CSV} — set NYANMESHI_FINANCE_DIR")
    today = date.today()
    totals, formats, gaps = ledger_totals(today)

    print(f"Ledger totals as of {today.isoformat()} (events started so far):")
    for k, v in totals.items():
        print(f"  {k:<22} {v}")
    print("  by format              " + ", ".join(f"{t} {n}" for t, n in formats.most_common()))

    for ev, ds in sorted(gaps.items()):
        ds = sorted(ds)
        print(f"  LEDGER GAP: {len(ds)} trading day(s) {ds[0]} → {ds[-1]} booked to {ev}, "
              "outside its events.csv dates. Likely a missing event row; fix in the finance repo.")

    text = STATS_YML.read_text()
    changed = []
    print("\nSite floors (_data/stats.yml):")
    for label, step in ROUND_TO.items():
        m = re.search(rf"- value: (\d+)\n(  suffix: [^\n]*\n)  label: {re.escape(label)}\n", text)
        if not m:
            continue
        current = int(m.group(1))
        proposed = max(current, totals[label] // step * step)
        note = f"  -> raise to {proposed}+" if proposed > current else ""
        print(f"  {label:<22} {current}+{note}")
        if proposed > current:
            changed.append((label, current, proposed))
            text = text.replace(m.group(0), m.group(0).replace(f"value: {current}\n", f"value: {proposed}\n", 1), 1)

    if "--write" in sys.argv and changed:
        STATS_YML.write_text(text)
        print("wrote _data/stats.yml: " + ", ".join(f"{l} {a}+ → {b}+" for l, a, b in changed))
    elif "--write" in sys.argv:
        print("stats.yml already current")


if __name__ == "__main__":
    main()
