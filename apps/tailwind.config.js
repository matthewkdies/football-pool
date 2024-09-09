/** @type {import('tailwindcss').Config} */
module.exports = {

  content: [
    "./football_pool/templates/**/*.html",
    "./football_pool/static/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('daisyui'),
  ],
}

