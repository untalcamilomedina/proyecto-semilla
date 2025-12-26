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
        primary: {
          DEFAULT: "#0df20d", // emerald-500
          foreground: "#ffffff",
        },
        background: {
          light: "#f5f8f5",
          dark: "#102210",
        },
        surface: {
          glass: "rgba(255, 255, 255, 0.03)",
        },
        zinc: {
          100: "#f4f4f5",
          200: "#e4e4e7",
          500: "#71717a",
          600: "#52525b",
          900: "#18181b",
        },
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(31, 38, 135, 0.07)",
        neon: "0 0 10px rgba(13, 242, 13, 0.15), 0 0 20px rgba(13, 242, 13, 0.05)",
      },
      borderRadius: {
        xl: "12px",
        "2xl": "16px",
      },
    },
  },
  plugins: [],
};
export default config;
