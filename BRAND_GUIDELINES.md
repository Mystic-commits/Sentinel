# Sentinel Brand Guidelines

**Version 1.0 | Last Updated: February 2024**

---

## 🎯 Brand Essence

**Sentinel** is a premium AI-powered file organization system that feels like a **control center for your digital life**. The brand should convey:

- **Intelligence** - AI-powered, smart decisions
- **Trust** - Safe, secure, reliable
- **Control** - User is in command
- **Premium** - Professional-grade tool
- **Modern** - Cutting-edge technology

**Brand Personality:** Intelligent • Trustworthy • Powerful • Sleek • Professional

---

## 🛡️ Logo Concepts

### Primary Logo Concept

```
┌─────────────────────────────────────┐
│                                     │
│    🛡️                               │
│    ╔═══════╗                        │
│    ║   S   ║  SENTINEL              │
│    ╚═══════╝                        │
│                                     │
└─────────────────────────────────────┘
```

**Concept 1: Shield with Circuit Pattern**
- Central shield icon with subtle circuit/tech lines
- Conveys protection + technology
- Modern geometric shield shape
- Monochromatic with cyan accent on edges

**Concept 2: Hexagonal Badge**
- Hexagon (tech/security association)
- "S" lettermark inside
- Minimalist, professional
- Works well at small sizes

**Concept 3: Radar/Scan Lines**
- Circular design with scanning lines
- Suggests active monitoring
- Animated potential (scan effect)
- Futuristic aesthetic

### Logo Variations

**Primary:** Full logo with wordmark  
**Secondary:** Icon only (for app icon, favicons)  
**Monochrome:** Single color version for print  
**Inverse:** Light version for dark backgrounds  

### Logo Usage Rules

✅ **Do:**
- Maintain minimum clear space (equal to height of "S")
- Use approved color combinations only
- Scale proportionally
- Use on contrasting backgrounds

❌ **Don't:**
- Rotate or distort the logo
- Change colors outside approved palette
- Add effects (shadows, glows, gradients)
- Use on busy backgrounds without container

---

## 🎨 Color Palette

### Primary Colors

```
┌─────────────────────────────────────────────────────┐
│ Background Hierarchy                                │
├─────────────────────────────────────────────────────┤
│ BG-900  #0A0E14  ████████  Deepest dark            │
│ BG-800  #111827  ████████  Primary background      │
│ BG-700  #1F2937  ████████  Elevated surfaces       │
│ BG-600  #374151  ████████  Card backgrounds        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Accent - Cyan (Primary)                             │
├─────────────────────────────────────────────────────┤
│ CYAN-400  #22D3EE  ████████  Bright accent          │
│ CYAN-500  #06B6D4  ████████  Primary accent         │
│ CYAN-600  #0891B2  ████████  Hover states           │
│ CYAN-700  #0E7490  ████████  Active/pressed         │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Text Hierarchy                                      │
├─────────────────────────────────────────────────────┤
│ TEXT-100  #F9FAFB  ████████  Primary text           │
│ TEXT-200  #E5E7EB  ████████  Secondary text         │
│ TEXT-300  #9CA3AF  ████████  Tertiary/muted         │
│ TEXT-400  #6B7280  ████████  Disabled text          │
└─────────────────────────────────────────────────────┘
```

### Semantic Colors

```
┌─────────────────────────────────────────────────────┐
│ Status Colors                                       │
├─────────────────────────────────────────────────────┤
│ SUCCESS   #10B981  ████████  Green - completed      │
│ WARNING   #F59E0B  ████████  Amber - caution        │
│ ERROR     #EF4444  ████████  Red - danger/delete    │
│ INFO      #3B82F6  ████████  Blue - information     │
└─────────────────────────────────────────────────────┘
```

### Usage Guidelines

