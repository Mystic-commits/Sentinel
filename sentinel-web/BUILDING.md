# Building Sentinel Desktop App

Complete guide for building Sentinel as a desktop application using Tauri.

## Prerequisites

### All Platforms

1. **Node.js 18+**
   ```bash
   node --version  # Should be >= 18
   ```

2. **Rust (Latest Stable)**
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source $HOME/.cargo/env
   rustc --version
   ```

3. **Python 3.11+**
   ```bash
   python3 --version  # Should be >= 3.11
   ```

### macOS

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Verify installation
xcode-select -p
```

### Windows

1. **Microsoft C++ Build Tools**
   - Download from: https://visualstudio.microsoft.com/downloads/
   - Install "Desktop development with C++" workload

2. **WebView2** (usually pre-installed on Windows 10/11)
   - Download from: https://developer.microsoft.com/en-us/microsoft-edge/webview2/

### Linux

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install libwebkit2gtk-4.0-dev \
  build-essential \
  curl \
  wget \
  libssl-dev \
  libgtk-3-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev

# Fedora
sudo dnf install webkit2gtk3-devel.x86_64 \
  openssl-devel \
  curl \
  wget \
  libappindicator-gtk3 \
  librsvg2-devel

# Arch
sudo pacman -S webkit2gtk \
  base-devel \
  curl \
  wget \
  openssl \
  appmenu-gtk-module \
  gtk3 \
  libappindicator-gtk3 \
  librsvg
```

---

## Setup

### 1. Install Dependencies

```bash
cd sentinel-web
npm install
```

### 2. Install Backend Dependencies

```bash
cd ../sentinel-core
pip install -r requirements.txt
cd ../sentinel-web
```

### 3. Verify Tauri Installation

```bash
npm run tauri --version
```

---

## Development

### Run in Development Mode

```bash
npm run tauri:dev
```

This command will:
1. Start Next.js dev server (`localhost:3000`)
2. Launch Tauri window
3. Tauri app will start Python backend
4. Health check ensures backend is running
5. UI loads in Tauri window

**Console Output:**
```
🚀 Launching FastAPI backend...
📂 Backend path: ../../sentinel-core
✅ Backend process started with PID: 12345
🏥 Health check attempt 1/30
🏥 Health check attempt 2/30
✅ Backend is ready!
✅ Backend ready, UI should load now
```

### Hot Reload

- **Frontend changes**: Hot reload automatically
- **Rust changes**: Requires app restart
- **Backend changes**: Restart app or backend manually

---

## Building for Production

### 1. Build Frontend

```bash
npm run build
npm run export
```

This creates an optimized static export in the `out/` directory.

### 2. Build Desktop App

#### macOS (Universal Binary)

```bash
npm run tauri:build:mac
```

**Output:**
- DMG: `src-tauri/target/release/bundle/dmg/Sentinel_0.1.0_universal.dmg`
- App: `src-tauri/target/release/bundle/macos/Sentinel.app`

**Architectures:** Intel (x86_64) + Apple Silicon (aarch64)

#### Windows

```bash
npm run tauri:build:win
```

**Output:**
- MSI Installer: `src-tauri/target/release/bundle/msi/Sentinel_0.1.0_x64_en-US.msi`
- EXE: `src-tauri/target/release/sentinel-desktop.exe`

#### Linux

```bash
npm run tauri:build
```

**Output:**
- DEB: `src-tauri/target/release/bundle/deb/sentinel_0.1.0_amd64.deb`
- AppImage: `src-tauri/target/release/bundle/appimage/sentinel_0.1.0_amd64.AppImage`

### 3. Test Build

**macOS:**
```bash
open src-tauri/target/release/bundle/macos/Sentinel.app
```

**Windows:**
```bash
.\src-tauri\target\release\sentinel-desktop.exe
```

**Linux:**
```bash
./src-tauri/target/release/bundle/appimage/sentinel_0.1.0_amd64.AppImage
```

---

## Icons

### Generate Icons

1. Create a 512x512 PNG icon: `icon.png`

2. Generate all required sizes:
   ```bash
   npm run tauri icon icon.png
   ```

This creates:
- `icons/32x32.png`
- `icons/128x128.png`
- `icons/128x128@2x.png`
- `icons/icon.icns` (macOS)
- `icons/icon.ico` (Windows)

### Manual Icon Setup

If you have custom icons, place them in `src-tauri/icons/`:

- **macOS**: `icon.icns`
- **Windows**: `icon.ico`
- **Tray**: `tray-icon.png` (22x22 for macOS, 16x16 for Windows)

---

## Configuration

### Bundle Identifier

Edit `src-tauri/tauri.conf.json`:

```json
{
  "tauri": {
    "bundle": {
      "identifier": "com.sentinel.app"
    }
  }
}
```

### Window Settings

```json
{
  "tauri": {
    "windows": [{
      "title": "Sentinel",
      "width": 1400,
      "height": 900,
      "minWidth": 1024,
      "minHeight": 768
    }]
  }
}
```

### Security Allowlist

Control what Tauri APIs the frontend can access:

```json
{
  "tauri": {
    "allowlist": {
      "fs": {
        "scope": ["$HOME/Downloads/**", "$HOME/Desktop/**"]
      },
      "http": {
        "scope": ["http://localhost:8000/**"]
      }
    }
  }
}
```

---

## Code Signing

### macOS

```bash
# Sign with Apple Developer Certificate
codesign --deep --force --verify --verbose --sign "Developer ID Application: YOUR_NAME (TEAM_ID)" Sentinel.app

