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
        // Apple Wallet inspired dark theme colors
        wallet: {
          bg: '#000000',
          surface: '#1C1C1E',
          surfaceElevated: '#2C2C2E',
          border: '#38383A',
          text: {
            primary: '#FFFFFF',
            secondary: '#98989D',
            tertiary: '#636366',
          },
          accent: {
            blue: '#0A84FF',
            green: '#32D74B',
            orange: '#FF9F0A',
            red: '#FF453A',
            purple: '#BF5AF2',
            pink: '#FF375F',
          },
        },
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          'sans-serif',
        ],
      },
      boxShadow: {
        'card': '0 4px 12px rgba(0, 0, 0, 0.5)',
        'card-hover': '0 8px 24px rgba(0, 0, 0, 0.6)',
        'glow-blue': '0 0 20px rgba(10, 132, 255, 0.3)',
        'glow-green': '0 0 20px rgba(50, 215, 75, 0.3)',
      },
      backdropBlur: {
        'wallet': '40px',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'slide-down': 'slideDown 0.4s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
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
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
