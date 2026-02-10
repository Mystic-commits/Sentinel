# Sentinel Design System

> **MinMaxAgent-inspired futuristic control center aesthetic**  
> Minimal • Premium • Dark • Subtle Cyan Accents

---

## Philosophy

Sentinel's design system embodies a **mission control aesthetic** — think premium developer tools meets futuristic command center. The design is intentionally _minimal_, using deep blacks, generous whitespace, and strategic cyan highlights to create a calm, professional environment.

### Core Principles

1. **Minimal & Premium** — Large whitespace, calm typography, no unnecessary elements
2. **Dark Control Center** — Deep dark backgrounds create focus and reduce eye strain
3. **Subtle Accents** — Cyan used strategically for primary actions, never overwhelming
4. **Clean Hierarchy** — Clear visual organization through consistent spacing and typography

### What This Is NOT

❌ Neon cyberpunk with bright colors everywhere  
❌ Glowing effects and animations overload  
❌ Busy gradients and complex patterns  
❌ Chat bubble UI with rounded avatars

### What This IS

✅ Deep blacks with subtle gray variations  
✅ Strategic cyan for primary actions only  
✅ Clean borders and subtle shadows  
✅ Generous whitespace and breathing room  
✅ Task-first design with clear states

---

## Color Palette

### Background Layers

Build depth through layering, not gradients.

| Token | Hex | Usage |
|-------|-----|-------|
| `background` | `#020617` | Base page background (slate-950) |
| `background-elevated` | `#0f172a` | Cards, panels, modals (slate-900) |
| `background-panel` | `#1e293b` | Elevated elements, popovers (slate-800) |
| `background-hover` | `#334155` | Hover states (slate-700) |

**Example:**
```tsx
<div className="bg-background">
  <div className="bg-background-elevated border border-slate-800">
    <div className="bg-background-panel">
      Elevated content
    </div>
  </div>
</div>
```

### Primary Accent (Cyan)

Use sparingly for maximum impact.

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | `#06b6d4` | Primary actions, links (cyan-500) |
| `primary-hover` | `#22d3ee` | Hover states (cyan-400) |
| `primary-active` | `#0891b2` | Active/pressed states (cyan-600) |
| `primary-subtle` | `#083344` | Subtle backgrounds (cyan-950) |

**Rules:**
- Use for **primary actions only** (main CTA, active states)
- **Maximum 1-2** primary actions per screen
- Never use cyan for decorative purposes
- Prefer `text-primary` over `bg-primary` when possible

### Semantic Colors

Standard Tailwind colors for semantic meaning.

| Purpose | Class | Example |
|---------|-------|---------|
| Success | `text-green-500` | "✓ Task completed" |
| Error | `text-red-500` | "❌ Operation failed" |
| Warning | `text-amber-500` | "⚠ Review required" |
| Info | `text-blue-500` | "ℹ 142 files scanned" |

### Text Hierarchy

| Level | Class | Hex | Usage |
|-------|-------|-----|-------|
| Headings | `text-slate-50` | `#f8fafc` | H1, H2, H3 |
| Body | `text-slate-200` | `#e2e8f0` | Paragraphs, content |
| Secondary | `text-slate-400` | `#94a3b8` | Captions, metadata |
| Disabled | `text-slate-600` | `#475569` | Disabled text |

---

## Typography

### Font Stack

**Sans-Serif (UI/Display): Inter**
- Clean, modern, excellent readability
- Variable font for performance
- Weights: 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold)
- Usage: `font-sans` (default)

**Monospace (Code/Data): JetBrains Mono**
- Designed for developers
- Clear distinction between characters (0/O, 1/l/I)
- Usage: `font-mono`

### Type Scale

