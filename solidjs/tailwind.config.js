/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
      },
      // Mobile-optimized spacing
      spacing: {
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
        'safe-left': 'env(safe-area-inset-left)',
        'safe-right': 'env(safe-area-inset-right)',
      },
      // Touch-friendly minimum sizes
      minHeight: {
        'touch': '44px', // iOS minimum touch target
        'touch-android': '48px', // Android minimum touch target
      },
      minWidth: {
        'touch': '44px',
        'touch-android': '48px',
      },
    },
    // Mobile-first breakpoints
    screens: {
      'xs': '320px',  // Small phones
      'sm': '640px',  // Large phones
      'md': '768px',  // Tablets
      'lg': '1024px', // Desktops
      'xl': '1280px', // Large desktops
    },
  },
  plugins: [],
}
