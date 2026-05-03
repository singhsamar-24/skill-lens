import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#101114",
        muted: "#667085",
        line: "#E6E8EC",
        accent: "#0F9F6E",
        mint: "#0F9F6E",
        amber: "#B7791F"
      },
      boxShadow: {
        soft: "0 20px 60px rgba(16, 17, 20, 0.08)",
        tight: "0 10px 30px rgba(16, 17, 20, 0.08)"
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "Segoe UI", "sans-serif"]
      }
    }
  },
  plugins: []
} satisfies Config;