| Class | Size | Usage | Example |
|-------|------|-------|---------|
| `text-xs` | 12px | Badges, tiny labels | "NEW" badge |
| `text-sm` | 14px | Body text, buttons | Most UI text |
| `text-base` | 16px | Primary body | Long-form content |
| `text-lg` | 18px | Card titles | "Organization Plan" |
| `text-xl` | 20px | Section headers | "Scan Results" |
| `text-2xl` | 24px | Page headers | "Dashboard" |
| `text-3xl` | 30px | Hero text | Landing page |
| `text-4xl` | 36px | Extra large | Hero sections |

### Font Weights

| Class | Weight | Usage |
|-------|--------|-------|
| `font-normal` | 400 | Body text |
| `font-medium` | 500 | Buttons, labels |
| `font-semibold` | 600 | Subtitles, emphasis |
| `font-bold` | 700 | Headings |

---

## Spacing

Use Tailwind's default scale strategically:

| Class | Size | Usage |
|-------|------|-------|
| `gap-2` | 8px | Tight spacing (icon + text) |
| `gap-3` | 12px | Default gap between elements |
| `gap-4` | 16px | Standard spacing |
| `gap-6` | 24px | Section spacing |
| `gap-8` | 32px | Large spacing between sections |
| `p-4` | 16px | Compact padding |
| `p-6` | 24px | Standard card padding |
| `p-8` | 32px | Large padding |
| `py-12` | 48px | Section vertical padding |

**Golden Rules:**
- Cards: `p-6` (standard), `p-4` (compact), `p-8` (large)
- Grid gaps: `gap-6` for cards, `gap-4` for lists
- Vertical rhythm: `space-y-8` between sections

---

## Components

### Buttons

```tsx
import { Button } from '@/components/ui';

// Primary (cyan) - use for main actions
<Button variant="primary">Start Scan</Button>

// Secondary (gray) - use for secondary actions
<Button variant="secondary">Cancel</Button>

// Ghost - use for tertiary actions
<Button variant="ghost">Learn More</Button>

// Danger - use for destructive actions
<Button variant="danger">Delete All</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="md">Medium</Button> // default
<Button size="lg">Large</Button>

// With loading state
<Button loading>Processing...</Button>

// With icon
<Button icon={<ScanIcon />}>Scan Directory</Button>
```

**Classes:**
```tsx
// Primary
bg-primary hover:bg-primary-hover active:bg-primary-active
text-white px-4 py-2 rounded-lg

// Secondary
bg-slate-700 hover:bg-slate-600
text-slate-200 border border-slate-600
px-4 py-2 rounded-lg

// Ghost
text-slate-300 hover:text-primary hover:bg-slate-800/50
px-3 py-2 rounded-md
```

### Cards

```tsx
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui';

// Standard card
<Card variant="standard">
  <CardHeader title="Scan Results" subtitle="142 files analyzed" />
  <CardContent>
    Your content here
  </CardContent>
  <CardFooter>
    <Button>View Details</Button>
  </CardFooter>
</Card>

// Interactive card (clickable)
<Card variant="interactive" onClick={handleClick}>
  Content
</Card>

// Elevated panel
<Card variant="elevated">
  Content
</Card>
```

**Classes:**
```tsx
// Standard
bg-background-elevated border border-slate-800
rounded-xl p-6 shadow-card

// Interactive
hover:border-primary/30 hover:shadow-glow-sm
transition-all duration-200 cursor-pointer

// Elevated
bg-background-panel border border-slate-700
shadow-card-lg
```

### Inputs

```tsx
<input
  type="text"
  placeholder="Enter path..."
  className="
    bg-slate-800 border border-slate-700
    focus:border-primary focus:ring-2 focus:ring-primary/20
    text-slate-200 placeholder:text-slate-500
    px-4 py-2.5 rounded-lg
    w-full
  "
/>
```

---

## Layout Patterns

### Page Container

```tsx
<div className="max-w-7xl mx-auto px-6 lg:px-8 py-8">
  {/* Your content */}
</div>
```

### Grid

