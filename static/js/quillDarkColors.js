(function() {
    // Lookup map supporting standard Quill palette and Tailwind CSS colors used in seeded posts
    const COLOR_MAP = {
        // --- Row 1 (base colors) ---
        '#000000': '#f8fafc',
        '#e60000': '#ff8a80',
        '#ff9900': '#ffe082',
        '#ffff00': '#ffff8d',
        '#008a00': '#b9f6ca',
        '#0066cc': '#80d8ff',
        '#9933ff': '#ea80fc',

        // --- Row 2 (lightest colors) ---
        '#ffffff': '#ffffff',
        '#facccc': '#facccc',
        '#ffebcc': '#ffebcc',
        '#ffffcc': '#ffffcc',
        '#cce8cc': '#cce8cc',
        '#cce0f5': '#cce0f5',
        '#ebd6ff': '#ebd6ff',

        // --- Row 3 (light colors) ---
        '#bbbbbb': '#f1f5f9',
        '#f06666': '#ff8a80',
        '#ffc266': '#ffe082',
        '#ffff66': '#ffff8d',
        '#66b966': '#b9f6ca',
        '#66a3e0': '#80d8ff',
        '#c285ff': '#ea80fc',

        // --- Row 4 (dark colors) ---
        '#888888': '#e2e8f0',
        '#a10000': '#ff8a80',
        '#b26b00': '#ffe082',
        '#b2b200': '#ffff8d',
        '#006100': '#b9f6ca',
        '#0047b2': '#80d8ff',
        '#6b24b2': '#ea80fc',

        // --- Row 5 (darkest colors) ---
        '#444444': '#e2e8f0',
        '#5c0000': '#ff8a80',
        '#663d00': '#ffe082',
        '#666600': '#ffff8d',
        '#003700': '#b9f6ca',
        '#002966': '#80d8ff',
        '#3d1466': '#ea80fc',

        // --- Tailwind background highlights (Seeded Posts) ---
        '#eef2ff': '#1e253b', // light indigo -> dark indigo
        '#faf5ff': '#241a36', // light purple -> dark purple
        '#ecfdf5': '#0f261c', // light emerald -> dark green
        '#fff7ed': '#2d1f10', // light orange -> dark brown
        '#fef2f2': '#2b1414', // light red -> dark red
        '#eff6ff': '#122036', // light blue -> dark blue
        '#fdf4ff': '#2c122c', // light pink -> dark magenta
        '#f1f5f9': '#1e293b', // light slate -> medium dark slate
        '#0f172a': '#1e293b', // dark slate block -> medium dark slate
        '#f8fafc': '#1e293b', // light slate -> medium dark slate

        // --- Tailwind border highlights (Seeded Posts) ---
        '#c7d2fe': '#312e81',
        '#e9d5ff': '#4c1d95',
        '#a7f3d0': '#064e3b',
        '#fed7aa': '#7c2d12',
        '#fecaca': '#7f1d1d',
        '#bfdbfe': '#1e3a8a',
        '#f0abfc': '#701a75',
        '#cbd5e1': '#334155',
        '#e2e8f0': '#334155',

        // --- Tailwind text highlights (Seeded Posts) ---
        '#3730a3': '#c7d2fe',
        '#1e293b': '#f1f5f9',
        '#334155': '#cbd5e1',
        '#7c3aed': '#c084fc',
        '#4c1d95': '#e9d5ff',
        '#047857': '#34d399',
        '#064e3b': '#a7f3d0',
        '#c2410c': '#fb923c',
        '#7c2d12': '#ffedd5',
        '#dc2626': '#fca5a5',
        '#7f1d1d': '#fecaca',
        '#1d4ed8': '#93c5fd',
        '#1e3a5f': '#dbeafe',
        '#a21caf': '#f472b6',
        '#701a75': '#fdf2f8',
        '#6366f1': '#818cf8',
        '#059669': '#34d399',
        '#d97706': '#fbbf24',
        '#4338ca': '#a5b4fc',
        '#475569': '#94a3b8',
        '#ef4444': '#f87171',
        '#991b1b': '#fca5a5'
    };

    // Normalize color output to lowercase hex
    function normalizeHex(color) {
        if (!color) return '';
        color = color.trim().toLowerCase();
        if (color.startsWith('rgb')) {
            const rgb = color.match(/\d+/g);
            if (rgb && rgb.length >= 3) {
                const r = parseInt(rgb[0], 10).toString(16).padStart(2, '0');
                const g = parseInt(rgb[1], 10).toString(16).padStart(2, '0');
                const b = parseInt(rgb[2], 10).toString(16).padStart(2, '0');
                return '#' + r + g + b;
            }
        }
        return color;
    }

    window.applyDarkModeTextColors = function(containerSelector) {
        if (!document.documentElement.classList.contains('dark')) return;

        const container = document.querySelector(containerSelector);
        if (!container) return;

        // 1. Text Colors
        const styledText = container.querySelectorAll('[style*="color"]');
        styledText.forEach(el => {
            const rawColor = el.style.color;
            if (!rawColor) return;
            const hex = normalizeHex(rawColor);
            if (COLOR_MAP[hex]) {
                if (!el.hasAttribute('data-original-color')) {
                    el.setAttribute('data-original-color', rawColor);
                }
                el.style.color = COLOR_MAP[hex];
            }
        });

        // 2. Background Colors
        const styledBg = container.querySelectorAll('[style*="background-color"]');
        styledBg.forEach(el => {
            const rawBg = el.style.backgroundColor;
            if (!rawBg) return;
            const hex = normalizeHex(rawBg);
            if (COLOR_MAP[hex]) {
                if (!el.hasAttribute('data-original-bg')) {
                    el.setAttribute('data-original-bg', rawBg);
                }
                el.style.backgroundColor = COLOR_MAP[hex];
            }
        });

        // 3. Borders
        const styledBorder = container.querySelectorAll('[style*="border"]');
        styledBorder.forEach(el => {
            const rawBorderColor = el.style.borderColor;
            if (rawBorderColor) {
                const hex = normalizeHex(rawBorderColor);
                if (COLOR_MAP[hex]) {
                    if (!el.hasAttribute('data-original-border-color')) {
                        el.setAttribute('data-original-border-color', rawBorderColor);
                    }
                    el.style.borderColor = COLOR_MAP[hex];
                }
            }
            if (el.style.border) {
                const hexMatch = el.style.border.match(/#[0-9a-f]{6}/gi);
                if (hexMatch) {
                    let newBorder = el.style.border;
                    let changed = false;
                    hexMatch.forEach(rawHex => {
                        const hex = normalizeHex(rawHex);
                        if (COLOR_MAP[hex]) {
                            if (!el.hasAttribute('data-original-border')) {
                                el.setAttribute('data-original-border', el.style.border);
                            }
                            newBorder = newBorder.replace(new RegExp(rawHex, 'gi'), COLOR_MAP[hex]);
                            changed = true;
                        }
                    });
                    if (changed) {
                        el.style.border = newBorder;
                    }
                }
            }
        });
    };

    window.restoreDarkModeTextColors = function(containerSelector) {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        // Restore text color
        container.querySelectorAll('[data-original-color]').forEach(el => {
            el.style.color = el.getAttribute('data-original-color');
        });

        // Restore background color
        container.querySelectorAll('[data-original-bg]').forEach(el => {
            el.style.backgroundColor = el.getAttribute('data-original-bg');
        });

        // Restore borders
        container.querySelectorAll('[data-original-border-color]').forEach(el => {
            el.style.borderColor = el.getAttribute('data-original-border-color');
        });
        container.querySelectorAll('[data-original-border]').forEach(el => {
            el.style.border = el.getAttribute('data-original-border');
        });
    };
})();
