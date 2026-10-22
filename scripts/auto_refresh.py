#!/usr/bin/env python3
"""Unattended daily refresh: pull the latest figures and publish them.

    python3 scripts/auto_refresh.py            # run (cron does this daily)
    python3 scripts/auto_refresh.py --dry-run  # everything except commit/push

Runs refresh_site.py (live Google rating, ledger floors, full verification)
and, only if Verify PASSes, commits and pushes. Guard rails, because nobody
is watching:

  * It only ever commits AUTO_FILES (the generated Google rating file). If
    anything else in the working tree is modified, it skips the whole run,
    so half-finished manual work is never swept into an automatic commit.
  * It only runs with main checked out, fast-forwards from origin first,
    never force-pushes, and retries a commit a previous run failed to push.
  * Any failure (verify, pull, push) is logged and nothing is published.

Log: ~/.local/state/nyanmeshi-site/refresh.log (LEDGER GAP warnings from
the finance ledger land there too).
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent
AUTO_FILES = {"_data/gbp.yml"}
LOG = Path.home() / ".local" / "state" / "nyanmeshi-site" / "refresh.log"


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"{datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line)
    with LOG.open("a") as f:
        f.write(line + "\n")


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=SITE_DIR, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {(r.stdout + r.stderr).strip()}")
    return r.stdout


def changed_files():
    out = git("status", "--porcelain", "--untracked-files=all")
    return {line[3:].strip() for line in out.splitlines() if line.strip()}


def main():
    dry = "--dry-run" in sys.argv
    branch = git("rev-parse", "--abbrev-ref", "HEAD", check=False).strip()
    if branch != "main":
        log(f"SKIP: checked out on '{branch}', not main; not auto-publishing")
        return 0
    other = changed_files() - AUTO_FILES
    if other:
        log(f"SKIP: uncommitted manual changes ({len(other)} file(s)), not auto-publishing")
        return 0

    try:
        git("pull", "--ff-only", "--quiet")
    except RuntimeError as e:
        log(f"FAIL: {e}")
        return 1

    r = subprocess.run([sys.executable, "scripts/refresh_site.py"], cwd=SITE_DIR,
                       capture_output=True, text=True)
    for line in (r.stdout + r.stderr).splitlines():
        if line.startswith(("wrote ", "  LEDGER GAP", "FAIL", "!!", "note:")):
            log("  " + line.strip())
    if r.returncode != 0:
        log("FAIL: refresh/verify failed, nothing published")
        return 1

    changes = changed_files()
    if not changes:
        # A previous run may have committed but failed to push (network
        # blip): retry so that commit doesn't sit stranded locally.
        ahead = git("rev-list", "--count", "@{u}..HEAD", check=False).strip()
        if ahead.isdigit() and int(ahead) > 0 and not dry:
            try:
                git("push", "--quiet")
            except RuntimeError as e:
                log(f"FAIL: retrying unpushed commit: {e}")
                return 1
            log(f"PUBLISHED: {ahead} previously unpushed commit(s)")
            return 0
        log("OK: site already shows the latest figures")
        return 0
    if not changes <= AUTO_FILES:
        log(f"FAIL: unexpected changes {sorted(changes - AUTO_FILES)}, nothing published")
        return 1
    if dry:
        log(f"DRY RUN: would publish {sorted(changes)}")
        return 0

    try:
        git("add", *sorted(changes))
        git("commit", "--quiet", "-m", "refresh track record and Google rating")
        git("push", "--quiet")
    except RuntimeError as e:
        log(f"FAIL: {e}")
        return 1
    log(f"PUBLISHED: {sorted(changes)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
