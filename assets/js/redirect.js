// Tracked redirect for short links such as the stall QR (/ig/), rendered by
// _layouts/redirect.html. Config arrives via the JSON data island (the CSP has
// no 'unsafe-inline' on script-src). Records a GA4 page_view plus the page's
// custom event, then leaves via location.replace as soon as GA confirms the
// event, or after timeout_ms if gtag.js is slow or blocked, so a visitor is
// never stranded. Without JS, the layout's meta refresh and button take over.
(() => {
    let config = {};
    try {
        const el = document.getElementById('nyan-redirect-config');
        config = el ? JSON.parse(el.textContent) : {};
    } catch (e) {
        config = {};
    }
    if (!config.url) return;

    let done = false;
    const go = () => {
        if (done) return;
        done = true;
        window.location.replace(config.url);
    };
    setTimeout(go, config.timeout_ms || 800);

    if (!config.id) {
        go();
        return;
    }
    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', config.id);
    if (config.event) {
        gtag('event', config.event, {
            transport_type: 'beacon',
            event_callback: go,
        });
    } else {
        go();
    }
})();
