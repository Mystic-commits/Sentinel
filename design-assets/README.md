# Sentinel Design Assets

This directory contains visual design assets for the Sentinel brand.

## 📁 Directory Structure

```
design-assets/
├── logos/
│   ├── logo-full.svg          # Full logo with wordmark
│   ├── logo-icon.svg          # Icon only
│   ├── logo-monochrome.svg    # Single color version
│   └── logo-inverse.svg       # Light version for dark BG
│
├── icons/
│   ├── app-icon/
│   │   ├── icon-1024.png      # macOS app icon
│   │   ├── icon-512.png       
│   │   ├── icon-256.png
│   │   └── icon.icns          # macOS bundle
│   │
│   └── web/
│       ├── favicon-32x32.png
│       ├── favicon-16x16.png
│       └── apple-touch-icon.png
│
├── ui-components/
│   ├── buttons.svg            # Button component variations
│   ├── cards.svg              # Card component styles
│   └── inputs.svg             # Input field styles
│
└── mockups/
    ├── dashboard-desktop.png  # Desktop UI mockup
    ├── dashboard-mobile.png   # Mobile UI mockup
    └── cli-demo.png           # CLI screenshot
```

## 🎨 Logo Design Brief

### Primary Logo Concept: "Shield Circuit"

**Description:**
- Hexagonal shield shape with rounded corners
- Subtle circuit board pattern integrated into shield edges
- "S" lettermark centered, using Inter font weight 700
- Wordmark "SENTINEL" to the right in Inter Medium

**Specifications:**
```
Icon Size: 64x64px base unit
Shield: 48x48px within 64x64 canvas (8px padding)
Stroke Width: 2px for circuit lines
Corner Radius: 4px on hexagon corners
Letter S: 32px height, centered

Colors:
- Shield outline: CYAN-500 (#06B6D4)
- Circuit lines: CYAN-400 (#22D3EE) at 40% opacity
- S lettermark: TEXT-100 (#F9FAFB)
- Wordmark: TEXT-100 (#F9FAFB)
```

**SVG Template:**
```svg
<svg width="200" height="64" viewBox="0 0 200 64" xmlns="http://www.w3.org/2000/svg">
  <!-- Shield hexagon -->
  <path d="M32 8 L48 16 L48 48 L32 56 L16 48 L16 16 Z" 
        fill="none" 
        stroke="#06B6D4" 
        stroke-width="2" 
        rx="4"/>
  
  <!-- Circuit lines (decorative) -->
  <path d="M20 20 L20 24 L16 24" 
        stroke="#22D3EE" 
        stroke-width="1" 
        opacity="0.4"/>
  
  <!-- Letter S -->
  <text x="32" y="38" 
        font-family="Inter" 
        font-weight="700" 
        font-size="24" 
        fill="#F9FAFB" 
        text-anchor="middle">S</text>
  
  <!-- Wordmark -->
  <text x="80" y="38" 
        font-family="Inter" 
        font-weight="500" 
        font-size="20" 
        fill="#F9FAFB">SENTINEL</text>
</svg>
```

### Icon-Only Variant

For app icons, system trays, and favicons:
- Remove wordmark
- Center shield on canvas
- Increase padding to 12px
- Scale S lettermark to fill shield better

**Specifications:**
```
Canvas: 1024x1024px (for macOS)
Shield: 900x900px (112px padding)
Background: BG-900 (#0A0E14)
```

## 🎨 Color Implementation

### CSS Variables

Add to your global CSS:

```css
:root {
  /* Backgrounds */
  --bg-900: #0A0E14;
  --bg-800: #111827;
  --bg-700: #1F2937;
  --bg-600: #374151;
  
  /* Cyan Accents */
  --cyan-400: #22D3EE;
  --cyan-500: #06B6D4;
  --cyan-600: #0891B2;
  --cyan-700: #0E7490;
  
  /* Text */
  --text-100: #F9FAFB;
  --text-200: #E5E7EB;
  --text-300: #9CA3AF;
  --text-400: #6B7280;
  
  /* Semantic */
  --success: #10B981;
  --warning: #F59E0B;
  --error: #EF4444;
  --info: #3B82F6;
}
```

### Tailwind Configuration

