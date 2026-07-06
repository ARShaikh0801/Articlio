/**
 * Reader Settings - blogPost
 * Line spacing, content width, reader settings dropdown toggle.
 */

// ── Spacing Control Logic ──
(function() {
    'use strict';

    var qlEditor = document.querySelector('.ql-editor');
    var spacingSelector = document.getElementById('spacing-selector');
    if (!spacingSelector) return;

    var SPACING_KEY = 'articlio_line_spacing';
    var spacingMap = {
        'compact': 1.4,
        'comfortable': 1.75,
        'spacious': 2.1
    };

    var currentSpacing = 'comfortable';

    try {
        var savedSpacing = localStorage.getItem(SPACING_KEY);
        if (savedSpacing && spacingMap[savedSpacing] !== undefined) {
            currentSpacing = savedSpacing;
        }
    } catch (e) {}

    function applySpacing(spacing, saveToStorage) {
        if (saveToStorage === undefined) saveToStorage = true;
        currentSpacing = spacing;
        var height = spacingMap[spacing];

        if (qlEditor) {
            qlEditor.style.setProperty('--ql-line-height', height);
        }

        // Update active class on spacing buttons
        spacingSelector.querySelectorAll('.spacing-btn').forEach(function(btn) {
            btn.classList.toggle('active', btn.dataset.spacing === spacing);
        });

        if (saveToStorage) {
            try {
                localStorage.setItem(SPACING_KEY, spacing);
            } catch (e) {}
        }
    }

    // Bind clicks
    spacingSelector.querySelectorAll('.spacing-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            applySpacing(this.dataset.spacing);
        });
    });

    // Initialize
    applySpacing(currentSpacing, false);
})();

// ── Content Width Control Logic ──
(function() {
    'use strict';

    var maxW5xl = document.querySelector('.max-w-5xl');
    var widthSelector = document.getElementById('width-selector');
    if (!widthSelector) return;

    var WIDTH_KEY = 'articlio_content_width';
    var widthMap = {
        'narrow': '40rem',
        'medium': '48rem',
        'wide': '56rem'
    };

    var currentWidth = 'medium';

    try {
        var savedWidth = localStorage.getItem(WIDTH_KEY);
        if (savedWidth && widthMap[savedWidth] !== undefined) {
            currentWidth = savedWidth;
        }
    } catch (e) {}

    function applyWidth(width, saveToStorage) {
        if (saveToStorage === undefined) saveToStorage = true;
        currentWidth = width;
        var remValue = widthMap[width];

        if (maxW5xl) {
            maxW5xl.style.setProperty('--focus-content-width', remValue);
        }

        // Update active class on width buttons
        widthSelector.querySelectorAll('.width-btn').forEach(function(btn) {
            btn.classList.toggle('active', btn.dataset.width === width);
        });

        if (saveToStorage) {
            try {
                localStorage.setItem(WIDTH_KEY, width);
            } catch (e) {}
        }
    }

    // Bind clicks
    widthSelector.querySelectorAll('.width-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            applyWidth(this.dataset.width);
        });
    });

    // Initialize
    applyWidth(currentWidth, false);
})();

// ── Reader Settings Dropdown Toggle ──
(function() {
    'use strict';

    var toggleBtn = document.getElementById('reader-settings-toggle');
    var dropdown = document.getElementById('reader-settings-dropdown');
    if (!toggleBtn || !dropdown) return;

    toggleBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdown.classList.toggle('active');
    });

    dropdown.addEventListener('click', function(e) {
        e.stopPropagation();
    });

    document.addEventListener('click', function() {
        dropdown.classList.remove('active');
    });
})();
