// tailwind.config.js
module.exports = {
  content: [
    './index.html',
    './src/**/*.vue',
  ],
  theme: {
    
    extend: {
      fontFamily: {
        AXIS: ['AXIS', 'Sans-serif'],
        JosefinSans: ['JosefinSans', 'Sans-serif']
      },
      colors: {
        'astro-guard-bg': '#00011f',
        'astro-guard-container': '#00002f',
        'astro-guard-white': "#dcedff",
        'astro-guard-green': '#21a179',
        'astro-guard-red': '#dc493a',
        'astro-guard-lilac': '#6a66a3',
      },
      keyframes: {
        RedInnerGlow: {
          '0%, 100%': { boxShadow: 'inset 0 0 50px 10px rgba(255, 0, 0, 0.8)' },
          '50%': { boxShadow: 'inset 0 0 40px 20px rgba(255, 0, 0, 0)' },
        },
        GreenInnerGlow: {
          '0%, 100%': { boxShadow: 'inset 0 0 50px 10px rgba(0, 252, 147, 0.8)' },
          '50%': { boxShadow: 'inset 0 0 40px 20px rgba(255, 0, 0, 0)' },
        },
      },
      animation: {
        RedInnerGlow: 'RedInnerGlow 2s ease-in-out infinite',
        GreenInnerGlow: 'GreenInnerGlow 1s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
