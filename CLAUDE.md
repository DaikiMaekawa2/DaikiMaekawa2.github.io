# Nyanmeshi JAPAN — Site Instructions

## Code Search
Always use `mcp__code-index__search_code_advanced` and `mcp__code-index__find_files` for any code searches. Never use grep or find for code lookups — they waste tokens.

## Commits
No Claude or Anthropic attribution in commit messages. Write commit messages as plain human-authored descriptions.

## Multi-Role Review Standard
When reviewing or improving this site, assess from all relevant perspectives before making changes:

**Web Designer**
- Visual hierarchy, whitespace, spacing rhythm
- Typography consistency (font sizes, weights, letter-spacing)
- Color usage against the brand palette (`--brand-red`, `--brand-red-dark`, `--ink-black`, `--charcoal`)
- Mobile layout and touch UX
- Section padding consistency across the page flow

**Code Reviewer**
- Duplicate or conflicting meta tags
- Broken anchor links (`href="#id"` with no matching element)
- Missing `loading="lazy"` on non-critical images
- Missing `rel="noopener noreferrer"` on `target="_blank"` links
- `var` usage — prefer `const`/`let`
- Semantic HTML (`<main>`, `<header>`, `<section>`, `<nav>` used correctly)
- CLS risk: images without `width`/`height` attributes

**Web Developer**
- Performance: preconnect hints for external fonts/CDNs, lazy loading
- Accessibility: ARIA labels on icon-only links, `aria-expanded` on toggles, `<main>` landmark
- Progressive enhancement: IntersectionObserver for scroll animations, passive event listeners
- SEO: structured data (JSON-LD), canonical URL, absolute OG image URLs

**Copywriter**
- Grammar and hyphenation (e.g. "Singapore-based", not "Singapore based")
- Clarity and specificity of trust signals (prefer concrete numbers over vague labels)
- Consistency in Japanese term usage (Matsuri, Omotenashi — always italicised)
- No em dashes in site copy (owner, Jul 2026): never "—" mid-sentence in EN and never "——"/"—" in JA on any rendered page; it reads as AI-generated. Use commas, a colon, or a full stop instead; "·" is fine as a separator in titles/type labels. En dashes in date ranges ("12 – 24 August") are fine. Code comments and repo docs are exempt
- Footprint/achievement claims state only achieved or firmly scheduled facts with dates, e.g. "across Singapore and, since August 2026, in Malaysia"; applies to EN and JA equally. Per owner directive (Jul 2026), "Southeast Asia" may appear as directional market framing in the supplier pitch (e.g. 「シンガポールから東南アジアへ」, "gateway to Southeast Asia") — but never as a claim of operations across the region (no "across Southeast Asia" / 「東南アジア全域へ」)
- Dual-audience positioning (owner, Jul 2026): the two language pages pitch different partners and are NOT translations of each other in hero/story/expertise/CTA. EN targets event organizers and venue managers — why us: crowd-pulling track record, SFA compliance, turnkey operations. JA targets Japanese food suppliers and brands — why us: proven local sales force (販売実績), Singapore→SEA market access, Japanese-language local team. Shared facts (dates, venue names, stat values) stay identical across languages

## Site Structure (Jekyll, bilingual EN/JA)
- `_layouts/default.html` — head, nav, footer; `_includes/sections.html` — all page sections, shared by both languages
- `index.html` (lang: en) and `ja/index.html` (lang: ja, permalink /ja/) are thin wrappers; an EN/日本語 toggle sits in the nav
- `_data/i18n.yml` — UI strings per language; content data files carry `*_ja` fields next to English ones (fallback is English)
- `_data/*.yml` — all editable content: `timeline.yml`, `menu.yml`, `gallery.yml`, `stats.yml`
- Headings/body use Montserrat (+ Noto Sans JP for Japanese); do not introduce serif/display fonts — the owner prefers the original Montserrat look
- `assets/css/style.css`, `assets/js/main.js`; images live in `assets/img/` (unused source photos in `assets/img/originals/`) — keep the root directory free of media files
- Build locally with `jekyll build` / preview with `jekyll serve`; GitHub Pages builds on push
- When adding content, always fill both the English field and its `*_ja` counterpart

