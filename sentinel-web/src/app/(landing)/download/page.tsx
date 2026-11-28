import Link from 'next/link';
import { pageMetadata } from '@/lib/site';

export const metadata = pageMetadata('/download');

export default function DownloadPage() {
    return (
        <article className="site-shell site-interior">
            <h1>Get Sentinel.</h1>
            <p className="site-lead">Sentinel is available as a developer preview. Build it from source to try the local dashboard and terminal commands.</p>
            <section><h2>Developer preview</h2><p>Requires Python 3.11 or 3.12, Poetry, and Node.js 22. Use a disposable folder with copies of files for your first run.</p></section>
            <section><h2>Desktop installers</h2><p>The preview build produces Apple Silicon macOS and Windows x64 packages for testing. GitHub Releases lists public installer availability.</p></section>
            <div className="site-actions">
                <Link className="site-button" href="/docs">Read the setup guide <span aria-hidden>→</span></Link>
                <a className="site-text-link" href="https://github.com/Mystic-commits/Sentinel/releases">GitHub releases ↗</a>
            </div>
        </article>
    );
}
