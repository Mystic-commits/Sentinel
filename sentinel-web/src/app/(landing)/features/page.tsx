import Link from 'next/link';
import { pageMetadata } from '@/lib/site';

export const metadata = pageMetadata('/features');

export default function FeaturesPage() {
    return (
        <article className="site-shell site-interior">
            <h1>Control every move.</h1>
            <p className="site-lead">Sentinel helps you organize files one folder at a time. You review the plan before the changes reach your filesystem.</p>
            <section><h2>Folder-scoped review</h2><p>Choose a folder and see each source and destination. Approve individual moves or leave files where they are.</p></section>
            <section><h2>Local suggestions</h2><p>The developer preview uses file metadata, local rules, and optional Ollama inference to suggest destinations.</p></section>
            <section><h2>History you can act on</h2><p>Completed dashboard moves have local receipts. Undo is available for eligible moves when the files still match the receipt and the original paths are free.</p></section>
            <div className="site-actions"><Link className="site-button" href="/#sample-folder">Try the demo <span aria-hidden>↗</span></Link></div>
        </article>
    );
}