# Notarize (required for distribution)
xcrun notarytool submit Sentinel_0.1.0_universal.dmg \
  --apple-id your@email.com \
  --team-id TEAM_ID \
  --password APP_SPECIFIC_PASSWORD
```

### Windows

```bash
# Sign with certificate
signtool sign /f certificate.pfx /p password /tr http://timestamp.digicert.com /td sha256 /fd sha256 Sentinel_0.1.0_x64_en-US.msi
```

---

## Distribution

### macOS

1. **DMG Distribution:**
   - Upload `Sentinel_0.1.0_universal.dmg` to website
   - Users drag to Applications folder

2. **App Store:**
   - Use `mac-app-store` target in tauri.conf.json
   - Follow App Store submission guidelines

### Windows

1. **Direct Download:**
   - Host `.msi` file on website
   - Users run installer

2. **Microsoft Store:**
   - Use `ms-store` target
   - Submit via Partner Center

### Linux

1. **Package Repositories:**
   - Submit `.deb` to Ubuntu PPA
   - Submit to AUR (Arch)
   - Publish `.AppImage` directly

---

## Troubleshooting

### Build Fails

```bash
# Clear Rust build cache
cd src-tauri
cargo clean
cd ..

# Rebuild
npm run tauri:build
```

### Backend Doesn't Start

- Check Python version: `python3 --version`
- Install backend deps: `cd sentinel-core && pip install -r requirements.txt`
- Check logs in terminal

### Window is Blank

- Verify frontend build: `npm run build && npm run export`
- Check `out/` directory exists
- Check console for errors

### "Command not found: tauri"

```bash
npm install --save-dev @tauri-apps/cli
```

---

## Performance Tips

### Reduce Bundle Size

1. **Strip debug symbols:**
   ```toml
   # src-tauri/Cargo.toml
   [profile.release]
   strip = true
   opt-level = "z"
   lto = true
   ```

2. **Optimize frontend:**
   ```bash
   npm run build  # Already optimized by Next.js
   ```

### Faster Builds

1. **Use mold linker (Linux):**
   ```bash
   sudo apt install mold
   ```
   
   ```toml
   # .cargo/config.toml
   [target.x86_64-unknown-linux-gnu]
   linker = "clang"
   rustflags = ["-C", "link-arg=-fuse-ld=mold"]
   ```

2. **Incremental compilation:**
   ```toml
   # src-tauri/Cargo.toml
   [profile.dev]
   incremental = true
   ```

---

## Build Output Sizes

**macOS Universal DMG:** ~100-150 MB  
**Windows MSI:** ~80-120 MB  
**Linux AppImage:** ~90-130 MB

---

## Next Steps

1. Build app: `npm run tauri:build`
2. Test installer
3. Code sign (optional)
4. Distribute to users

For issues, check: https://tauri.app/v1/guides/debugging
