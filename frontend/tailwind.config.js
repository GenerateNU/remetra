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
        'remetra-warm-brown':     '#7A4F35',  // Warmer brown for secondary
        // Structural / semantic
        'remetra-surface':        '#fafafa',  // input & list-item backgrounds
        'remetra-border':         '#ccc',     // generic input / card borders
        'remetra-muted':          '#aaa',     // secondary / meta text
        'remetra-surface-accent': '#fff5f0',  // selected-item card background
        'remetra-text-holder':    '#676767',  // Placeholder text
        // Welcome splash (Remetra v22)
        'remetra-canvas':         '#fef4ee',
        'remetra-primary':        '#b5582f',
        'remetra-text-primary':   '#3b2a24',
        'remetra-text-secondary': '#6e5a50',
        'remetra-ember':          '#c42f55',
      },
      fontSize: {
        // Brand wordmark used across onboarding screens
        brand: '32px',
      },
      fontFamily: {
        lora:              ['Lora_400Regular'],
        ptserif:           ['PTSerif_400Regular'],
        prata:             ['Prata_400Regular'],
        figtree:           ['Figtree_400Regular'],
        'figtree-semibold': ['Figtree_600SemiBold'],
      },
    },
  },
  plugins: [],
}