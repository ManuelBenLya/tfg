/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        main: "var(--main-color)",
        title: "var(--title-color)",
        text: "var(--text-color)",
        light: "var(--light-text-color)",
        body: "var(--body-color)",
        surface: "var(--surface-color)",
        border: "var(--border-color)",
      }
    },
  },
  plugins: [],
};