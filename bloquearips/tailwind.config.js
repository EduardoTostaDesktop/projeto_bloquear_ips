/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/templates/**/*.html', // escaneia todos os templates
    './**/static/**/*.js',      // escaneia JS se tiver Tailwind classes
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
