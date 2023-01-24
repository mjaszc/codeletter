/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
        './blog/templates/blog/*.{html, js}',
        './blog/static/blog/*.{html,js}',
        './templates/*.html'
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
