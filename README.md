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

## Build

```bash
jekyll serve    # local preview at http://localhost:4000
```

GitHub Pages builds and deploys automatically on push to `main`.
