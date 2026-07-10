/**
 * Reading Progress Bar - blogPost
 * Navbar reading progress bar + Focus mode progress bar + time remaining indicator.
 */
(function() {
    'use strict';

    var contentEl = document.querySelector('.ql-editor');

    // ── Move progress bar to navbar ──
    var progressContainer = document.querySelector('.reading-progress-container');
    var mainNav = document.getElementById('main-nav');
    if (mainNav && progressContainer) {
        mainNav.appendChild(progressContainer);
    }

    var readingProgressBar = document.getElementById('reading-progress-bar');
    var focusProgressBar = document.getElementById('focus-progress-bar');
    var focusTimeText = document.getElementById('focus-time-text');
    var focusTimeEl = document.getElementById('focus-time-remaining');
    var totalReadingTime = parseInt(focusTimeEl ? focusTimeEl.dataset.totalTime : '3') || 3;

    // Cache layout variables to avoid layout thrashing on scroll
    var contentHeight = 0;
    var contentOffsetTop = 0;

    function updateLayoutMetrics() {
        if (!contentEl) return;
        contentHeight = contentEl.offsetHeight;
        var rect = contentEl.getBoundingClientRect();
        contentOffsetTop = rect.top + window.scrollY;
    }

    function updateReadingProgressBar() {
        if (!contentEl || !readingProgressBar) return;
        var scrollY = window.scrollY;
        var viewportHeight = window.innerHeight;
        
        var elementTop = contentOffsetTop;
        var elementBottom = contentOffsetTop + contentHeight;
        
        var startY = 100; // Top boundary (navbar offset)
        var endY = viewportHeight; // Bottom boundary
        
        var progress = 0;
        if (scrollY + startY < elementTop) {
            progress = 0;
        } else if (scrollY + endY > elementBottom) {
            progress = 100;
        } else {
            var totalRange = (contentHeight + startY) - endY;
            if (totalRange > 0) {
                var currentScrolled = (scrollY + startY) - elementTop;
                progress = (currentScrolled / totalRange) * 100;
            }
        }
        
        readingProgressBar.style.width = Math.min(100, Math.max(0, progress)) + '%';
    }

    window.updateFocusReadingIndicators = function() {
        if (!contentEl) return;
        var scrollY = window.scrollY;
        var viewportHeight = window.innerHeight;
        var progress = 0;
        
        var elementTop = contentOffsetTop;
        var elementBottom = contentOffsetTop + contentHeight;

        if (scrollY < elementTop) {
            progress = 0;
        } else if (scrollY + viewportHeight > elementBottom) {
            progress = 100;
        } else {
            var totalRange = contentHeight - viewportHeight;
            if (totalRange > 0) {
                progress = ((scrollY - elementTop) / totalRange) * 100;
            }
        }
        progress = Math.min(100, Math.max(0, progress));
        if (focusProgressBar) {
            focusProgressBar.style.width = progress + '%';
        }
        if (focusTimeText) {
            var remaining = Math.max(0, Math.ceil(totalReadingTime * (1 - progress / 100)));
            if (progress >= 98) {
                focusTimeText.textContent = 'Finished!';
            } else if (remaining < 1) {
                focusTimeText.textContent = '< 1 min left';
            } else {
                focusTimeText.textContent = '~' + remaining + ' min left';
            }
        }
    };

    var isScrollTicking = false;
    function onScroll() {
        if (!isScrollTicking) {
            window.requestAnimationFrame(function() {
                updateReadingProgressBar();
                window.updateFocusReadingIndicators();
                isScrollTicking = false;
            });
            isScrollTicking = true;
        }
    }

    window.addEventListener('scroll', onScroll, { passive: true });

    window.addEventListener('resize', function() {
        updateLayoutMetrics();
        updateReadingProgressBar();
        window.updateFocusReadingIndicators();
    });

    // Update metrics when content might change size (e.g. dynamic state loads)
    window.addEventListener('load', function() {
        updateLayoutMetrics();
        updateReadingProgressBar();
        window.updateFocusReadingIndicators();
    });

    // Observe changes inside contentEl to update metrics if DOM updates
    if (contentEl && 'MutationObserver' in window) {
        var contentObserver = new MutationObserver(function() {
            updateLayoutMetrics();
            updateReadingProgressBar();
            window.updateFocusReadingIndicators();
        });
        contentObserver.observe(contentEl, { childList: true, subtree: true, characterData: true });
    }

    // Initial metrics and calculation
    updateLayoutMetrics();
    updateReadingProgressBar();
    window.updateFocusReadingIndicators();
})();
