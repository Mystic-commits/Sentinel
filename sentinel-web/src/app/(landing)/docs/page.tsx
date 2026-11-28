import CopyCommands from '@/components/landing/CopyCommands';
import { pageMetadata } from '@/lib/site';

export const metadata = pageMetadata('/docs');

export default function DocsPage() {
    return (
        <article className="site-shell site-interior">
            <h1>Developer setup.</h1>
            <p className="site-lead">Run the backend and dashboard locally in separate terminals. You’ll need Python 3.11 or 3.12, Poetry, Node.js 22, and two shell windows.</p>
            <section>
                <h2>Clone the preview branch</h2>
                <CopyCommands commands={'git clone --branch codex/production-readiness https://github.com/Mystic-commits/Sentinel.git'} />
            </section>
            <nav aria-label="Setup platforms" className="site-actions">
                <a href="#mac-linux" className="site-inline-link">macOS and Linux</a>
                <a href="#windows" className="site-inline-link">Windows PowerShell</a>
            </nav>
            <section id="mac-linux">
                <h2>macOS and Linux</h2>
                <h3>Start the local backend</h3>
                <CopyCommands commands={'cd Sentinel/sentinel-core\npoetry install\nexport SENTINEL_ACCESS_TOKEN="$(python3 -c \'import secrets; print(secrets.token_hex(32))\')"\nprintf \'%s\\n\' "$SENTINEL_ACCESS_TOKEN"\npoetry run uvicorn sentinel_core.api.main:app --host 127.0.0.1 --port 8000'} />
                <h3>Start the dashboard in a second terminal</h3>
                <CopyCommands commands={'cd Sentinel/sentinel-web\nnpm ci\nnpm run dev'} />
            </section>
            <section id="windows">
                <h2>Windows PowerShell</h2>
                <h3>Start the local backend</h3>
                <CopyCommands commands={'Set-Location Sentinel/sentinel-core\npoetry install\n$env:SENTINEL_ACCESS_TOKEN = py -3 -c "import secrets; print(secrets.token_hex(32))"\n$env:SENTINEL_ACCESS_TOKEN\npoetry run uvicorn sentinel_core.api.main:app --host 127.0.0.1 --port 8000'} />
                <h3>Start the dashboard in a second terminal</h3>
                <CopyCommands commands={'Set-Location Sentinel/sentinel-web\nnpm.cmd ci\nnpm.cmd run dev'} />
            </section>
            <section>
                <h2>Connect the dashboard</h2>
                <p>Open <a className="site-inline-link" href="http://localhost:3000/dashboard">the local dashboard</a> and paste the token shown in the backend terminal.</p>
            </section>
            <section aria-labelledby="first-plan">
                <h2 id="first-plan">Review your first move</h2>
                <p>Copy a PDF into an empty test folder. Enter the folder’s absolute path in the workspace and leave local AI off. Review the proposed destination, select the PDF, and apply the move. Open execution history to inspect the receipt or undo the move.</p>
            </section>
            <section className="setup-help" aria-labelledby="setup-help">
                <h2 id="setup-help">Setup help</h2>
                <details><summary>The dashboard can’t connect</summary><p>Keep both terminals running. Check that the backend started on port 8000 and open the dashboard on localhost port 3000. Paste the token from the current backend terminal.</p></details>
                <details><summary>My plan used rules after I enabled AI</summary><p>The preview tries the local Ollama model and falls back to rules if the model is unavailable or its plan fails validation. Custom instructions apply only to AI plans. Check the plan source before approving a move.</p></details>
                <details><summary>Undo is blocked</summary><p>Open Receipt details and compare the original and current paths. Sentinel stops recovery if the moved file has changed or its original path is occupied. Inspect both files before making a manual change.</p></details>
            </section>
            <div className="site-actions"><a className="site-text-link" href="https://github.com/Mystic-commits/Sentinel/tree/codex/production-readiness#readme">Read the repository guide ↗</a></div>
        </article>
    );
}
