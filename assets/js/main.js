// Hamburger menu
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobile-menu');
hamburger.addEventListener('click', () => {
    const open = mobileMenu.classList.toggle('open');
    hamburger.classList.toggle('open', open);
    hamburger.setAttribute('aria-expanded', open);
});
mobileMenu.querySelectorAll('.mobile-menu-link').forEach(link => {
    link.addEventListener('click', () => {
        mobileMenu.classList.remove('open');
        hamburger.classList.remove('open');
        hamburger.setAttribute('aria-expanded', false);
    });
});

// Nav scroll shrink + scroll-to-top visibility
const nav = document.querySelector('nav');
const scrollTopBtn = document.getElementById('scroll-top');
window.addEventListener('scroll', () => {
    const scrolled = window.scrollY > 60;
    nav.classList.toggle('scrolled', scrolled);
    scrollTopBtn.classList.toggle('visible', scrolled);
}, { passive: true });
scrollTopBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

// Section reveal on scroll
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            revealObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.1 });
document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

// Season timeline line draws itself as the section scrolls through the viewport.
const timeline = document.querySelector('.timeline');
if (timeline) {
    timeline.style.setProperty('--progress', 0);
    window.addEventListener('scroll', () => {
        const rect = timeline.getBoundingClientRect();
        const viewH = window.innerHeight;
        const progress = (viewH * 0.85 - rect.top) / rect.height;
        timeline.style.setProperty('--progress', Math.min(Math.max(progress, 0), 1));
    }, { passive: true });
}

// Scrollspy: highlight the nav link for the section in view.
const navLinks = [...document.querySelectorAll('.nav-links a[href^="#"]')];
const sectionFor = Object.fromEntries(navLinks.map(a => [a.getAttribute('href').slice(1), a]));
const spyObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        const link = sectionFor[entry.target.id];
        if (!link) return;
        if (entry.isIntersecting) {
            navLinks.forEach(a => a.classList.remove('active'));
            link.classList.add('active');
        }
    });
}, { rootMargin: '-40% 0px -55% 0px' });
Object.keys(sectionFor).forEach(id => {
    const el = document.getElementById(id);
    if (el) spyObserver.observe(el);
});

// Stat numerals count up once when scrolled into view.
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const statObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        statObserver.unobserve(entry.target);
        const el = entry.target;
        const target = parseInt(el.dataset.count, 10);
        if (reduceMotion || !Number.isFinite(target)) return;
        const duration = 1100;
        const startTime = performance.now();
        const tick = (now) => {
            const t = Math.min((now - startTime) / duration, 1);
            const eased = 1 - Math.pow(1 - t, 3);
            el.textContent = Math.round(target * eased);
            if (t < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    });
}, { threshold: 0.6 });
document.querySelectorAll('.stat-number').forEach(el => statObserver.observe(el));

// Schedule cards: mark On Now / Coming Up / Season Wrapped from data attributes,
// so the static build never shows a stale status.
document.querySelectorAll('.schedule-card[data-start]').forEach(card => {
    const start = new Date(card.dataset.start + 'T00:00:00');
    const end = new Date(card.dataset.end + 'T23:59:59');
    const now = new Date();
    const label = card.querySelector('.schedule-status-text');
    if (now >= start && now <= end) {
        card.classList.add('is-live');
        label.textContent = card.dataset.labelLive || 'On Now';
    } else if (now < start) {
        label.textContent = card.dataset.labelUpcoming || 'Coming Up';
    } else {
        label.textContent = card.dataset.labelPast || 'Season Wrapped';
    }
});

// Footprint map: region-level coverage only — venue names and exact
// coordinates are deliberately never published (see CLAUDE.md). Data comes
// from a non-executable JSON data island, and labels are built with DOM
// APIs (textContent) so it can never be interpreted as HTML.
document.addEventListener('DOMContentLoaded', () => {
    if (typeof L === 'undefined' || !document.getElementById('singapore-map')) return;

    let regions = [];
    try {
        const dataEl = document.getElementById('nyan-coverage');
        regions = dataEl ? JSON.parse(dataEl.textContent) : [];
    } catch (e) {
        regions = [];
    }

    const lang = document.documentElement.lang;
    const brandRed = getComputedStyle(document.documentElement)
        .getPropertyValue('--brand-red-dark').trim() || '#d63031';

    const map = L.map('singapore-map', { scrollWheelZoom: false }).setView([1.3521, 103.8198], 11);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);

    regions.forEach(region => {
        // Circle AREA encodes the venue count (radius ∝ √n), with a small
        // floor in metres so the smallest region stays legible.
        const radius = 700 * Math.sqrt(region.venues) + 800;
        L.circle([region.lat, region.lng], {
            radius,
            color: brandRed,
            weight: 1.5,
            opacity: 0.5,
            fillColor: brandRed,
            fillOpacity: 0.12,
            interactive: false
        }).addTo(map);

        const label = document.createElement('div');
        label.className = 'map-region-label';
        const count = document.createElement('span');
        count.className = 'map-region-count';
        count.textContent = region.venues;
        const name = document.createElement('span');
        name.className = 'map-region-name';
        name.textContent = (lang === 'ja' && region.region_ja) ? region.region_ja : region.region;
        label.append(count, name);
        L.marker([region.lat, region.lng], {
            icon: L.divIcon({ className: 'map-region-icon', html: label, iconSize: [120, 44], iconAnchor: [60, 22] }),
            interactive: false,
            keyboard: false
        }).addTo(map);
    });
});
