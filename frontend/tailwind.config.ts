import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        heading: ["var(--font-heading)"],
        body: ["var(--font-body)"],
        mono: ["var(--font-mono)"],
      },
      colors: {
        background: "hsl(var(--background) / <alpha-value>)",
        foreground: "hsl(var(--foreground) / <alpha-value>)",
        primary: {
          DEFAULT: "hsl(var(--primary) / <alpha-value>)",
          foreground: "hsl(var(--primary-foreground) / <alpha-value>)",
        },
        muted: {
          DEFAULT: "hsl(var(--muted) / <alpha-value>)",
          foreground: "hsl(var(--muted-foreground) / <alpha-value>)",
        },
        border: "hsl(var(--border) / <alpha-value>)",
        glass: {
          bg: "hsl(var(--glass-bg))",
          border: "hsl(var(--glass-border))",
        },
        // Legacy colors kept for backward compatibility with older components
        card: "hsl(var(--background) / <alpha-value>)",
        "card-foreground": "hsl(var(--foreground) / <alpha-value>)",
        neon: {
          DEFAULT: "var(--neon)",
          bg: "var(--neon-bg)",
          "bg-strong": "var(--neon-bg-strong)",
          border: "var(--neon-border)",
          text: "var(--neon-text)",
        },
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
        lg: "var(--radius-lg)",
        md: "var(--radius)",
        sm: "calc(var(--radius) - 4px)",
        full: "var(--radius-full)",
      },
      boxShadow: {
        neon: "var(--neon-glow)",
      },
    },
  },
  plugins: [],
};
export default config;
