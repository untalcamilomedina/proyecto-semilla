import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: {
          DEFAULT: "var(--primary)",
          foreground: "var(--primary-foreground)",
        },
        secondary: {
          DEFAULT: "var(--secondary)",
          foreground: "var(--secondary-foreground)",
        },
        muted: {
          DEFAULT: "var(--muted)",
          foreground: "var(--muted-foreground)",
        },
        accent: {
          DEFAULT: "var(--accent)",
          foreground: "var(--accent-foreground)",
        },
        card: {
          DEFAULT: "var(--card)",
          foreground: "var(--card-foreground)",
        },
        popover: {
          DEFAULT: "var(--popover)",
          foreground: "var(--popover-foreground)",
        },
        border: "var(--border)",
        input: "var(--input)",
        ring: "var(--ring)",
        neon: {
          DEFAULT: "var(--neon)",
          bg: "var(--neon-bg)",
          "bg-strong": "var(--neon-bg-strong)",
          border: "var(--neon-border)",
          text: "var(--neon-text)",
        },
        glass: {
          bg: "var(--glass-bg)",
          "bg-hover": "var(--glass-bg-hover)",
          "bg-strong": "var(--glass-bg-strong)",
          border: "var(--glass-border)",
          "border-subtle": "var(--glass-border-subtle)",
          overlay: "var(--glass-overlay)",
          "overlay-strong": "var(--glass-overlay-strong)",
        },
        "text-secondary": "var(--text-secondary)",
        "text-tertiary": "var(--text-tertiary)",
        "text-quaternary": "var(--text-quaternary)",
        "text-ghost": "var(--text-ghost)",
        "text-highlight": "var(--text-highlight)",
        "text-subtle": "var(--text-subtle)",
        error: {
          bg: "var(--error-bg)",
          border: "var(--error-border)",
          text: "var(--error-text)",
        },
        success: {
          text: "var(--success-text)",
        },
        warning: {
          bg: "var(--warning-bg)",
          border: "var(--warning-border)",
          text: "var(--warning-text)",
        },
        surface: {
          page: "var(--surface-page)",
          raised: "var(--surface-raised)",
          overlay: "var(--surface-overlay)",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      boxShadow: {
        neon: "var(--neon-glow)",
      },
    },
  },
  plugins: [],
};
export default config;
