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

## Project Context
- Single `index.html` static site hosted on GitHub Pages at nyanmeshi.com
- Company: Nyanmeshi JAPAN PTE. LTD. — Singapore-based specialist for Japanese culinary pop-ups and F&B activations
- Brand tone: premium, authentic, approachable — not flashy
- Key contacts: emi.maekawa@nyanmeshi.com · WhatsApp +65 98615103
- Social: @nyanmeshi_japan (Instagram), nyanmeshijp (Facebook)
