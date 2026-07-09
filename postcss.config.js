const autoprefixer = require("autoprefixer");
const { plugin } = require("postcss");

module.exports={
  plugins:{
    '@tailwindcss/postcss':{},
    autoprefixer:{},
    cssnano: process.env.NODE_ENV === 'production' ? {
      preset: ['default', {
        calc: false,
      }],
    } : false,
  },
}
