# Tauri Icon Placeholder

This is a placeholder for the Sentinel app icon.

## Required Icons

Place the following icons in this directory:

- `32x32.png` - 32x32px PNG
- `128x128.png` - 128x128px PNG
- `128x128@2x.png` - 256x256px PNG (Retina)
- `icon.icns` - macOS app icon bundle
- `icon.ico` - Windows app icon
- `tray-icon.png` - System tray icon (22x22 for macOS, 16x16 for Windows)

## Generate Icons

To generate all required icons from a 512x512 PNG source:

```bash
npm run tauri icon path/to/source-icon.png
```

This will automatically create all necessary icon formats.

## Icon Requirements

- **Source**: 512x512px PNG with transparent background
- **Format**: PNG for all except .icns (macOS) and .ico (Windows)
- **Colors**: Support for dark/light themes
- **Tray Icon**: Simple, recognizable at small sizes (16x16)

## Temporary Icons

For development, Tauri will use default icons if custom ones are not provided.
The app will still build and run, but will use generic icons.
