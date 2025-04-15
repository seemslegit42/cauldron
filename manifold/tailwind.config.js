/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#4dabf5',
          DEFAULT: '#1890ff',
          dark: '#096dd9',
        },
        secondary: {
          light: '#f6ffed',
          DEFAULT: '#52c41a',
          dark: '#389e0d',
        },
        danger: {
          light: '#fff1f0',
          DEFAULT: '#f5222d',
          dark: '#cf1322',
        },
        warning: {
          light: '#fffbe6',
          DEFAULT: '#faad14',
          dark: '#d48806',
        },
        info: {
          light: '#e6f7ff',
          DEFAULT: '#1890ff',
          dark: '#096dd9',
        },
        success: {
          light: '#f6ffed',
          DEFAULT: '#52c41a',
          dark: '#389e0d',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Roboto Mono', 'monospace'],
      },
      boxShadow: {
        card: '0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px 0 rgba(0, 0, 0, 0.02)',
        dropdown: '0 6px 16px 0 rgba(0, 0, 0, 0.08), 0 3px 6px -4px rgba(0, 0, 0, 0.12), 0 9px 28px 8px rgba(0, 0, 0, 0.05)',
      },
    },
  },
  plugins: [],
  // Disable Tailwind's default preflight styles to avoid conflicts with Ant Design
  corePlugins: {
    preflight: false,
  },
}