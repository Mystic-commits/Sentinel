import Link from 'next/link';
import { pageMetadata } from '@/lib/site';
import Hero from '@/components/landing/Hero';

export const metadata = pageMetadata('/');

export default function Home() {
    return (
        <>
            <Hero />
            <section className="site-shell site-workflow" aria-labelledby="workflow-title">
                <h2 id="workflow-title">See what changes.<br />Decide what moves.</h2>
                <div className="site-steps">
                    <article><h3>Choose a folder</h3><p>Start with a single folder, such as Downloads, and scan its inventory.</p></article>
                    <article><h3>Review the plan</h3><p>See each proposed destination and approve the moves you want.</p></article>
                    <article><h3>Restore from history</h3><p>Reopen the workspace and undo eligible moves, even after restarting.</p></article>
                </div>
                <Link className="site-text-link" href="/how-it-works">Explore the workflow <span aria-hidden>→</span></Link>
            </section>
        </>
    );
}
