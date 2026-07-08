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
  'post-card-inner',
  'post-card-header',
  'post-card-tags',
  'post-card-title',
  'post-card-author',
  'post-card-summary',
  'post-card-footer',
  'post-card-read-link',
  'card-enter-animate',

  'category-pill',
  'stat-chip',
  'stats-row',
  'stat-separator',
  'badge-new',
  'badge-trending',

  'hero-section',
  'hero-title',
  'hero-subtitle',
  'hero-cta-group',
  'hero-cta-primary',
  'hero-cta-secondary',
  'hero-shape',

  'skeleton-card',
  'skeleton-bar',

  'section-heading',
  'section-heading-icon',
  'blog-header',

  'like-bounce',
  'like-particle',
  'comment-enter-animate',
  'btn-press',
],
}