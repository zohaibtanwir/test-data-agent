import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Macy's Brand Colors
        'macys-red': '#CE0037',
        'macys-red-dark': '#A8002C',
        'macys-red-light': '#E53E3E',
        'macys-black': '#000000',
        'macys-gray-dark': '#333333',
        'macys-gray': '#666666',
        'macys-gray-light': '#999999',
        'macys-gray-lighter': '#E5E5E5',
        'macys-white': '#FFFFFF',

        // Backgrounds
        'bg-primary': '#FFFFFF',
        'bg-secondary': '#F7F7F7',
        'bg-tertiary': '#E5E5E5',
        'bg-elevated': '#FFFFFF',

        // Borders
        'border-default': '#E5E5E5',
        'border-light': '#F0F0F0',

        // Text
        'text-primary': '#000000',
        'text-secondary': '#333333',
        'text-muted': '#666666',

        // Accent (Macy's red)
        accent: {
          DEFAULT: '#CE0037',
          hover: '#A8002C',
          muted: 'rgba(206, 0, 55, 0.1)',
          foreground: '#ffffff',
        },

        // Status
        warning: '#FFB000',
        error: '#CE0037',
        info: '#0062CC',

        // shadcn defaults
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))'
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))'
        },
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))'
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))'
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))'
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))'
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        chart: {
          '1': 'hsl(var(--chart-1))',
          '2': 'hsl(var(--chart-2))',
          '3': 'hsl(var(--chart-3))',
          '4': 'hsl(var(--chart-4))',
          '5': 'hsl(var(--chart-5))'
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '6px',
        lg: 'var(--radius)',
        xl: '12px',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)'
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
export default config;