---
description: Sync the website schedule & map from the finance ledger, verify, and publish
---

Update nyanmeshi.com from the finance ledger. Follow these steps exactly, in order.
The scripts do the hard work — your job is to run them and act on their output.

## 1. Sync the schedule

```bash
python3 scripts/sync_schedule.py
```

This regenerates `_data/schedule.yml` from the finance repo's `events.csv`
(public fields only). Read its output:

- If it prints `MAP: no marker for '<venue>' ...` — a scheduled event is
  missing from the footprint map. Add an entry to `_data/locations.yml`:

  ```yaml
  - name: <venue name>
    lat: <latitude>
    lng: <longitude>
    type: Event Venue   # or "Bank Roadshow"
  ```

  Use coordinates you know to be correct for the venue; if unsure, ask the
  user for them. If the venue is OUTSIDE Singapore, instead add
  `map_skip: true` under that event's id in `_data/schedule_overrides.yml`.

- If a NEW event appears with the default location "Singapore" and no note,
  add editorial copy under its `event_id` in `_data/schedule_overrides.yml`
  (`name`, `name_ja`, `location`, `location_ja`, `note`, `note_ja`), then run
  the script again. Write the Japanese fields too — the site is bilingual.

## 2. Verify

```bash
python3 scripts/check_site.py
```

This builds the site and checks both language pages for confidential terms,
broken links/anchors, missing assets, and schedule drift. It must print
`PASS`. If it prints `FAIL` lines, fix each one and re-run. Never publish
while this fails.

## 3. Publish

Review the diff, then commit and push (GitHub Pages deploys automatically):

```bash
git diff
git add _data/ && git commit -m "update event schedule" && git push
```

Rules:
- This is a PUBLIC repository. Never commit tokens, credentials, financial
  figures (rent, commissions, sales), payee names, or helper/worker names.
  `check_site.py` guards the built pages, but the rule applies to every file.
- Plain commit message, no AI attribution.
- Only `_data/` should normally change in this workflow. If other files
  changed unexpectedly, stop and ask the user before committing.
