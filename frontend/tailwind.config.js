/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1a73e8',
          light: '#e8f0fe',
          dark: '#1557b0',
        },
      },
    },
  },
  plugins: [],
}
