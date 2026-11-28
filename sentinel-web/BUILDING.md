# Build the Sentinel desktop preview

The Tauri app opens the local workspace, launches the packaged FastAPI backend, and pairs with it automatically. PyInstaller includes the Python runtime and Sentinel's backend dependencies. The app works with local rules when Ollama is unavailable.

## Prerequisites

- Node.js 22, Python 3.12, Poetry 2.3.4, and stable Rust for the native target.
- macOS 12 or newer with Xcode command-line tools. Build on Apple Silicon for arm64 or on Intel for x86-64.
- Windows with Microsoft C++ Build Tools and WebView2 for the Windows build.

Build on the target OS and architecture. The frozen backend and desktop binary must match.

## Build

From the repository checkout, install the backend and its optional packaging dependencies.

```sh
cd sentinel-core
poetry install --with desktop
cd ../sentinel-web
npm ci
```

Build the native preview for the OS you are using.

```sh
# macOS
npm run tauri:build:mac

# Windows
npm run tauri:build:win
```

Find bundle artifacts under `sentinel-web/src-tauri/target/release/bundle`. For development, `npm run tauri:dev` builds the same backend and opens the local dashboard.

## Validate a candidate

1. Install or open the bundle on a clean machine of the advertised architecture.
2. Confirm the workspace opens without a system Python installation or a manual token.
3. Use a disposable folder and verify scan, review, apply, and undo.
4. Quit Sentinel and confirm its backend process exits.
5. Relaunch and confirm execution history remains available.

The Desktop preview workflow builds unsigned artifacts for validation. Public download links require signed, verified artifacts. macOS distribution requires Developer ID signing and Apple notarization. Windows production distribution requires an Authenticode signing identity and timestamping. Supply release credentials through the CI secret store when a release is authorized.
