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

    function updateReadingProgressBar() {
        if (!contentEl || !readingProgressBar) return;
        var rect = contentEl.getBoundingClientRect();
        var contentHeight = contentEl.offsetHeight;
        
        var elementTop = rect.top;
        var elementBottom = rect.bottom;
        var viewportHeight = window.innerHeight;
        
        var startY = 100; // Top boundary (navbar offset)
        var endY = viewportHeight; // Bottom boundary
        
        var progress = 0;
        if (elementTop > startY) {
            progress = 0;
        } else if (elementBottom < endY) {
            progress = 100;
        } else {
            var totalRange = (contentHeight + startY) - endY;
            var currentScrolled = startY - elementTop;
            progress = (currentScrolled / totalRange) * 100;
        }
        
        readingProgressBar.style.width = Math.min(100, Math.max(0, progress)) + '%';
    }

    // ── Focus Mode Reading Indicators ──
    var focusProgressBar = document.getElementById('focus-progress-bar');
    var focusTimeText = document.getElementById('focus-time-text');
    var focusTimeEl = document.getElementById('focus-time-remaining');
    var totalReadingTime = parseInt(focusTimeEl ? focusTimeEl.dataset.totalTime : '3') || 3;

    window.updateFocusReadingIndicators = function() {
        if (!contentEl) return;
        var rect = contentEl.getBoundingClientRect();
        var contentHeight = contentEl.offsetHeight;
        var viewportHeight = window.innerHeight;
        var progress = 0;
        if (rect.top > 0) {
            progress = 0;
        } else if (rect.bottom < viewportHeight) {
            progress = 100;
        } else {
            var totalRange = contentHeight - viewportHeight;
            if (totalRange > 0) {
                progress = (-rect.top / totalRange) * 100;
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

    window.addEventListener('scroll', function() {
        updateReadingProgressBar();
        window.updateFocusReadingIndicators();
    });

    window.addEventListener('resize', function() {
        updateReadingProgressBar();
        window.updateFocusReadingIndicators();
    });

    // Initialize progress bars
    updateReadingProgressBar();
    window.updateFocusReadingIndicators();
})();
