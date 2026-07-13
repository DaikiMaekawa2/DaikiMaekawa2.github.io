# nyanmeshi.com

Bilingual (EN / 日本語) Jekyll site for Nyanmeshi JAPAN PTE. LTD., hosted on
GitHub Pages.

## Layout

```
_layouts/default.html      head, nav, footer (language-aware)
_includes/sections.html    all page sections, shared by both languages
index.html, ja/index.html  thin per-language wrappers
_data/                     all editable content (YAML)
  i18n.yml                 UI strings per language
  schedule.yml             GENERATED — do not edit by hand
  schedule_overrides.yml   editorial copy for schedule cards
  menu.yml, timeline.yml, gallery.yml, stats.yml, locations.yml
assets/css, assets/js      styles and scripts
assets/img                 site images (originals/ holds unused sources)
scripts/                   sync + verification tooling
```

## Updating content

Most content is plain YAML in `_data/` — edit, build, push. English fields
have `*_ja` counterparts for the Japanese page; fill both.

The event schedule is generated from an internal ledger:

```bash
python3 scripts/sync_schedule.py   # regenerate _data/schedule.yml
python3 scripts/check_site.py     # build + verify (must print PASS)
```

In Claude Code, `/sync-site` runs this whole workflow.

## Analytics

The site ships with GA4 (Google Analytics 4, free) wiring that is off by
default. To switch it on:

1. Create a GA4 property at [analytics.google.com](https://analytics.google.com)
   for `nyanmeshi.com` and copy its Measurement ID (`G-XXXXXXXXXX`).
2. Set `ga4_measurement_id` in `_config.yml` to that ID.
3. Run `python3 scripts/check_site.py` — it rebuilds the site, which appends
   the GA4 script origins to the CSP meta tag only now that the ID is set.
4. Push. UTM parameters (`utm_source`, `utm_medium`, `utm_campaign`, …) on
   incoming links are picked up automatically by GA4's default campaign
   tracking — no extra code needed.

CTA clicks (`data-cta="book_whatsapp"` / `"book_email"` in the Book Us
section) fire a GA4 `cta_click` event once analytics is live; see
`assets/js/analytics.js`.

## Search Console

Verify the property at [search.google.com/search-console](https://search.google.com/search-console)
either via the DNS TXT method (no code change here) or the HTML meta tag
method — if you use the meta tag, set `google_site_verification` in
`_config.yml` to the code Search Console gives you, then submit
`https://nyanmeshi.com/sitemap.xml`.

## Build

```bash
jekyll serve    # local preview at http://localhost:4000
```

GitHub Pages builds and deploys automatically on push to `main`.
