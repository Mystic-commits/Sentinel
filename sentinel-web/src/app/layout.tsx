import { siteUrl } from '@/lib/site';
import type { Metadata } from "next";
import "@/styles/globals.css";

export const metadata: Metadata = { metadataBase: siteUrl };

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" className="dark">
            <body className="font-sans antialiased">
                {children}
            </body>
        </html>
    );
}
