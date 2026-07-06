/**
 * Font Size Control - blogPost
 * Font size increase/decrease/reset with localStorage persistence.
 */
(function() {
    'use strict';

    var qlEditor = document.querySelector('.ql-editor');
    var fontDecBtns = document.querySelectorAll('#font-dec, #font-dec-main');
    var fontIncBtns = document.querySelectorAll('#font-inc, #font-inc-main');
    var fontResetBtns = document.querySelectorAll('#font-reset, #font-reset-main');

    var minSize = 12; // px
    var maxSize = 24; // px
    var defaultSize = 16; // px
    var step = 2; // px

    var currentFontSize = defaultSize;

    try {
        var savedSize = localStorage.getItem('articlio_font_size');
        if (savedSize) {
            var parsed = parseInt(savedSize, 10);
            if (!isNaN(parsed) && parsed >= minSize && parsed <= maxSize) {
                currentFontSize = parsed;
            }
        }
    } catch (e) {
        console.warn('Failed to load font size from localStorage', e);
    }

    function updateFontSize(size) {
        currentFontSize = size;
        if (qlEditor) {
            qlEditor.style.setProperty('--ql-font-size', currentFontSize + 'px');
        }

        fontDecBtns.forEach(function(btn) { btn.disabled = (currentFontSize <= minSize); });
        fontIncBtns.forEach(function(btn) { btn.disabled = (currentFontSize >= maxSize); });
        
        var percentage = Math.round((currentFontSize / defaultSize) * 100);
        fontResetBtns.forEach(function(btn) {
            btn.innerText = percentage + '%';
        });

        try {
            localStorage.setItem('articlio_font_size', currentFontSize.toString());
        } catch (e) {}
    }

    fontDecBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            if (currentFontSize > minSize) {
                updateFontSize(currentFontSize - step);
            }
        });
    });

    fontIncBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            if (currentFontSize < maxSize) {
                updateFontSize(currentFontSize + step);
            }
        });
    });

    fontResetBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            updateFontSize(defaultSize);
        });
    });

    // Initialize
    updateFontSize(currentFontSize);
})();
