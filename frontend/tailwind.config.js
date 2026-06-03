/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        krishna: {
          50: '#F0F4FB',
          100: '#D4E3F7',
          200: '#A8C8EF',
          300: '#7CAAE7',
          400: '#5D94E1',
          500: '#4F77D8',
          600: '#3D5FBF',
          700: '#2F47A6',
          800: '#1F2F7D',
          900: '#141B54',
        },
        peacock: {
          50: '#F0FDFA',
          100: '#CCFBF1',
          200: '#99F6E4',
          300: '#5EEAD4',
          400: '#2DD4BF',
          500: '#14B8A6',
          600: '#0D9488',
          700: '#0F766E',
          800: '#115E59',
          900: '#134E4A',
        },
        saffron: {
          50: '#FFFBEB',
          100: '#FEF3C7',
          200: '#FDE68A',
          300: '#FCD34D',
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706',
          700: '#B45309',
          800: '#92400E',
          900: '#78350F',
        },
      },
      backgroundImage: {
        'gradient-krishna': 'linear-gradient(135deg, #4F77D8 0%, #2F47A6 100%)',
        'gradient-peacock': 'linear-gradient(135deg, #14B8A6 0%, #0D9488 100%)',
        'gradient-divine': 'linear-gradient(135deg, #8B5CF6 0%, #4F77D8 50%, #14B8A6 100%)',
      },
      animation: {
        'feather-float': 'featherFloat 6s ease-in-out infinite',
        'glow-pulse': 'glowPulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        featherFloat: {
          '0%, 100%': { transform: 'translateY(0px) rotate(0deg)', opacity: '0.3' },
          '50%': { transform: 'translateY(-20px) rotate(180deg)', opacity: '0.1' },
        },
        glowPulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
      },
    },
  },
  plugins: [],
}
