/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
     extend: {
      colors: {
        primary: {
          50: '#ecfff5',
          100: '#d1ffe8',
          200: '#a3ffd1',
          300: '#6dffb5',
          400: '#2eff95',
          500: '#00ff88', // main neon green
          600: '#00cc6a',
          700: '#00994f',
          800: '#006b38',
          900: '#003d20',
        },

        secondary: {
          50: '#fff4ed',
          100: '#ffe6d5',
          200: '#ffccaa',
          300: '#ffad75',
          400: '#ff8a3d',
          500: '#ff6b00', // cyber orange
          600: '#e65f00',
          700: '#b84b00',
          800: '#803400',
          900: '#4d1f00',
        },

        success: {
          50: '#ecfff5',
          100: '#d1ffe8',
          200: '#a3ffd1',
          300: '#6dffb5',
          400: '#2eff95',
          500: '#00ff88',
          600: '#00cc6a',
          700: '#00994f',
          800: '#006b38',
          900: '#003d20',
        },

        warning: {
          50: '#fff8eb',
          100: '#ffedc2',
          200: '#ffdb85',
          300: '#ffc247',
          400: '#ffaa1f',
          500: '#ff8800',
          600: '#db7300',
          700: '#b35e00',
          800: '#804300',
          900: '#4d2800',
        },

        danger: {
          50: '#fff1f1',
          100: '#ffd6d6',
          200: '#ffb3b3',
          300: '#ff8080',
          400: '#ff4d4d',
          500: '#ff3b30', // hacker red
          600: '#e62e24',
          700: '#b8221b',
          800: '#801813',
          900: '#4d0d0a',
        },

        neutral: {
          50: '#f5f5f5',
          100: '#d9d9d9',
          200: '#bfbfbf',
          300: '#a6a6a6',
          400: '#8c8c8c',
          500: '#737373',
          600: '#404040',
          700: '#262626',
          800: '#121212',
          900: '#050505', // deep hacker black
        }
      },
      fontFamily: {
        sans: ['"JetBrains Mono"', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.875rem' }],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'scale-x': 'scaleX 0.3s ease-out',
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 1.5s ease-in-out infinite',
        'shake': 'shake 0.5s ease-in-out',
        'toast-slide-in': 'toastSlideIn 0.3s ease-out',
        'bounce-slow': 'bounce 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        scaleX: {
          '0%': { transform: 'scaleX(0)' },
          '100%': { transform: 'scaleX(1)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '10%, 30%, 50%, 70%, 90%': { transform: 'translateX(-4px)' },
          '20%, 40%, 60%, 80%': { transform: 'translateX(4px)' },
        },
        toastSlideIn: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
      },
      transitionDuration: {
        '0': '0ms',
        '2000': '2000ms',
        '3000': '3000ms',
      },
      backdropBlur: {
        xs: '2px',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}