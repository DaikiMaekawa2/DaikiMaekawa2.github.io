#!/usr/bin/env python3
"""Build the site and verify it is safe and consistent to publish.

    python3 scripts/check_site.py

Checks, on every built page:
  1. No confidential terms. Generic finance words are checked by word
     boundary; specific names (payees, helpers) are loaded AT RUNTIME from
     the private finance repo, so the blocklist itself never appears in
     this public repository. If the private repo is absent, only the
     generic check runs.
  1b. No non-marquee venue names (night markets, malls, markets: their
     venue IDs, names and areas, also loaded at runtime from venues.csv)
     on the home pages or in the content files (_data/, _includes/).
     The circuit is competitive intelligence; marquee credentials
     (department stores, festivals) may be named. Legal pages are exempt:
     they must carry the registered address.
  2. No broken in-page anchors (href="#id" without a matching id).
  3. Every local asset reference (src/href starting with "/") resolves to
     a file in _site/.
  4. hreflang alternates are present on both language pages.
  5. The Google rating/review floor in _data/gbp.yml does not overstate
     the live profile (delegates to sync_gbp.py --check; skipped when the
     marketing repo's snapshot is absent).

Exits 0 and prints PASS when everything holds; otherwise prints each
failure and exits 1.
"""

import csv
import re
import subprocess
import sys
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent
OUT = SITE_DIR / "_site"
PAGES = ["index.html", "ja/index.html"]

# Generic terms only — anything business-specific is derived at runtime.
GENERIC_TERMS = ["rent", "commission", "payee", "salary", "wage", "cogs", "reconcile"]

# Credential patterns that must never appear in this public repository.
SECRET_PATTERN = re.compile(
    r"(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}"
    r"|sk-[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9-]+"
    r"|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY"
    r"|(api[_-]?key|client_secret|password)\s*[:=]\s*['\"][^'\"]{8,})", re.I)

SOURCE_SUFFIXES = {".html", ".yml", ".yaml", ".js", ".css", ".md", ".xml", ".txt", ".json", ".py"}


def private_terms():
    """Names that must never appear on the site, read from the private repo."""
    import os
    finance = Path(os.environ.get(
        "NYANMESHI_FINANCE_DIR",
        "/home/common/nyanmeshi_business_materials/nyanmeshi_finance",
    ))
    terms = set()
    events = finance / "data" / "events.csv"
    if events.exists():
        with open(events, newline="") as f:
            for row in csv.DictReader(f):
                for col in ("rent_payee", "utilities_payee"):
                    v = (row.get(col) or "").strip()
                    if v:
                        terms.add(v)
    workers = finance / "data" / "workers.csv"
    if workers.exists():
        with open(workers, newline="") as f:
            for row in csv.DictReader(f):
                # The CEO is the public contact; everyone else stays private.
                if (row.get("role") or "").strip().upper() == "CEO":
                    continue
                for v in ((row.get("name") or ""), (row.get("worker_id") or "")):
                    v = v.strip()
                    if len(v) >= 4:
                        terms.add(v)
    return terms


# Venue formats that are never named publicly (see CLAUDE.md, Confidentiality).
UNNAMED_VENUE_TYPES = {"pasar malam", "mall", "market"}
CONTENT_DIRS = ("_data/", "_includes/")


def private_venue_terms():
    """Non-marquee venue IDs, names and areas, read from the private repo."""
    import os
    finance = Path(os.environ.get(
        "NYANMESHI_FINANCE_DIR",
        "/home/common/nyanmeshi_business_materials/nyanmeshi_finance",
    ))
    venues = finance / "data" / "venues.csv"
    terms = set()
    if not venues.exists():
        return terms
    with open(venues, newline="") as f:
        for row in csv.DictReader(f):
            if (row.get("venue_type") or "").strip().lower() not in UNNAMED_VENUE_TYPES:
                continue
            for col in ("venue_id", "name", "area"):
                v = re.sub(r"\s*\(.*?\)", "", row.get(col) or "").strip()
                if len(v) >= 3:
                    terms.add(v.lower())
    return terms


