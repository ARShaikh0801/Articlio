/**@type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html",
    "./**/templates/**/*.html",
    "./static/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [require('@tailwindcss/typography'),],
  safelist: [
  'theme-darkest',
  'theme-dark',
  'theme-base',
  'theme-base-faded',
  'theme-medium',
  'theme-light',
  'theme-lightest',

  'text-color-light',
  'text-color-lightest',
  'text-color-darkest',

  'all-border',
  'card-shadow',
  'hover-card-shadow',
  'theme-medium-btn',

  'active-link',
  'link-hover-medium',
  'author-link-hover-medium',

  'filter-bar',
  'ad-sidebar',

  'post-card',
  'card-enter-animate',
  'like-bounce',
  'like-particle',
  'comment-enter-animate',
  'btn-press',
],
}