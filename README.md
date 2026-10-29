# Sentinel

Local-first file organization with local AI planning, explicit review, and deterministic safety validation.

**Status: developer preview. Not ready for a public production launch.** See [the launch plan](docs/PRODUCTION_PLAN.md) for B2C and B2B release gates.

## Run locally

Requires Python 3.11/3.12, Poetry, Node 20.9+, and Ollama. Clone this repository before running these commands.

```sh
cd sentinel-core
poetry install
# In another terminal, start Ollama and download the selected local model.
ollama pull qwen3:4b
SENTINEL_OLLAMA_MODEL=qwen3:4b poetry run python -m sentinel_core.api.main
```

```sh
cd sentinel-web
npm ci
npm run dev
```

Open http://localhost:3000. The API defaults to 127.0.0.1:8000. Do not expose this local filesystem agent as a public service.

## Local models

Set `SENTINEL_OLLAMA_MODEL`, `SENTINEL_OLLAMA_URL` (loopback only), and `SENTINEL_OLLAMA_TIMEOUT`. The API defaults to `qwen3:4b` with a 120-second timeout. Configure the Ollama service with `OLLAMA_NO_CLOUD=1` and use a downloaded local model. No model download runs automatically.

Ollama supports JSON-schema constrained output ([API reference](https://docs.ollama.com/api/generate)). Plans remain untrusted: the application restores the scan scope, rejects references to unscanned sources, and validates again before file mutation.

Qwen3 4B is an initial evaluation candidate; hardware performance and plan quality still need measurement. Existing Llama 2 also works through `SENTINEL_OLLAMA_MODEL=llama2`. Model licensing must be checked for the exact distributed model.

## Verification

```sh
cd sentinel-core
poetry run pytest
```

```sh
cd sentinel-web
npm run type-check
npm run build
npm audit
```

Run the whole Python suite, including safety and executor tests. Tests use temporary fixtures; Trash integration is mocked.

## Safety and limitations

- Review selected actions before execution; the API requires explicit action indices and rejects execution replay.
- Scope escapes, existing destinations, missing sources, and directory deletion are rejected. The scanner skips symlinks.
- Deletes use system Trash. Automatic restoration of Trash deletions is unavailable.
- The web API persists plans, approvals, timestamps, results and operation receipts in SQLite. Set `SENTINEL_TASK_DATABASE_PATH` to change its default `~/.sentinel/api-tasks.sqlite3` location. Run one API process per database: multi-worker deployment is unsupported. Interrupted jobs are flagged for manual review and never automatically replayed.
- API execution requires a durable claim and a started receipt before each selected operation. Receipts identify attempted/completed operations; they are not tamper-proof audit evidence. A process crash between mutation and completion can leave an uncertain outcome requiring manual inspection. CLI execution still needs equivalent mandatory audit integration.
- API undo returns an explicit unavailable response until persistence is integrated.
- Local origin/host checks reduce browser cross-origin access; device pairing and race-resistant filesystem operations still need implementation.
- Desktop installers are placeholders. Signed release artifacts are not available.
- Team membership, roles, tenant isolation, billing, and managed deployment are not implemented.

## Components

`sentinel-core`: scanner, classifier, planner, safety engine, executor, FastAPI, CLI.
`sentinel-web`: Next.js dashboard and website, Tauri desktop sources.
`sentinel-api` and `sentinel-cli`: legacy shells requiring consolidation.

MIT licensed; see [LICENSE](LICENSE).
