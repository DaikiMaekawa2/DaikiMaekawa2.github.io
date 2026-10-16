---
description: Pull the latest Google reviews and track record into the site, verify, and publish
---

One command refreshes every live figure on nyanmeshi.com. Run it, read the
output, publish. The site is evergreen (no schedule, no map), so this is
never urgent: run it whenever the owner wants the latest numbers up.

## 1. Refresh

```bash
python3 scripts/refresh_site.py
```

It runs, in order:
- **Google reviews**: live rating + review-count floor via the marketing
  repo's GBP API client (falls back to its daily snapshot) → `_data/gbp.yml`
- **Track record**: activations, stall-days, venues from the finance
  ledger → `_data/stats.yml`. Floors only ever go up.
- **Verify**: `check_site.py` (confidential terms, anchors, assets, CSP,
  rating never overstated). Must print `PASS`.

Relay to the owner:
- What changed (rating, review floor, any raised stat).
- Any `LEDGER GAP` line: the finance ledger is behind (e.g. an event run
  without its events.csv row). Tell the owner; don't fix the finance repo
  without asking.
- If the step output shows a strong new 4-5★ review not yet quoted, offer
  to add it to `_data/reviews.yml` (mask the name as first letter + x's,
  write `quote_ja`, keep the total a multiple of 3). Never auto-publish
  quotes.

If any step fails, fix it and rerun. Never publish while Verify fails.

## 2. Publish

If `_data/` changed and Verify passed:

```bash
git add _data/ && git commit -m "refresh track record and Google rating" && git push
```

Rules:
- PUBLIC repository. Never commit tokens, credentials, financial figures,
  payee names, or worker names. GBP performance metrics (impressions,
  clicks) stay internal.
- Plain commit message, no AI attribution.
- Only `_data/` should change in this workflow. If other files changed,
  stop and ask before committing.
