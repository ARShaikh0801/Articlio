/**
 * Articlio Theme System - 5 curated blog-friendly palettes
 * Each theme generates CSS custom properties for the full shade range.
 */

const THEMES = {
    ocean:   { h: 210, s: 50, l: 45, label: 'Ocean',   color: '#3a7cc0' },
    emerald: { h: 160, s: 42, l: 42, label: 'Emerald', color: '#3da88a' },
    slate:   { h: 220, s: 14, l: 40, label: 'Slate',   color: '#575e6d' },
    crimson: { h: 350, s: 50, l: 45, label: 'Crimson', color: '#b04050' },
    violet:  { h: 270, s: 35, l: 45, label: 'Violet',  color: '#7a50b0' },
};

const DEFAULT_THEME = 'ocean';

function applyTheme(themeName) {
    const t = THEMES[themeName];
    if (!t) return;

    // Lighter shade system for a clean, airy blog feel
    const softS = Math.round(t.s * 0.6);  // desaturated for backgrounds

    const vars = {
        '--theme-base':       `hsl(${t.h}, ${t.s}%, ${t.l}%)`,
        '--theme-darkest':    `hsl(${t.h}, ${t.s}%, 18%)`,
        '--theme-dark':       `hsl(${t.h}, ${t.s}%, 28%)`,
        '--theme-medium':     `hsl(${t.h}, ${t.s}%, ${t.l + 8}%)`,
        '--theme-base-faded': `hsl(${t.h}, ${softS}%, ${t.l}%, 0.10)`,
        '--theme-light':      `hsl(${t.h}, ${softS}%, 90%)`,
        '--theme-lightest':   `hsl(${t.h}, ${Math.round(t.s * 0.3)}%, 96%)`,
    };

    for (const key in vars) {
        document.documentElement.style.setProperty(key, vars[key]);
    }
}

/** Mark the active pill visually */
function setActivePill(themeName) {
    document.querySelectorAll('.theme-pill').forEach(pill => {
        pill.classList.remove('theme-pill--active');
        pill.setAttribute('aria-pressed', 'false');
    });
    const active = document.querySelector(`.theme-pill[data-theme="${themeName}"]`);
    if (active) {
        active.classList.add('theme-pill--active');
        active.setAttribute('aria-pressed', 'true');
    }
}

/** Build the pill buttons inside a container */
function renderThemePills(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';

    for (const [name, t] of Object.entries(THEMES)) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'theme-pill';
        btn.dataset.theme = name;
        btn.title = t.label;
        btn.setAttribute('aria-label', `${t.label} theme`);
        btn.setAttribute('aria-pressed', 'false');
        btn.style.setProperty('--pill-color', t.color);

        btn.addEventListener('click', () => {
            applyTheme(name);
            setActivePill(name);
            
            if (window.USER_IS_AUTHENTICATED) {
                // Persistent across pages in this session
                try { sessionStorage.setItem('articlio_theme', name); } catch(e) {}
                
                // Persist to DB (Optimistic UI - we already applied it above)
                fetch('/update-theme', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ theme: name })
                }).catch(err => console.error('Theme DB sync failed:', err));
            } else {
                try { localStorage.setItem('articlio_theme', name); } catch(e) {}
            }
        });

        container.appendChild(btn);
    }
}

/** CSRF helper for the theme update API */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/** Initialize on DOMContentLoaded */
document.addEventListener('DOMContentLoaded', () => {
    let saved = DEFAULT_THEME;

    if (window.USER_IS_AUTHENTICATED) {
        // Check session storage first (for cross-page persistence without DB hits)
        const sessionStored = sessionStorage.getItem('articlio_theme');
        if (sessionStored && THEMES[sessionStored]) {
            saved = sessionStored;
        } else if (window.DB_THEME && THEMES[window.DB_THEME]) {
            // Use DB theme if session is empty (e.g. first page load of session)
            saved = window.DB_THEME;
            sessionStorage.setItem('articlio_theme', saved);
        }
    } else {
        // Fallback to localStorage for guests
        try {
            const stored = localStorage.getItem('articlio_theme');
            if (stored && THEMES[stored]) saved = stored;
        } catch(e) {}
    }

    applyTheme(saved);

    // Render pills in both desktop and mobile nav
    renderThemePills('theme-pills');
    renderThemePills('theme-pills-mobile');
    setActivePill(saved);

    // Initialize creative dark mode toggler
    initDarkModeToggle();
});

/** Dark mode toggle logic */
function initDarkModeToggle() {
    const desktopBtn = document.getElementById('dark-mode-toggle-desktop');
    const mobileBtn = document.getElementById('dark-mode-toggle-mobile');

    function updateToggleButtonsState(isDark) {
        [desktopBtn, mobileBtn].forEach(btn => {
            if (!btn) return;
            btn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
            btn.title = isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode';
        });
    }

    function toggleDarkMode() {
        const isDark = document.documentElement.classList.toggle('dark');
        localStorage.setItem('articlio_dark_mode', isDark ? 'true' : 'false');
        updateToggleButtonsState(isDark);
        
        if (typeof window.applyDarkModeTextColors === 'function') {
            if (isDark) {
                window.applyDarkModeTextColors('.ql-editor');
            } else {
                window.restoreDarkModeTextColors('.ql-editor');
            }
        }
    }

    const currentIsDark = document.documentElement.classList.contains('dark');
    updateToggleButtonsState(currentIsDark);
    if (currentIsDark && typeof window.applyDarkModeTextColors === 'function') {
        window.applyDarkModeTextColors('.ql-editor');
    }

    if (desktopBtn) desktopBtn.addEventListener('click', toggleDarkMode);
    if (mobileBtn) mobileBtn.addEventListener('click', toggleDarkMode);
}

