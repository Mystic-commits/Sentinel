import '@fontsource-variable/manrope';
import '@fontsource/ibm-plex-mono/latin-400.css';
import Link from 'next/link';
import SiteMark from '@/components/landing/SiteMark';
import './website.css';

const links = [
    { href: '/features', label: 'Features' },
    { href: '/how-it-works', label: 'How it works' },
    { href: '/docs', label: 'Docs' },
];

export default function LandingLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="sentinel-site">
            <a className="site-skip" href="#page-content">Skip to content</a>
            <header className="site-header">
                <div className="site-shell site-nav">
                    <Link href="/" className="site-wordmark"><SiteMark />Sentinel</Link>
                    <nav aria-label="Main navigation">
                        {links.map(link => <Link key={link.href} href={link.href}>{link.label}</Link>)}
                    </nav>
                    <div className="site-nav-actions">
                        <Link className="site-button site-button-small" href="/download">Get Sentinel <span aria-hidden>↗</span></Link>
                    </div>
                </div>
            </header>
            <main id="page-content" tabIndex={-1}>{children}</main>
            <footer className="site-footer">
                <div className="site-shell site-footer-inner">
                    <Link href="/" className="site-wordmark"><SiteMark />Sentinel</Link>
                    <p>Open-source file organization.</p>
                    <nav aria-label="Footer navigation">
                        {links.map(link => <Link key={link.href} href={link.href}>{link.label}</Link>)}
                        <a href="https://github.com/Mystic-commits/Sentinel">GitHub ↗</a>
                    </nav>
                </div>
            </footer>
        </div>
    );
}
