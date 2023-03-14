/** @type {import('tailwindcss').Config} */
const plugin = require("tailwindcss/plugin");

module.exports = {
  content: [
    "./blog/templates/blog/*/*.{html, js}",
    "./blog/static/blog/*.{html,js}",
    "./templates/*.html",
  ],
  theme: {},
  plugins: [
    require("@tailwindcss/line-clamp"),
    plugin(function ({ addBase }) {
      addBase({
        html: { fontSize: "20px" },
      });
    }),
  ],
};
