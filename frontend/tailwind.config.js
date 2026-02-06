/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./App.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  presets: [require('nativewind/preset')],
  theme: {
    extend: {
      colors: {
        'remetra-peach': '#F8B4A8',
        'remetra-orange': '#fca450',
        'remetra-coral': '#D9806E',
        'remetra-rose': '#C85A4A',
        'remetra-burgundy': '#B8624F',
        'remetra-terracotta': '#ca5e5e',
        'remetra-mauve': '#b2939b',
      },
    },
  },
  plugins: [],
}