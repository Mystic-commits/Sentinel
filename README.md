# Sentinel

Sentinel is a local-first file organizer in developer preview. It scans a folder, proposes changes using organization rules and an optional local Ollama model, and shows the proposed moves and renames for review. The dashboard submits the selected actions to the local backend.

## Try the developer preview

Use a disposable folder with copies of files. Start the backend and dashboard in separate terminals from the checkout. The project uses Python 3.11 or 3.12, Poetry, and Node.js 22.

```sh
cd sentinel-core
poetry install
export SENTINEL_ACCESS_TOKEN="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
printf '%s\n' "$SENTINEL_ACCESS_TOKEN"
poetry run uvicorn sentinel_core.api.main:app --host 127.0.0.1 --port 8000
```

```sh
cd sentinel-web
npm ci
npm run dev
```

Open [the local dashboard](http://localhost:3000/dashboard), enter the access token printed in the backend terminal, then enter the absolute path of your sample folder, and review the plan before applying any changes. The planning pipeline currently targets the local Ollama service using `llama2` and can fall back to rules. Folder selection determines scope. The dashboard's description and mode controls are still preview UI and do not drive planning.

Use `poetry run sentinel --help` from `sentinel-core` to inspect the CLI. Download availability is listed on the [public site](https://sentinel-ten-black.vercel.app/download).

## Repository layout

| Path | Responsibility |
| --- | --- |
| `sentinel-core/sentinel_core` | Scanner, planner, rules, safety validator, executor, local FastAPI app, and CLI |
| `sentinel-core/tests` | Core and API tests |
| `sentinel-web` | Public site, local review dashboard, and experimental Tauri launcher |
| `docs` | Project design material |

## Release status

Run the development service on loopback only. The local dashboard uses a single-user access token for HTTP and WebSocket requests. The experimental desktop launcher inherits the token when launched from the configured shell. Automated desktop pairing, per-session event isolation, durable task history and undo, stale-file detection, filesystem race handling, and resource limits need further work. The developer dashboard can apply selected moves and renames. Its task state lives in memory, and API undo returns a feature-unavailable error. Signed desktop installers and a supported package-registry installation remain release milestones.

## Checks

From `sentinel-core`, run `poetry run pytest`. From `sentinel-web`, run `npm run type-check`, `npm run lint`, and `npm run build`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution information and [LICENSE](LICENSE) for license terms.
