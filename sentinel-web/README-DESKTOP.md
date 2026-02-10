# Tauri Desktop App

This directory contains the Tauri desktop wrapper for Sentinel.

## Prerequisites

### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install dependencies
npm install
```

### Windows
```bash
# Install Rust from https://rustup.rs/
# Install Visual Studio C++ Build Tools from https://visualstudio.microsoft.com/downloads/

# Install dependencies
npm install
```

## Development

```bash
# Run in development mode (launches backend + frontend in Tauri window)
npm run tauri:dev
```

This will:
1. Start the Python backend on `localhost:8000`
2. Start Next.js dev server on `localhost:3000`
3. Open Tauri window with the UI

## Building

### macOS (Universal Binary)
```bash
npm run tauri:build:mac
```

Output: `src-tauri/target/release/bundle/dmg/Sentinel_0.1.0_universal.dmg`

### Windows
```bash
npm run tauri:build:win
```

Output: `src-tauri/target/release/bundle/msi/Sentinel_0.1.0_x64_en-US.msi`

### All Platforms
```bash
npm run tauri:build
```

## Icons

Icons are located in `src-tauri/icons/`. To regenerate from a 512x512 PNG source:

```bash
npm run tauri icon path/to/icon.png
```

## System Requirements

- **Python**: 3.11+ (required for backend)
- **Rust**: Latest stable
- **Node.js**: 18+

## Features

- ✅ Auto-launches Python backend on startup
- ✅ Health check ensures backend is ready
- ✅ System tray for quick access
- ✅ Hide on close (doesn't quit)
- ✅ Clean process cleanup on exit
- ✅ Native installers (DMG for macOS, MSI for Windows)

## Troubleshooting

### Backend doesn't start
- Make sure Python 3.11+ is installed: `python3 --version`
- Check backend dependencies: `cd ../sentinel-core && pip install -r requirements.txt`

### Build fails
- Update Rust: `rustup update`
- Clear build cache: `cargo clean`

### Window doesn't show
- Check console for errors
- Ensure Next.js build completed: `npm run build`

## Architecture

```
User opens Sentinel.app
    ↓
Tauri launches
    ↓
Launch Python backend (FastAPI)
    ↓
Health check (30 retries, 500ms interval)
    ↓
Load Next.js UI in WebView
    ↓
User quits from tray
    ↓
Kill backend process
    ↓
Clean exit
```
