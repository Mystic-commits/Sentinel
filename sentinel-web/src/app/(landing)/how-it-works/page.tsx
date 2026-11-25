import Link from 'next/link';
import { pageMetadata } from '@/lib/site';

export const metadata = pageMetadata('/how-it-works');

export default function WorkflowPage() {
    return (
        <article className="site-shell site-interior">
            <h1>From folder to file plan.</h1>
            <p className="site-lead">Try the workflow with the public demo, then use a disposable folder when testing the developer preview.</p>
            <section><h2>1. Scan a folder</h2><p>Enter an absolute folder path. Sentinel reads metadata and proposes destinations within the selected folder.</p></section>
            <section><h2>2. Choose what moves</h2><p>Check the source and proposed destination of each file. Apply only the operations you approve. Sentinel rechecks reviewed files before execution.</p></section>
            <section><h2>3. Revisit the receipt</h2><p>Open execution history to see completed moves. Eligible changes can be restored after restarting the backend.</p></section>
            <div className="site-actions"><Link className="site-button" href="/#sample-folder">Open the sample <span aria-hidden>↗</span></Link></div>
        </article>
    );
}
