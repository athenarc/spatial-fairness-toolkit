import { fontFamily } from 'tailwindcss/defaultTheme';
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
    "./src/*.{vue,js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        aidapt: {
          50: '#9471F1',
          100: '#865FF0',
          200: '#6A39EC',
          300: '#4E16E6',
          400: '#4213C1',
          500: '#350F9C',
          600: '#240A69',
          700: '#1C0854',
          800: '#130538',
          900: '#0D0425',
          950: '#060213',
        },
        aidaptSecondary: {
          50: '#FDD5E8',
          100: '#FDC1DD',
          200: '#FB9AC7',
          300: '#FA73B1',
          400: '#F84B9B',
          500: '#F72485',
          600: '#DB0869',
          700: '#A5064F',
          800: '#6F0435',
          900: '#39021B',
          950: '#1D010E',
        },
        ocean: '#4960E5',
        aqua: '#70C6EC',
        aidaptPurple: '#E33E84'
      },
      fontFamily: {
        sans: ['Inter var', ...fontFamily.sans],
      },
    },
  },
  plugins: [],
}