```tsx
// Responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <Card>...</Card>
  <Card>...</Card>
  <Card>...</Card>
</div>
```

### Sidebar Layout

```tsx
<div className="flex h-screen">
  {/* Sidebar */}
  <aside className="w-64 bg-background-elevated border-r border-slate-800">
    Navigation
  </aside>
  
  {/* Main content */}
  <main className="flex-1 overflow-y-auto">
    Content
  </main>
</div>
```

---

## Effects & Animation

### Shadows

| Class | Usage |
|-------|-------|
| `shadow-card` | Standard cards |
| `shadow-card-lg` | Elevated panels, modals |
| `shadow-glow-sm` | Subtle cyan glow on hover |
| `shadow-glow-md` | Medium cyan glow for focus |

### Animations

```tsx
// Fade in
<div className="animate-fade-in">Content</div>

// Slide up (form elements)
<div className="animate-slide-up">Content</div>

// Slide down (dropdowns)
<div className="animate-slide-down">Content</div>

// Transitions
<button className="transition-colors duration-150">
  Hover me
</button>
```

---

## Do's and Don'ts

### ✅ DO

- Use `bg-background` for page backgrounds
- Use `bg-background-elevated` for cards
- Reserve `primary` (cyan) for primary actions only
- Use `text-slate-200` for body text
- Maintain generous whitespace (`p-6`, `gap-6`)
- Use `rounded-lg` or `rounded-xl` for corners
- Add subtle shadows (`shadow-card`)

### ❌ DON'T

- Don't use cyan everywhere (it's an accent, not a theme)
- Don't use bright neon colors
- Don't create busy gradients
- Don't use small spacing (prefer `p-6` over `p-2`)
- Don't mix border radius (stick to `rounded-lg/xl`)
- Don't create deeply nested cards
- Don't use multiple primary CTAs per screen

---

## Accessibility

### Contrast Ratios (WCAG AA)

All text colors meet minimum contrast requirements:

- `slate-50` on `#020617`: **18.9:1** ✓
- `slate-200` on `#0f172a`: **10.1:1** ✓
- `cyan-500` on `#020617`: **7.2:1** ✓

### Focus States

All interactive elements include focus rings:

```tsx
focus:outline-none focus:ring-2 focus:ring-primary/50
```

### Keyboard Navigation

- Buttons: native `<button>` elements
- Links: semantic `<a>` elements
- Forms: proper labels and aria attributes

---

## Quick Reference

```tsx
// Page setup
<html className="dark">
<body className="bg-background text-slate-200">

// Card
<div className="bg-background-elevated border border-slate-800 rounded-xl p-6">

// Button
<button className="bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded-lg">

// Input
<input className="bg-slate-800 border border-slate-700 focus:border-primary px-4 py-2.5 rounded-lg">

// Heading
<h1 className="text-2xl font-bold text-slate-50">

// Body text
<p className="text-slate-200">

// Secondary text
<span className="text-slate-400">
```

---

## Resources

- **Tailwind Config**: [`tailwind.config.ts`](file:///Users/Mystic/Desktop/trial%20and%20error/Sentinel/sentinel-web/tailwind.config.ts)
- **Fonts**: [`src/app/fonts.ts`](file:///Users/Mystic/Desktop/trial%20and%20error/Sentinel/sentinel-web/src/app/fonts.ts)
- **Components**: [`src/components/ui/`](file:///Users/Mystic/Desktop/trial%20and%20error/Sentinel/sentinel-web/src/components/ui)
- **Button**: [`Button.tsx`](file:///Users/Mystic/Desktop/trial%20and%20error/Sentinel/sentinel-web/src/components/ui/Button.tsx)
- **Card**: [`Card.tsx`](file:///Users/Mystic/Desktop/trial%20and%20error/Sentinel/sentinel-web/src/components/ui/Card.tsx)

---

**Version**: 1.0  
**Last Updated**: February 2026
