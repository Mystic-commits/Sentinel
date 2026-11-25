import CopyCommands from '@/components/landing/CopyCommands';
import { pageMetadata } from '@/lib/site';

export const metadata = pageMetadata('/docs');

export default function DocsPage() {
    return (
        <article className="site-shell site-interior">
            <h1>Developer setup.</h1>
            <p className="site-lead">Run the backend and dashboard locally in separate terminals. Start with a disposable folder containing copies of files.</p>
            <section>
                <h2>Clone the project</h2>
                <CopyCommands commands={'git clone https://github.com/Mystic-commits/Sentinel.git'} />
            </section>
            <section>
                <h2>Start the local backend</h2>
                <CopyCommands commands={'cd Sentinel/sentinel-core\npoetry install\nexport SENTINEL_ACCESS_TOKEN="$(python3 -c \'import secrets; print(secrets.token_hex(32))\')"\nprintf \'%s\\n\' "$SENTINEL_ACCESS_TOKEN"\npoetry run uvicorn sentinel_core.api.main:app --host 127.0.0.1 --port 8000'} />
            </section>
            <section>
                <h2>Start the dashboard</h2>
                <CopyCommands commands={'cd Sentinel/sentinel-web\nnpm ci\nnpm run dev'} />
                <p>Open <code>http://localhost:3000/dashboard</code> and paste the token shown in the backend terminal.</p>
            </section>
            <div className="site-actions"><a className="site-text-link" href="https://github.com/Mystic-commits/Sentinel#readme">Read the repository guide ↗</a></div>
        </article>
    );
}