def scan_content_for_venues(venue_terms):
    """Content files must not name non-marquee venues."""
    failures = []
    tracked = subprocess.run(["git", "ls-files", *CONTENT_DIRS], cwd=SITE_DIR,
                             capture_output=True, text=True).stdout.splitlines()
    untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", *CONTENT_DIRS],
                               cwd=SITE_DIR, capture_output=True, text=True).stdout.splitlines()
    for rel in tracked + untracked:
        path = SITE_DIR / rel
        if not path.exists():
            continue
        low = path.read_text(errors="ignore").lower()
        if any(t in low for t in venue_terms):
            failures.append(f"{rel}: names a non-marquee venue (not echoed here)")
    return failures


def scan_source_tree(specific):
    """Scan every git-tracked text file for secrets and private terms."""
    failures = []
    tracked = subprocess.run(["git", "ls-files"], cwd=SITE_DIR,
                             capture_output=True, text=True).stdout.splitlines()
    for rel in tracked:
        path = SITE_DIR / rel
        if path.suffix not in SOURCE_SUFFIXES or not path.exists():
            continue
        text = path.read_text(errors="ignore")
        if SECRET_PATTERN.search(text):
            failures.append(f"{rel}: credential-like pattern in source")
        low = text.lower()
        for term in specific:
            if term.lower() in low:
                failures.append(f"{rel}: private term from ledger in source (not echoed here)")
                break
    return failures


def main():
    failures = []

    build = subprocess.run(["jekyll", "build"], cwd=SITE_DIR, capture_output=True, text=True)
    if build.returncode != 0:
        print(build.stdout + build.stderr)
        sys.exit("FAIL: jekyll build failed")

    specific = private_terms()
    if not specific:
        print("note: private finance repo not found — only generic term check runs")

    failures += scan_source_tree(specific)

    # Business counts (venues, stall-days, activations) are never published
    # (owner, Oct 2026); the old ledger-fed stats file must not return.
    if (SITE_DIR / "_data" / "stats.yml").exists():
        failures.append("_data/stats.yml exists: business counts are never published")

    venue_terms = private_venue_terms()
    failures += scan_content_for_venues(venue_terms)

    for page in PAGES:
        path = OUT / page
        if not path.exists():
            failures.append(f"{page}: missing from _site/")
            continue
        html = path.read_text()
        low = html.lower()

        for term in GENERIC_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", low):
                failures.append(f"{page}: generic confidential term '{term}' found")
        for term in specific:
            if term.lower() in low:
                failures.append(f"{page}: private term from ledger found (not echoed here)")
        if re.search(r"stall-days|stall days|屋台営業日|販売会場数|出店国数", low):
            failures.append(f"{page}: publishes a business count (stall-days/venues)")
        if any(t in low for t in venue_terms):
            failures.append(f"{page}: names a non-marquee venue (not echoed here)")

        ids = set(re.findall(r'id="([^"]+)"', html))
        for anchor in set(re.findall(r'href="#([^"]+)"', html)):
            if anchor not in ids:
                failures.append(f"{page}: broken anchor #{anchor}")

        for ref in set(re.findall(r'(?:src|href)="(/[^"]+)"', html)):
            local = ref.split("?")[0].split("#")[0]
            if local.startswith("//"):
                continue
            target = OUT / local.lstrip("/")
            if not target.exists() and not (target / "index.html").exists():
                failures.append(f"{page}: missing local asset {local}")

        if 'hreflang="ja"' not in html or 'hreflang="en"' not in html:
            failures.append(f"{page}: hreflang alternates missing")

        if 'http-equiv="Content-Security-Policy"' not in html:
            failures.append(f"{page}: CSP meta tag missing")
        # non-executable types (application/json, application/ld+json) are fine
        if re.search(r"<script(?![^>]*\bsrc=)(?![^>]*json)", html):
            failures.append(f"{page}: inline executable <script> found — breaks the CSP")

    gbp = subprocess.run(
        [sys.executable, "scripts/sync_gbp.py", "--check"],
        cwd=SITE_DIR, capture_output=True, text=True,
    )
    gbp_out = (gbp.stdout + gbp.stderr).strip()
    if "not found" in gbp_out:
        print("note: marketing repo GBP snapshot not found — rating check skipped")
    elif gbp.returncode != 0:
        failures.append("gbp: " + gbp_out.splitlines()[-1])

    if failures:
        for f in failures:
            print("FAIL:", f)
        sys.exit(1)
    print(f"PASS: {len(PAGES)} pages checked")


if __name__ == "__main__":
    main()
