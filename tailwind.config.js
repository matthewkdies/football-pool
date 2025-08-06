/** @type {import('tailwindcss').Config} */
module.exports = {

  content: [
    "./apps/football_pool/templates/**/*.html",
    "./apps/football_pool/static/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('daisyui'),
  ],
}