**Backgrounds:**
- Use BG-900 for app backgrounds
- Use BG-800 for main content areas
- Use BG-700 for cards and elevated elements
- Never use pure black (#000000)

**Accents:**
- CYAN-500 for primary CTAs
- CYAN-400 for highlights and active states
- Use sparingly (10% of interface max)
- Always pair with dark backgrounds for contrast

**Text:**
- TEXT-100 for headings and primary content
- TEXT-200 for body text
- TEXT-300 for labels and secondary info
- Minimum contrast ratio: 4.5:1

### Color Psychology

- **Dark backgrounds** → Professional, focused, premium
- **Cyan accent** → Technology, trust, intelligence
- **High contrast** → Clarity, precision, control

---

## 🔤 Typography

### Font Stack

**Primary: Inter**
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```
- **Why Inter:** Modern, highly legible, professional
- Excellent at small sizes
- Variable font support
- Tech industry standard

**Monospace: JetBrains Mono**
```css
font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
```
- For code snippets, file paths, technical data
- Excellent ligature support
- Clean, readable

### Type Scale

```
Display Large   48px / 3rem    font-weight: 700  Line height: 1.1
Display         36px / 2.25rem font-weight: 700  Line height: 1.2
Heading 1       30px / 1.875rem font-weight: 600  Line height: 1.2
Heading 2       24px / 1.5rem  font-weight: 600  Line height: 1.3
Heading 3       20px / 1.25rem font-weight: 600  Line height: 1.4
Body Large      18px / 1.125rem font-weight: 400  Line height: 1.6
Body            16px / 1rem    font-weight: 400  Line height: 1.6
Body Small      14px / 0.875rem font-weight: 400  Line height: 1.5
Caption         12px / 0.75rem font-weight: 500  Line height: 1.4
```

### Typography Rules

**Headings:**
- Use font-weight 600-700
- Tighter line-height (1.1-1.3)
- Letter-spacing: -0.02em for large text
- Color: TEXT-100

**Body Text:**
- Font-weight 400 (regular)
- Line-height: 1.6 for readability
- Color: TEXT-200
- Max width: 65 characters for paragraphs

**UI Text:**
- Buttons: font-weight 500, uppercase or sentence case
- Labels: font-weight 500, 12-14px
- File paths: Monospace font, TEXT-300

---

## 🎯 Icon System

### Icon Style

**Style:** Outlined (stroke-based), minimal  
**Weight:** 1.5-2px strokes  
**Corners:** Rounded (border-radius: 2px)  
**Grid:** 24x24px base, scale proportionally  

**Recommended Library:** Lucide Icons
- Consistent style
- High quality
- Open source
- React components available

### Icon Categories

**Actions:** Play, Pause, Stop, Execute, Undo, Delete  
**Files:** Document, Folder, Archive, Image, Video  
**Status:** Check, Alert, Info, Loading (spinner)  
**UI:** Menu, Close, Search, Settings, Filter  

### Icon Usage

```
Small   16px  - Inline with text
Medium  24px  - UI buttons, navigation
Large   32px  - Feature highlights
XLarge  48px  - Empty states, hero sections
```

**Color:**
- Default: TEXT-300 (#9CA3AF)
- Active: CYAN-500 (#06B6D4)
- Hover: TEXT-200 (#E5E7EB)
- Destructive: ERROR (#EF4444)

---

## 🖼️ UI Components

### Buttons

**Primary Button (CTA):**
```css
background: #06B6D4 (CYAN-500)
color: #0A0E14 (BG-900)
padding: 12px 24px
border-radius: 8px
font-weight: 500
hover: #22D3EE (CYAN-400)
```

**Secondary Button:**
```css
background: transparent
border: 1px solid #374151 (BG-600)
color: #F9FAFB (TEXT-100)
padding: 12px 24px
border-radius: 8px
hover: background #1F2937 (BG-700)
```

**Danger Button:**
```css
background: #EF4444 (ERROR)
color: #F9FAFB (TEXT-100)
hover: #DC2626 (darker red)
```

### Cards

```css
background: #1F2937 (BG-700)
border: 1px solid #374151 (BG-600)
border-radius: 12px
padding: 24px
box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3)
```

**Hover State:**
```css
border-color: #06B6D4 (CYAN-500)
transform: translateY(-2px)
transition: all 0.2s ease
```

### Inputs

```css
background: #111827 (BG-800)
border: 1px solid #374151 (BG-600)
border-radius: 8px
padding: 10px 16px
color: #F9FAFB (TEXT-100)

focus:
  border-color: #06B6D4 (CYAN-500)
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1)
```

---

## ✨ Visual Effects

### Shadows

**Subtle (cards):**
```css
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
```

**Medium (modals):**
```css
box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
```

**Strong (dropdowns):**
```css
box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6);
```

### Glow Effects (Accent Only)

```css
box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
```

Use sparingly for:
- Active states
- Focus indicators
- Important CTAs

### Border Radius

```
Small    4px  - Badges, tags
Medium   8px  - Buttons, inputs
Large    12px - Cards, containers
XLarge   16px - Modals, large panels
```

### Transitions

**Default:**
```css
transition: all 0.2s ease-in-out;
```

**Smooth:**
```css
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
```

---

## 🎭 UI Tone & Voice

### Visual Tone

**Characteristics:**
- **Minimal** - Remove unnecessary elements
- **Precise** - Exact alignment, consistent spacing
- **High-contrast** - Clear visual hierarchy
- **Purposeful** - Every element serves a function
- **Technical** - Embrace monospace, data visualization

### Spacing System

Use 8px base unit:
```
xs:  4px  (0.25rem)
sm:  8px  (0.5rem)
md:  16px (1rem)
lg:  24px (1.5rem)
xl:  32px (2rem)
2xl: 48px (3rem)
```

### Animation Principles

**Speed:**
- Micro-interactions: 150-200ms
- Standard: 250-300ms
- Complex: 400-500ms

**Easing:**
- Entrance: ease-out
- Exit: ease-in
- Movement: ease-in-out

**Examples:**
```css
/* Button hover */
transition: background-color 0.2s ease-out;

