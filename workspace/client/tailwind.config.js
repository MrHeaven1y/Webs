/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#1e1e1e',
        surface: '#252526',
        border: '#3c3c3c',
        text: '#d4d4d4',
        accent: '#5c9cf5',
      },
    },
  },
  plugins: [],
};