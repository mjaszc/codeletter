/** @type {import('tailwindcss').Config} */
module.exports = {
  purge: [
        './blog/templates/blog/*.{html, js}',
        './blog/static/blog/*.js'
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
