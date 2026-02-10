import type { Metadata } from "next";
import { inter, jetbrainsMono } from "./fonts";
import "@/styles/globals.css";

export const metadata: Metadata = {
    title: "Sentinel — AI File Organization",
    description: "Local-first AI agent for safe, intelligent file organization",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" className="dark">
            <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
                {children}
            </body>
        </html>
    );
}
