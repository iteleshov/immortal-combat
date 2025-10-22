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
          50: '#00d4ff',
          100: '#00d4ff',
          200: '#00d4ff',
          300: '#00d4ff',
          400: '#00d4ff',
          500: '#00d4ff',
          600: '#00d4ff',
          700: '#00d4ff',
          800: '#00d4ff',
          900: '#00d4ff',
        },
        secondary: {
          50: '#2ee59d',
          100: '#2ee59d',
          200: '#2ee59d',
          300: '#2ee59d',
          400: '#2ee59d',
          500: '#2ee59d',
          600: '#2ee59d',
          700: '#2ee59d',
          800: '#2ee59d',
          900: '#2ee59d',
        },
        background: {
          DEFAULT: '#0d1117',
          card: '#161b22',
          'default': '#f0f0f0',
        },
        text: {
          primary: '#f0f6fc',
          secondary: '#8b949e',
          'primary': '#333333',
        },
        border: '#30363d',
      },
      fontFamily: {
        sans: ['Inter', 'SF Pro', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      fontWeight: {
        regular: 400,
        medium: 500,
        semibold: 600,
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
  safelist: [
    'bg-background-card',
    'text-primary',
    'bg-primary-500',
    'text-text-primary',
    'hover:bg-background-card',
    'hover:text-text-primary',
  ],
}

