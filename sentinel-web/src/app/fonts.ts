/**
 * Typography Configuration
 * 
 * Loads Inter (UI/display) and JetBrains Mono (code/monospace) from Google Fonts.
 */

import { Inter, JetBrains_Mono } from 'next/font/google';

export const inter = Inter({
    subsets: ['latin'],
    variable: '--font-inter',
    display: 'swap',
    weight: ['400', '500', '600', '700'],
});

export const jetbrainsMono = JetBrains_Mono({
    subsets: ['latin'],
    variable: '--font-jetbrains',
    display: 'swap',
    weight: ['400', '500', '700'],
});