## Evergreen Content — no live schedule
The site deliberately does NOT publish current or upcoming events (owner, Oct 2026): keeping a live schedule fresh was too costly, and a stale one hurts credibility. "Where's the stall this week?" is answered by Instagram (the Find Us band links there). Keep every claim evergreen so the site never needs a deadline-driven update:
- Stats are floors ("170+") with no year in the label; floors only go up
- Google rating/count are never hand-typed: `scripts/sync_gbp.py` generates `_data/gbp.yml` via the marketing repo's GBP API client (live pull, daily snapshot as fallback; no credentials in this repo) (rating to one decimal, count as a floor like "20+"); `check_site.py` fails if the site overstates the live profile. GBP performance metrics (impressions, clicks) stay internal
- Milestones are dated past facts ("since August 2026", "in August 2026"), never future tense ("from August 2026", 「出店します」)
- Don't reintroduce dated "now/next" content, interactive/venue-level maps, countdowns, or per-event JSON-LD. Presence is conveyed by the static Our Reach section (all 5 Singapore regions + Kuala Lumpur), which only grows and never needs syncing
- `/sync-site` (`.claude/commands/sync-site.md`) is the one-step refresh: `python3 scripts/refresh_site.py` pulls the live Google rating (`sync_gbp.py`), raises the stat floors from the finance ledger (`ledger_stats.py --write`, which also reports LEDGER GAPs when events.csv lags operations), then runs `check_site.py` (must PASS) before any push. Timeline entries and review quotes stay hand-curated

## Confidentiality
This is a PUBLIC repository — never commit tokens or credentials, and never hardcode confidential business strings (payee or worker names) even in tooling; `scripts/check_site.py` derives its blocklist from the private finance repo at runtime for this reason. Menu items are fine to publish. PAST venue details are competitive intelligence (competitors mine this site to copy the venue circuit): the site carries no venue list or venue-level map: the interactive map was removed Oct 2026 and replaced by the static "Our Reach" dot-matrix island (`_includes/reach-map.svg`, generated once by `scripts/make_reach_map.py` from URA region boundaries) with all five regions lit, region-level only, and the timeline/gallery name only marquee credentials (Gardens by the Bay, Isetan Scotts, Takashimaya, Seibu KL, bank roadshow clients) — heartland Pasar Malam venues are never named once the event has wrapped. Prefer aggregate numbers (venue counts, stall-days) over venue lists everywhere; the full venue list is shared with prospective partners privately, on request. Do NOT publish menu prices — not confidential, but they vary over time and by venue, so the owner keeps them off the site (signature dishes only; no sub-menu items either). Never publish rent, commissions, sales figures, supplier costs, payees, or worker names. Run `check_site.py` before shipping.

## Security Invariants — do not weaken
`check_site.py` enforces most of these; keep them true when editing:
- **CSP** ships as a meta tag in `_layouts/default.html` (GitHub Pages can't set headers). `script-src` is strict: **never add an inline executable `<script>`** — put JS in `assets/js/`, and pass data via `<script type="application/json">` islands (see the GA4 config island)
- Third-party scripts/styles: pinned versions with **SRI `integrity` hashes** only; the site currently loads no third-party JS at all, keep it that way where possible. Don't add new CDN origins without adding them to the CSP deliberately
- DOM building from data uses `textContent`, never HTML string interpolation (never `innerHTML` with data)
- `check_site.py` also scans all tracked source files for credential patterns and ledger-derived private terms, and fails if the home pages or `_data/`/`_includes/` name a non-marquee venue (IDs, names and areas of night markets/malls/markets, loaded at runtime from the finance repo's `venues.csv`; romanised names only, so Japanese renderings still need a human eye). Only aggregate floors and the Google rating are ever generated into this repo; ledger detail, GBP performance metrics and LEDGER GAP output stay local (auto-refresh logs to `~/.local/state/nyanmeshi-site/`); GitHub secret scanning + push protection are enabled on the repo
- External links keep `rel="noopener noreferrer"`; referrer policy is `strict-origin-when-cross-origin`
- `/.well-known/security.txt` exists (expires 2027-06-30 — renew before then)
- Known accepted limitations of GitHub Pages: no clickjacking protection (`frame-ancestors` can't be set via meta), Google Fonts CSS has no SRI (mitigated by CSP allowlisting). Self-hosting fonts would remove the remaining CDN trust if ever desired

## Project Context
- Jekyll single-page site hosted on GitHub Pages at nyanmeshi.com
- Company: Nyanmeshi JAPAN PTE. LTD. — Singapore-based specialist for Japanese culinary pop-ups and F&B activations
- Brand tone: premium, authentic, approachable — not flashy
- Key contacts: emi.maekawa@nyanmeshi.com · WhatsApp +65 98615103
- Social: @nyanmeshijp (Instagram, TikTok, YouTube), nyanmeshijp (Facebook)