If using Tailwind CSS:

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        bg: {
          900: '#0A0E14',
          800: '#111827',
          700: '#1F2937',
          600: '#374151',
        },
        cyan: {
          400: '#22D3EE',
          500: '#06B6D4',
          600: '#0891B2',
          700: '#0E7490',
        },
        text: {
          100: '#F9FAFB',
          200: '#E5E7EB',
          300: '#9CA3AF',
          400: '#6B7280',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
}
```

## 📐 Component Templates

### Button Component (React + Tailwind)

```tsx
// Primary Button
<button className="
  bg-cyan-500 
  text-bg-900 
  px-6 py-3 
  rounded-lg 
  font-medium 
  hover:bg-cyan-400 
  transition-colors 
  duration-200
">
  Execute Plan
</button>

// Secondary Button
<button className="
  bg-transparent 
  border border-bg-600 
  text-text-100 
  px-6 py-3 
  rounded-lg 
  font-medium 
  hover:bg-bg-700 
  transition-colors 
  duration-200
">
  Cancel
</button>

// Danger Button
<button className="
  bg-error 
  text-text-100 
  px-6 py-3 
  rounded-lg 
  font-medium 
  hover:bg-red-600 
  transition-colors 
  duration-200
">
  Delete
</button>
```

### Card Component

```tsx
<div className="
  bg-bg-700 
  border border-bg-600 
  rounded-xl 
  p-6 
  shadow-lg 
  hover:border-cyan-500 
  hover:-translate-y-0.5 
  transition-all 
  duration-200
">
  <h3 className="text-xl font-semibold text-text-100 mb-2">
    Task Title
  </h3>
  <p className="text-text-200 mb-4">
    Description goes here
  </p>
  <button className="text-cyan-500 font-medium">
    View Details →
  </button>
</div>
```

## 🎭 Animation Examples

### Loading Spinner (CSS)

```css
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spinner {
  border: 3px solid var(--bg-600);
  border-top-color: var(--cyan-500);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 0.8s linear infinite;
}
```

### Pulse Effect (Active State)

```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-active {
  animation: pulse 2s ease-in-out infinite;
}
```

### Slide In (Modal)

```css
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal {
  animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

## 🖼️ Mockup Guidelines

When creating UI mockups:

1. **Use actual brand colors** - No placeholders
2. **Real content** - Use actual file names, sizes, dates
3. **Consistent spacing** - 8px grid system
4. **High contrast** - Ensure text is readable
5. **Show states** - Hover, active, disabled
6. **Include icons** - Use Lucide icon set

### Recommended Tools

- **Figma** - UI design (preferred)
- **Adobe XD** - Alternative
- **Sketch** - macOS only
- **Penpot** - Open source alternative

## 📸 Screenshot Guidelines

For documentation and marketing:

**Background:** Always use BG-900 (#0A0E14)  
**Window:** Show native title bar or hide (fullscreen)  
**Content:** Real tasks, not "Lorem ipsum"  
**Resolution:** 2x retina (2880x1800 for desktop)  
**Format:** PNG with transparency or solid background  

### CLI Screenshots

Use actual terminal with:
- Font: JetBrains Mono 14px
- Theme: Dark background
- Colors: Cyan for highlights, white for text
- Tool: [Carbon](https://carbon.now.sh) or iTerm2 screenshots

## 🚀 Export Specifications

### App Icons

**macOS:**
- 1024x1024px PNG (for App Store)
- Generate .icns with `iconutil`

**Windows:**
- 256x256px PNG
- Generate .ico with ImageMagick

**Linux:**
- 512x512px PNG
- SVG for scalability

### Web Icons

- favicon.ico (16x16, 32x32)
- favicon.png (32x32)
- apple-touch-icon.png (180x180)
- og-image.png (1200x630) for social sharing

## ✅ Design Checklist

Before finalizing any design asset:

- [ ] Uses official color palette
- [ ] Typography matches brand guide (Inter/JetBrains Mono)
- [ ] Spacing follows 8px grid
- [ ] Icons are from Lucide or match style
- [ ] Contrast ratio ≥ 4.5:1 (WCAG AA)
- [ ] Works on dark backgrounds
- [ ] Scalable (vector when possible)
- [ ] Compressed for web use

---

**Need custom assets?** Contact the design team or use the templates above to create consistent visuals.
