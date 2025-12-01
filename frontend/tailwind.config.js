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
                // AI-Native Palette
                cyber: {
                    // Light-first palette for the UI refresh
                    black: '#F8FAFC',       // canvas background
                    dark: '#EDF2F7',        // subtle panels / toggles
                    card: '#FFFFFF',        // main surface
                    border: '#D7DEEA',      // light borders
                    text: '#0F172A',        // primary text
                    muted: '#5B6474',       // secondary text
                    primary: '#2563EB',     // blue accent
                    secondary: '#A855F7',   // purple accent
                    accent: '#F97316',      // warm accent
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            animation: {
                'scan': 'scan 2s linear infinite',
                'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'float': 'float 6s ease-in-out infinite',
            },
            keyframes: {
                scan: {
                    '0%': { transform: 'translateY(-100%)' },
                    '100%': { transform: 'translateY(100%)' },
                },
                'pulse-glow': {
                    '0%, 100%': { opacity: 1, boxShadow: '0 0 20px rgba(0, 240, 255, 0.5)' },
                    '50%': { opacity: .5, boxShadow: '0 0 10px rgba(0, 240, 255, 0.2)' },
                },
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                }
            },
            backgroundImage: {
                'cyber-grid': "url(\"data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%231E2438' fill-opacity='0.4' fill-rule='evenodd'%3E%3Cpath d='M0 40L40 0H20L0 20M40 40V20L20 40'/%3E%3C/g%3E%3C/svg%3E\")",
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
            }
        },
    },
    plugins: [],
}
