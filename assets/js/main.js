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

// Intro film: branded play button over the poster, plus chapter jumps.
// The video ships with native controls, so it still works without JS.
const film = document.querySelector('.film-video');
if (film) {
    const playBtn = document.querySelector('.film-play');
    const chapterList = document.querySelector('.film-chapters');
    const chapters = [...document.querySelectorAll('.film-chapter')];
    const starts = chapters.map(btn => parseFloat(btn.dataset.start));
    const play = () => {
        playBtn.hidden = true;
        film.controls = true;
        // If the browser refuses playback, the native controls are already up.
        film.play().catch(() => {});
    };
    film.controls = false;
    playBtn.hidden = false;
    chapterList.hidden = false;
    playBtn.addEventListener('click', play);
    // The fixed nav covers the top of the player when it sits high on a
    // phone screen (the clip's corner badge got cut in half), so starting
    // playback brings the whole frame into view just below the nav.
    const frame = film.closest('.film-frame');
    const smooth = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const revealFrame = () => {
        const navBottom = nav.getBoundingClientRect().bottom;
        const r = frame.getBoundingClientRect();
        if (r.top < navBottom + 8 || r.bottom > window.innerHeight) {
            window.scrollBy({ top: r.top - navBottom - 16, behavior: smooth ? 'smooth' : 'auto' });
        }
    };
    film.addEventListener('play', () => {
        playBtn.hidden = true;
        film.controls = true;
        revealFrame();
    });
    // With preload="none" a seek before metadata loads is discarded,
    // so the first chapter click waits for loadedmetadata.
    const seek = (t) => {
        if (film.readyState >= 1) film.currentTime = t;
        else film.addEventListener('loadedmetadata', () => { film.currentTime = t; }, { once: true });
    };
    chapters.forEach((btn, i) => btn.addEventListener('click', () => {
        seek(starts[i]);
        play();
    }));
    film.addEventListener('timeupdate', () => {
        let current = 0;
        starts.forEach((start, i) => { if (film.currentTime >= start) current = i; });
        chapters.forEach((btn, i) => btn.setAttribute('aria-current', i === current ? 'true' : 'false'));
    });
}