/* Modal open */
animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);

/* Loading spinner */
animation: spin 1s linear infinite;
```

---

## 📐 Layout Guidelines

### Grid System

**Desktop:** 12-column grid, 24px gutters  
**Tablet:** 8-column grid, 16px gutters  
**Mobile:** 4-column grid, 16px gutters  

**Max Content Width:** 1440px

### Breakpoints

```css
/* Mobile first */
sm: 640px   /* Small devices */
md: 768px   /* Tablets */
lg: 1024px  /* Laptops */
xl: 1280px  /* Desktops */
2xl: 1536px /* Large screens */
```

### Sidebar Navigation

```
Width: 280px (desktop)
Background: BG-800
Border-right: 1px solid BG-600
```

### Main Content

```
Padding: 32px (desktop)
Padding: 24px (tablet)
Padding: 16px (mobile)
```

---

## 🎨 UI Patterns

### Dashboard Layout

```
┌──────────────────────────────────────────────────┐
│  Sidebar    │  Main Content                      │
│             │                                     │
│  • Home     │  ┌──────────────────────────────┐ │
│  • Tasks    │  │  Page Header                 │ │
│  • History  │  │  Breadcrumb / Title          │ │
│  • Settings │  └──────────────────────────────┘ │
│             │                                     │
│             │  ┌──────────┐  ┌──────────┐       │
│             │  │  Card 1  │  │  Card 2  │       │
│             │  └──────────┘  └──────────┘       │
│             │                                     │
└──────────────────────────────────────────────────┘
```

### Task Flow UI

```
Step 1: Scan  →  Step 2: Review  →  Step 3: Execute
[Active]         [Pending]           [Pending]

Each step card shows:
- Icon (large, cyan when active)
- Title (bold)
- Description (muted text)
- Action button
```

### Data Visualization

**File Size Bars:**
```css
background: BG-700
fill: CYAN-500
height: 8px
border-radius: 4px
```

**Progress Indicators:**
```css
Circular: Stroke CYAN-500, 4px width
Linear: Animated gradient CYAN-400 to CYAN-600
```

---

## 🎯 Application-Specific Guidance

### File Type Icons

Use color coding:
- **Documents:** Blue (#3B82F6)
- **Images:** Purple (#8B5CF6)
- **Videos:** Pink (#EC4899)
- **Archives:** Orange (#F59E0B)
- **Executables:** Red (#EF4444)

### Status Indicators

```
Scanning:    Animated spinner, CYAN-500
Planning:    Pulsing dot, CYAN-400
Reviewing:   Static dot, WARNING
Executing:   Progress bar, CYAN-500
Completed:   Check icon, SUCCESS
Failed:      X icon, ERROR
```

### Empty States

**Design:**
- Large icon (48-64px), TEXT-400
- Heading: TEXT-200
- Description: TEXT-300
- CTA button: Primary style

**Example:**
```
     [📂]
  No tasks yet
  Create your first cleanup task
  [ + New Task ]
```

---

## 📱 Platform Adaptations

### Desktop App (Tauri)

- Use native window controls
- System tray icon: Simplified monochrome logo
- Notification badges: CYAN-500 dot

### Web App

- Responsive layout
- Progressive Web App (PWA) support
- Favicon: 32x32px icon variant

### CLI

- Use cyan color for highlights
- Bold for headings
- Dim for secondary info
- Spinner: Cyan dots animation

---

## ✅ Brand Checklist

Before releasing any visual asset, ensure:

- [ ] Uses approved color palette
- [ ] Typography follows scale
- [ ] Icons are from Lucide (or match style)
- [ ] Spacing uses 8px grid
- [ ] Contrast ratio meets WCAG AA (4.5:1)
- [ ] Dark theme optimized
- [ ] Animations are subtle and fast
- [ ] Feels premium and professional

---

## 📦 Design Resources

**Fonts:**
- Inter: [Google Fonts](https://fonts.google.com/specimen/Inter)
- JetBrains Mono: [JetBrains](https://www.jetbrains.com/lp/mono/)

**Icons:**
- Lucide Icons: [lucide.dev](https://lucide.dev)

**Color Tools:**
- Contrast Checker: [WebAIM](https://webaim.org/resources/contrastchecker/)
- Tailwind Colors: [tailwindcss.com/docs/colors](https://tailwindcss.com/docs/customizing-colors)

**Inspiration:**
- Linear (linear.app) - Clean, minimal UI
- Vercel (vercel.com) - Dark theme excellence
- Raycast (raycast.com) - Command center aesthetic

---

**Last Updated:** February 2024  
**Version:** 1.0  
**Maintained by:** Sentinel Design Team
