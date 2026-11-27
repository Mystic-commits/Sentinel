# Sentinel

Sentinel is a local-first file organizer in developer preview. It scans a folder, proposes changes using organization rules and an optional local Ollama model, and shows the proposed moves and renames for review. The dashboard submits the selected actions to the local backend.

## Try the developer preview

Check out the codex/production-readiness preview branch. Use a disposable folder with copies of files. Start the backend and dashboard in separate terminals from the checkout. The project uses Python 3.11 or 3.12, Poetry, and Node.js 22.

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

Open [the local dashboard](http://localhost:3000/dashboard), enter the access token printed in the backend terminal, then enter the absolute path of your sample folder, and review the plan before applying any changes. The planning pipeline currently targets the local Ollama service using `llama2` and can fall back to rules. Folder selection determines scope.

The dashboard uses local rules by default. Enable **Use local AI (Ollama)** to send folder metadata and optional instructions to your local model. The review identifies the source of the plan, including when Sentinel falls back to rules.

### Review and apply a plan from the terminal

Run these commands from `sentinel-core`. Substitute the task ID printed by the plan command and the action numbers you want to approve.

```sh
poetry run sentinel plan /absolute/path/to/sample-folder --rules-only
poetry run sentinel apply TASK_ID --dry-run
poetry run sentinel apply TASK_ID --action 1
poetry run sentinel undo TASK_ID
```

Repeat `--action` to approve multiple changes. Omitting it selects the entire displayed plan and prompts for confirmation. Leave off `--rules-only` to try local Ollama, or use `--no-save` to print a plan without persisting it. Saved plans and execution receipts use the local Sentinel SQLite database.

Use `sentinel clean-pc` to create rules-based plans for Downloads, Desktop, and Documents, or pass repeated `--location` options. Add `--execute` to review and confirm each folder before moving files. Use `sentinel scan --verbose` to list the ten largest files reached by the scan. These commands run through `poetry run` from the backend directory.

Use `poetry run sentinel --help` to see all commands. Download availability is listed on the [public site](https://sentinel-ten-black.vercel.app/download).

## Repository layout

| Path | Responsibility |
| --- | --- |
| `sentinel-core/sentinel_core` | Scanner, planner, rules, safety validator, executor, local FastAPI app, and CLI |
| `sentinel-core/tests` | Core and API tests |
| `sentinel-web` | Public site, local review dashboard, and experimental Tauri launcher |
| `docs` | Project design material |

## Release status

Run the development service on loopback only. The local dashboard uses a single-user access token for HTTP and WebSocket requests. The desktop preview can bundle the local backend and pair automatically. See the [desktop build guide](sentinel-web/BUILDING.md). Per-session event isolation, filesystem race handling, and hard timeouts for blocked filesystem calls need further work. The developer dashboard can apply selected moves and renames. Pending plans live in memory. Completed dashboard moves have SQLite receipts. Use **Show execution history** to undo eligible moves after restarting the backend. Undo blocks if a file changed or an original path is occupied. Apply and undo require a single filesystem that supports exclusive renames. Sentinel refuses to replace an existing destination even if it appears during the operation. Each move has a durable receipt entry. After an interruption, **Receipt details** shows which moves were confirmed, which had not started, and which need manual inspection. A partially applied task can undo its confirmed moves. Sentinel leaves interrupted jobs for review rather than replaying them automatically. The API and terminal share one writer lock when they use the same local database. Signed desktop installers and a supported package-registry installation remain release milestones.

## Checks

From `sentinel-core`, run `poetry run pytest`. From `sentinel-web`, run `npm run type-check`, `npm run lint`, and `npm run build`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution information and [LICENSE](LICENSE) for license terms.

## Public site search setup

The static export includes canonical URLs, page-specific search metadata, a sitemap, and crawler instructions. It keeps the local dashboard out of search results. The canonical origin defaults to the existing Vercel site. If the production hostname changes, set `NEXT_PUBLIC_SITE_URL` before building.

After deploying, submit `/sitemap.xml` in Google Search Console for the verified production property. Use the Page indexing and Performance reports to track discovery and search clicks.

## Local job limits

The API accepts one scan or plan at a time per backend process. Additional scan or plan requests receive HTTP 429 with a `Retry-After` header. Authenticated write requests also share a rolling limit of 30 per minute.

API scans stop after 10,000 directory entries or a cooperative 15-second budget. Plans derived from a partial scan are marked as partial. Planning uses local rules for inventories over 250 files. These limits apply to the local API preview.
