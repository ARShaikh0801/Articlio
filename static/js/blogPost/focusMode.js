/**
 * Focus Mode - blogPost
 * Focus mode toggle, exit float, reading theme selector, inactivity hide, keyboard shortcuts.
 */
(function() {
    'use strict';

    var toggleBtn = document.getElementById('focus-mode-toggle');
    var floatExitBtn = document.getElementById('focus-mode-exit-float');
    var transitionOverlay = document.getElementById('focus-transition-overlay');

    // ── Reading Theme Selector Logic ──
    var READING_THEME_KEY = 'articlio_reading_theme';
    var currentReadingTheme = 'light'; // 'light' | 'sepia' | 'dark'
    // Track the dark mode state the user had BEFORE entering focus mode
    var darkModeBeforeFocus = document.documentElement.classList.contains('dark');

    function applyReadingTheme(theme, saveToStorage) {
        if (saveToStorage === undefined) saveToStorage = true;
        currentReadingTheme = theme;
        var html = document.documentElement;

        // Remove sepia class
        html.classList.remove('reading-theme-sepia');

        if (theme === 'sepia') {
            // Sepia: remove dark mode, add sepia class
            html.classList.remove('dark');
            html.classList.add('reading-theme-sepia');
        } else if (theme === 'dark') {
            // Dark: add dark mode
            html.classList.add('dark');
        } else {
            // Light: remove dark mode
            html.classList.remove('dark');
        }

        // Update active state on dots
        document.querySelectorAll('.reading-theme-dot').forEach(function(dot) {
            dot.classList.toggle('active', dot.dataset.theme === theme);
        });

        if (saveToStorage) {
            try {
                localStorage.setItem(READING_THEME_KEY, theme);
            } catch (e) {}
        }
    }

    // Bind reading theme dot clicks
    document.querySelectorAll('.reading-theme-dot').forEach(function(dot) {
        dot.addEventListener('click', function() {
            applyReadingTheme(this.dataset.theme);
        });
    });

    // ── Inactivity Auto-Hide Logic ──
    var exitBtnTimer = null;
    var isHoveredOnExitBtn = false;

    function resetExitBtnTimer() {
        if (!floatExitBtn) return;
        floatExitBtn.classList.remove('is-idle');
        if (exitBtnTimer) clearTimeout(exitBtnTimer);
        
        var isActive = document.documentElement.classList.contains('focus-mode-active');
        if (isActive && !isHoveredOnExitBtn) {
            exitBtnTimer = setTimeout(function() {
                if (document.documentElement.classList.contains('focus-mode-active') && !isHoveredOnExitBtn) {
                    floatExitBtn.classList.add('is-idle');
                }
            }, 3000);
        }
    }

    var activityEvents = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll'];
    function onUserActivity() {
        resetExitBtnTimer();
    }

    function enableActivityListeners() {
        activityEvents.forEach(function(evt) {
            window.addEventListener(evt, onUserActivity, { passive: true });
        });
        resetExitBtnTimer();
    }

    function disableActivityListeners() {
        activityEvents.forEach(function(evt) {
            window.removeEventListener(evt, onUserActivity);
        });
        if (exitBtnTimer) clearTimeout(exitBtnTimer);
        if (floatExitBtn) floatExitBtn.classList.remove('is-idle');
    }

    // Fullscreen Helper for Mobile Focus Mode
    function toggleFullscreen(active) {
        if (window.innerWidth >= 768) return;
        var docEl = document.documentElement;
        try {
            if (active) {
                if (docEl.requestFullscreen) {
                    docEl.requestFullscreen().catch(function() {});
                } else if (docEl.webkitRequestFullscreen) {
                    docEl.webkitRequestFullscreen().catch(function() {});
                } else if (docEl.msRequestFullscreen) {
                    docEl.msRequestFullscreen().catch(function() {});
                }
            } else {
                if (document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement) {
                    if (document.exitFullscreen) {
                        document.exitFullscreen().catch(function() {});
                    } else if (document.webkitExitFullscreen) {
                        document.webkitExitFullscreen().catch(function() {});
                    } else if (document.msExitFullscreen) {
                        document.msExitFullscreen().catch(function() {});
                    }
                }
            }
        } catch (err) {}
    }

    function setFocusMode(active, animate) {
        if (animate === undefined) animate = true;
        function doApply() {
            var settingsToggleBtn = document.getElementById('reader-settings-toggle');
            var dropdown = document.getElementById('reader-settings-dropdown');

            if (active) {
                // Save the user's dark mode state before focus mode takes over
                darkModeBeforeFocus = document.documentElement.classList.contains('dark');
                document.documentElement.classList.add('focus-mode-active');
                enableActivityListeners();
                if (settingsToggleBtn) settingsToggleBtn.style.display = 'flex';
                if (toggleBtn) {
                    toggleBtn.innerHTML = '\
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16">\
                            <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8M1.173 8a13 13 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5s3.879 1.168 5.168 2.457A13 13 0 0 1 14.828 8q-.086.13-.195.288c-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5s-3.879-1.168-5.168-2.457A13 13 0 0 1 1.172 8z"/>\
                            <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5M4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0"/>\
                        </svg>\
                        <span>Exit Focus</span>';
                }
                // Apply the saved reading theme
                try {
                    var savedTheme = localStorage.getItem(READING_THEME_KEY);
                    if (savedTheme && ['light', 'sepia', 'dark'].indexOf(savedTheme) !== -1) {
                        applyReadingTheme(savedTheme, false);
                    } else {
                        // Auto-detect: if user was in dark mode, default to dark reading theme
                        var detectedTheme = darkModeBeforeFocus ? 'dark' : 'light';
                        applyReadingTheme(detectedTheme, false);
                    }
                } catch (e) {
                    var detectedTheme = darkModeBeforeFocus ? 'dark' : 'light';
                    applyReadingTheme(detectedTheme, false);
                }
            } else {
                document.documentElement.classList.remove('focus-mode-active');
                document.documentElement.classList.remove('reading-theme-sepia');
                disableActivityListeners();
                if (settingsToggleBtn) settingsToggleBtn.style.display = 'none';
                if (dropdown) dropdown.classList.remove('active');
                // Restore the dark mode state the user had before focus mode
                if (darkModeBeforeFocus) {
                    document.documentElement.classList.add('dark');
                } else {
                    document.documentElement.classList.remove('dark');
                }
                if (toggleBtn) {
                    toggleBtn.innerHTML = '\
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16">\
                            <path d="M10.5 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0"/>\
                            <path d="M0 8s3-5.5 8-5.5S16 8 16 8s-3 5.5-8 5.5S0 8 0 8m8 3.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7"/>\
                        </svg>\
                        <span>Focus Mode</span>';
                }
            }
            try {
                localStorage.setItem('articlio_focus_mode', active ? 'true' : 'false');
            } catch (e) {}
            if (typeof window.updateFocusReadingIndicators === 'function') {
                setTimeout(window.updateFocusReadingIndicators, 100);
            }
            if (active && typeof handleTOCScroll === 'function') {
                setTimeout(handleTOCScroll, 100);
            }
        }

        if (animate && transitionOverlay) {
            transitionOverlay.classList.add('active');
            setTimeout(function() {
                doApply();
                toggleFullscreen(active);
                setTimeout(function() {
                    transitionOverlay.classList.remove('active');
                }, 50);
            }, 350);
        } else {
            doApply();
            if (!active) {
                toggleFullscreen(false);
            }
        }
    }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            var isActive = document.documentElement.classList.contains('focus-mode-active');
            setFocusMode(!isActive);
        });
    }

    if (floatExitBtn) {
        floatExitBtn.addEventListener('mouseenter', function() {
            isHoveredOnExitBtn = true;
            floatExitBtn.classList.remove('is-idle');
            if (exitBtnTimer) clearTimeout(exitBtnTimer);
        });
        floatExitBtn.addEventListener('mouseleave', function() {
            isHoveredOnExitBtn = false;
            resetExitBtnTimer();
        });
        floatExitBtn.addEventListener('click', function() {
            setFocusMode(false);
            toggleFullscreen(false);
        });
    }



    // Keyboard shortcuts: Escape to exit, F to toggle
    document.addEventListener('keydown', function(e) {
        var tag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
        if (tag === 'input' || tag === 'textarea' || tag === 'select') return;
        if (document.activeElement && document.activeElement.isContentEditable) return;

        if (e.key === 'Escape' && document.documentElement.classList.contains('focus-mode-active')) {
            e.preventDefault();
            setFocusMode(false);
            toggleFullscreen(false);
        }

        if ((e.key === 'f' || e.key === 'F') && !e.ctrlKey && !e.metaKey && !e.altKey) {
            e.preventDefault();
            var isActive = document.documentElement.classList.contains('focus-mode-active');
            setFocusMode(!isActive);
        }
    });

    // ── Table of Contents Sidebar Logic ──
    var headings = [];
    var tocItems = [];
    var isTOCEnabled = false;
    var isTOCScrollThrottled = false;

    function initFocusTOC() {
        var editor = document.querySelector('.ql-editor');
        var tocSidebar = document.getElementById('focus-toc-sidebar');
        var tocList = document.getElementById('focus-toc-list');
        if (!editor || !tocSidebar || !tocList) return;

        var headingElements = editor.querySelectorAll('h2, h3');
        if (headingElements.length < 2) {
            tocSidebar.classList.add('no-toc');
            return;
        }

        headings = Array.prototype.slice.call(headingElements);
        isTOCEnabled = true;

        tocList.innerHTML = '';
        tocItems = [];

        headings.forEach(function(heading, index) {
            if (!heading.id) {
                heading.id = 'toc-heading-' + index;
            }

            var li = document.createElement('li');
            var a = document.createElement('a');
            a.textContent = heading.textContent.trim();
            a.href = '#' + heading.id;
            a.className = 'focus-toc-item';
            if (heading.tagName.toLowerCase() === 'h3') {
                a.classList.add('focus-toc-item-h3');
            }

            a.addEventListener('click', function(e) {
                e.preventDefault();
                var headingTop = heading.getBoundingClientRect().top + window.scrollY;
                // Offset of 110px ensures the heading clears the top sticky toolbar (approx 60px height + 50px padding)
                window.scrollTo({
                    top: headingTop - 110,
                    behavior: 'smooth'
                });
            });

            li.appendChild(a);
            tocList.appendChild(li);
            tocItems.push(a);
        });

        window.addEventListener('scroll', handleTOCScroll, { passive: true });
        handleTOCScroll();
    }

    function handleTOCScroll() {
        if (!isTOCEnabled || !document.documentElement.classList.contains('focus-mode-active')) return;
        if (isTOCScrollThrottled) return;

        isTOCScrollThrottled = true;
        window.requestAnimationFrame(function() {
            var scrollPosition = window.scrollY || window.pageYOffset;
            var activeIndex = -1;

            for (var i = 0; i < headings.length; i++) {
                var headingTop = headings[i].getBoundingClientRect().top + scrollPosition;
                if (scrollPosition >= headingTop - 150) {
                    activeIndex = i;
                }
            }

            if ((window.innerHeight + scrollPosition) >= document.documentElement.scrollHeight - 50) {
                activeIndex = headings.length - 1;
            }

            tocItems.forEach(function(item, idx) {
                if (idx === activeIndex) {
                    item.classList.add('active');
                    var sidebar = document.getElementById('focus-toc-sidebar');
                    if (sidebar) {
                        var itemTop = item.offsetTop;
                        var sidebarScroll = sidebar.scrollTop;
                        var sidebarHeight = sidebar.clientHeight;
                        if (itemTop < sidebarScroll || itemTop > sidebarScroll + sidebarHeight - 40) {
                            sidebar.scrollTop = itemTop - sidebarHeight / 2;
                        }
                    }
                } else {
                    item.classList.remove('active');
                }
            });

            isTOCScrollThrottled = false;
        });
    }

    // Initialize TOC on page load
    initFocusTOC();

    // Initialize from localStorage (no animation on page load)
    try {
        var savedFocus = localStorage.getItem('articlio_focus_mode');
        if (savedFocus === 'true') {
            setFocusMode(true, false);
        }
    } catch (e) {}
})();
