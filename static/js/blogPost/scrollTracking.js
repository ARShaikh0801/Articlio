/**
 * Scroll Tracking - blogPost
 * Tracks reading scroll progress and syncs to server or localStorage.
 */
(function() {
    'use strict';

    var config = window.BlogPostConfig;
    var postSno = config.postSno;
    var slug = config.slug;
    var contentEl = document.querySelector('.ql-editor');

    function getScrollProgress() {
        if (!contentEl) return 0;
        var rect = contentEl.getBoundingClientRect();
        var contentTop = rect.top + window.scrollY;
        var contentHeight = contentEl.offsetHeight;
        if (contentHeight <= 0) return 0;
        var scrolledIntoContent = window.scrollY + window.innerHeight - contentTop;
        var progress = (scrolledIntoContent / contentHeight) * 100;
        return Math.min(100, Math.max(0, Math.round(progress)));
    }

    var scrollTrackTimer = null;
    var lastSyncedProgress = -1;

    function syncScrollProgress() {
        var progress = getScrollProgress();
        if (progress === lastSyncedProgress) return;
        lastSyncedProgress = progress;

        if (window.USER_IS_AUTHENTICATED) {
            // POST to server
            fetch('/blog/api/history/track/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.CSRF_TOKEN
                },
                body: JSON.stringify({
                    post_sno: postSno,
                    scroll_progress: progress
                })
            }).catch(function() {});
        } else {
            // Save to localStorage
            try {
                var HISTORY_LS_KEY = 'articlio_history';
                var SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000;
                var raw = localStorage.getItem(HISTORY_LS_KEY);
                var entries = raw ? JSON.parse(raw) : [];
                var cutoff = Date.now() - SEVEN_DAYS_MS;
                entries = entries.filter(function(e) { return e.ts >= cutoff; });
                var idx = entries.findIndex(function(e) { return e.sno == postSno; });
                var entry = { sno: parseInt(postSno), scroll_progress: progress, ts: Date.now(), slug: slug };
                if (idx >= 0) {
                    entries[idx] = entry;
                } else {
                    entries.unshift(entry);
                }
                localStorage.setItem(HISTORY_LS_KEY, JSON.stringify(entries));
            } catch(e) {}
        }
    }

    window.addEventListener('scroll', function() {
        clearTimeout(scrollTrackTimer);
        scrollTrackTimer = setTimeout(syncScrollProgress, 2000);
    });

    // Also sync on page unload to capture final position
    window.addEventListener('beforeunload', function() {
        syncScrollProgress();
    });

    // Sync once on load to record the visit
    syncScrollProgress();
})();
