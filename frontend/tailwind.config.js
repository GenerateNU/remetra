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
        // Brand palette — warm terracotta/peach tones
        'remetra-accent':         '#eea487',  // primary: labels, titles, links
        'remetra-peach':          '#F8B4A8',  // auth screens brand title, chart fills
        'remetra-orange':         '#fca450',  // food accent / legend dot
        'remetra-coral':          '#D9806E',  // onboarding inputs, medium intensity
        'remetra-rose':           '#C85A4A',  // onboarding text, high intensity, errors
        'remetra-burgundy':       '#B8624F',  // CTAs, save buttons, auth borders
        'remetra-terracotta':     '#ca5e5e',  // chart bar fill
        'remetra-mauve':          '#b2939b',  // screen headers, low intensity, spinners
        'remetra-espresso':       '#5C2E14',  // Dark text on gradient
        'remetra-warm-brown':     '#7A4F35',  // Warmer brown for secondary text
        // Structural / semantic
        'remetra-surface':        '#fafafa',  // input & list-item backgrounds
        'remetra-border':         '#ccc',     // generic input / card borders
        'remetra-muted':          '#aaa',     // secondary / meta text
        'remetra-surface-accent': '#fff5f0',  // selected-item card background
        'remetra-text-holder':    '#676767',  // Placeholder text
      },
      fontSize: {
        // Brand wordmark used across onboarding screens
        brand: '32px',
      },
      fontFamily: {
        lora:    ['Lora_400Regular'],
        ptserif: ['PTSerif_400Regular'],
      },
    },
  },
  plugins: [],
}