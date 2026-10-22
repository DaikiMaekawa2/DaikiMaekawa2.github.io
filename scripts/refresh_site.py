#!/usr/bin/env python3
"""One-shot refresh of every live figure on the site, then verify.

    python3 scripts/refresh_site.py

  1. sync_gbp.py            live Google rating + review floor -> _data/gbp.yml
  2. check_site.py          build + verify both pages (must PASS)

Business counts (venues, stall-days) are deliberately never published
(owner, Oct 2026), so nothing here reads the finance ledger.

Ends with the list of changed files. Publishing is left to the caller
(/sync-site commits and pushes when this exits 0).
"""

import subprocess
import sys
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent
STEPS = [
    ("Google reviews", ["scripts/sync_gbp.py"]),
    ("Verify", ["scripts/check_site.py"]),
]


def main():
    ok = True
    for title, cmd in STEPS:
        print(f"\n== {title} ==", flush=True)
        r = subprocess.run([sys.executable, *cmd], cwd=SITE_DIR)
        if r.returncode != 0:
            ok = False
            print(f"!! {title} step failed (exit {r.returncode})")
            if title == "Verify":
                break

    print("\n== Changed ==")
    diff = subprocess.run(["git", "status", "--short", "_data/"], cwd=SITE_DIR,
                          capture_output=True, text=True).stdout.strip()
    print(diff or "nothing: the site already reflects the latest data")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
