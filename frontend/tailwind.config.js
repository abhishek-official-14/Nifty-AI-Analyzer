/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        panel: '#0f172a',
        panelSoft: '#1e293b',
        accent: '#38bdf8',
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(56, 189, 248, 0.25), 0 8px 30px rgba(15, 23, 42, 0.35)',
      },
    },
  },
  plugins: [],
};
