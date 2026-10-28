/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#F5F8FC',
          900: '#FFFFFF',
          850: '#FFFFFF',
          800: '#E2E8F0',
          700: '#CBD5E1',
          600: '#94A3B8',
        },
        brand: {
          cyan: '#0D9488',
          blue: '#2563EB',
          accent: '#0D9488',
          emerald: '#15803D',
          amber: '#D97706',
          rose: '#DC2626',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
