// GA4 init + CTA click tracking. Only runs when _layouts/default.html has
// emitted the config data island (i.e. site.ga4_measurement_id is set) —
// see the comment there for why the measurement ID travels via a JSON
// island rather than an inline gtag() call (CSP has no 'unsafe-inline' on
// script-src).
document.addEventListener('DOMContentLoaded', () => {
    let config = {};
    try {
        const configEl = document.getElementById('nyan-ga-config');
        config = configEl ? JSON.parse(configEl.textContent) : {};
    } catch (e) {
        config = {};
    }
    if (!config.id) return;

    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', config.id);

    document.querySelectorAll('[data-cta]').forEach((el) => {
        el.addEventListener('click', () => {
            gtag('event', 'cta_click', { cta_id: el.dataset.cta });
        });
    });
});
