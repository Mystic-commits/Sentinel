import { execFileSync } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = new URL('../../', import.meta.url);
const core = fileURLToPath(new URL('sentinel-core/', root));
const binaries = fileURLToPath(new URL('sentinel-web/src-tauri/binaries/', root));
const prompt = fileURLToPath(new URL('sentinel-core/sentinel_core/planner/planner_prompt.txt', root));
const build = fileURLToPath(new URL('sentinel-core/build/desktop/', root));
const target = execFileSync('rustc', ['-vV'], { encoding: 'utf8' }).match(/^host: (.+)$/m)?.[1].trim();

if (!target) throw new Error('Cannot identify the native Rust target');
mkdirSync(binaries, { recursive: true });
mkdirSync(build, { recursive: true });

execFileSync('poetry', [
    'run', 'pyinstaller', '--noconfirm', '--onefile', '--noupx',
    '--name', `sentinel-backend-${target}`, '--distpath', binaries,
    '--workpath', build, '--specpath', build,
    '--paths', core,
    '--add-data', `${prompt}:sentinel_core/planner`,
    '--hidden-import', 'uvicorn.logging', '--hidden-import', 'uvicorn.loops.auto',
    '--hidden-import', 'uvicorn.protocols.http.auto', '--hidden-import', 'uvicorn.protocols.websockets.auto',
    '--hidden-import', 'uvicorn.lifespan.on',
    'sentinel_core/desktop_backend.py',
], { cwd: core, stdio: 'inherit' });
