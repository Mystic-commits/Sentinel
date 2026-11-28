import type { Metadata } from 'next';

export const siteUrl = new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://sentinel-ten-black.vercel.app');
export const publicPages = {
    '/': ['Sentinel | Local AI File Organizer', 'Organize a folder with local AI and rules. Review proposed file moves before committing them in the Sentinel developer preview.'],
    '/features': ['Local File Organization Features | Sentinel', 'Explore folder-scoped scanning, local AI suggestions, and per-file review in the open-source Sentinel file organizer.'],
    '/how-it-works': ['How Local AI File Organization Works | Sentinel', 'See how Sentinel scans a selected folder, proposes file moves, and gives you control over which changes to apply.'],
    '/download': ['Get Sentinel | File Organizer Developer Preview', 'Build Sentinel from source and check desktop release availability for the open-source local AI file organizer.'],
    '/docs': ['Sentinel Documentation | Local File Organizer Setup', 'Find developer setup and workflow documentation for Sentinel, an open-source file organizer with local rules and optional Ollama inference.'],
} as const;

export function pageMetadata(path: keyof typeof publicPages): Metadata {
    const [title, description] = publicPages[path];
    return {
        title,
        description,
        alternates: { canonical: path },
        openGraph: { title, description, url: path, siteName: 'Sentinel', type: 'website' },
    };
}
