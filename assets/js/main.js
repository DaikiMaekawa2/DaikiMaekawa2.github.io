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
document.querySelectorAll('.schedule-card').forEach(card => {
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

// Interactive footprint map. Locations come from a non-executable JSON data
// island, and popups are built with DOM APIs (textContent) so location data
// can never be interpreted as HTML.
document.addEventListener('DOMContentLoaded', () => {
    if (typeof L === 'undefined' || !document.getElementById('singapore-map')) return;

    let locations = [];
    try {
        const dataEl = document.getElementById('nyan-locations');
        locations = dataEl ? JSON.parse(dataEl.textContent) : [];
    } catch (e) {
        locations = [];
    }

    const map = L.map('singapore-map', { scrollWheelZoom: false }).setView([1.3521, 103.8198], 11);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);

    const brandIcon = L.divIcon({
        className: 'custom-div-icon',
        html: '<div class="map-marker-dot"></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
    });

    locations.forEach(loc => {
        const popup = document.createElement('div');
        popup.className = 'map-popup';
        const name = document.createElement('strong');
        name.textContent = loc.name;
        const type = document.createElement('span');
        type.className = 'map-popup-type';
        type.textContent = loc.type;
        popup.append(name, document.createElement('br'), type);
        L.marker([loc.lat, loc.lng], { icon: brandIcon }).bindPopup(popup).addTo(map);
    });
});
