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
            colors: {
                surface: {
                    0: "#000000",
                    1: "#0c0c0c",
                    2: "#141414",
                    3: "#1c1c1c",
                },
                edge: {
                    DEFAULT: "#222",
                    hover: "#333",
                    strong: "#444",
                },
                txt: {
                    primary: "#ededed",
                    secondary: "#999",
                    muted: "#666",
                    faint: "#444",
                },
            },
            fontFamily: {
                sans: ["var(--font-inter)", "Inter", "-apple-system", "system-ui", "sans-serif"],
                mono: ["var(--font-jetbrains)", "JetBrains Mono", "SF Mono", "monospace"],
            },
            animation: {
                'fade-in': 'fadeIn 0.3s ease-out',
                'slide-up': 'slideUp 0.3s ease-out',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(8px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
            },
        },
    },
    plugins: [],
};

export default config;
