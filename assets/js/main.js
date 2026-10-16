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
