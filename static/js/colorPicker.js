function hexToHSL(hex) {
    hex = hex.replace('#', '');

    let r = parseInt(hex.substring(0, 2), 16) / 255;
    let g = parseInt(hex.substring(2, 4), 16) / 255;
    let b = parseInt(hex.substring(4, 6), 16) / 255;

    let max = Math.max(r, g, b);
    let min = Math.min(r, g, b);
    let delta = max - min;

    let h = 0;
    let s = 0;
    let l = (max + min) / 2;

    if (delta !== 0) {
        s = delta / (1 - Math.abs(2 * l - 1));

        switch (max) {
            case r:
                h = ((g - b) / delta) % 6;
                break;
            case g:
                h = (b - r) / delta + 2;
                break;
            case b:
                h = (r - g) / delta + 4;
                break;
        }

        h = Math.round(h * 60);
        if (h < 0) h += 360;
    }

    return {
        h,
        s: Math.round(s * 100),
        l: Math.round(l * 100)
    };
}

function applyThemeFromHex(hex) {
    const { h, s, l } = hexToHSL(hex);

    const theme = {
        "--theme-base": `hsl(${h}, ${s}%, ${l}%)`,
        "--theme-darkest": `hsl(${h}, ${s}%, ${(l - 30 + 100) % 100}%)`,
        "--theme-dark": `hsl(${h}, ${s}%, ${(l - 20 + 100) % 100}%)`,
        "--theme-medium": `hsl(${h}, ${s}%, ${(l - 10 + 100) % 100}%)`,
        "--theme-base-faded": `hsl(${h}, ${s}%, ${l}%, 0.6)`,
        "--theme-light": `hsl(${h}, ${s}%, ${(l + 30) % 100}%)`,
        "--theme-lightest": `hsl(${h}, ${s}%, ${(l + 40) % 100}%)`
    };

    for (const key in theme) {
        document.documentElement.style.setProperty(key, theme[key]);
    }
}

const DEFAULT_COLOR = "#2e8ab8";
const colorPicker = document.getElementById('colorPicker');
const colorReseter = document.getElementById('colorReseter');

if (colorReseter && colorPicker) {
    colorReseter.addEventListener('click', function () {
        colorPicker.value = DEFAULT_COLOR;
        applyThemeFromHex(DEFAULT_COLOR);

        if (`${window.CURRENT_USER}` !== "") {
            localStorage.setItem(`${window.CURRENT_USER}_baseTheme`, JSON.stringify(DEFAULT_COLOR));
        } else {
            sessionStorage.setItem('baseTheme', JSON.stringify(DEFAULT_COLOR));
        }

        colorReseter.classList.add('hidden');
    });
}

if (colorPicker && colorReseter) {
    colorPicker.addEventListener('input', function () {
        const selectedColor = colorPicker.value;

        applyThemeFromHex(selectedColor);

        selectedColor === DEFAULT_COLOR
            ? colorReseter.classList.add('hidden')
            : colorReseter.classList.remove('hidden');

        if (`${window.CURRENT_USER}` !== "") {
            localStorage.setItem(`${window.CURRENT_USER}_baseTheme`, JSON.stringify(selectedColor));
        } else {
            sessionStorage.setItem('baseTheme', JSON.stringify(selectedColor));
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    let savedColor = DEFAULT_COLOR;

    if (`${window.CURRENT_USER}` !== "") {
        savedColor = JSON.parse(
            localStorage.getItem(`${window.CURRENT_USER}_baseTheme`)
        ) || DEFAULT_COLOR;
    } else {
        savedColor = JSON.parse(
            sessionStorage.getItem('baseTheme')
        ) || DEFAULT_COLOR;
    }

    if (colorPicker) colorPicker.value = savedColor;
    applyThemeFromHex(savedColor);

    if (colorReseter) {
        savedColor === DEFAULT_COLOR
            ? colorReseter.classList.add('hidden')
            : colorReseter.classList.remove('hidden');
    }
});
