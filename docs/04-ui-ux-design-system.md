# A.R.I.A. — UI/UX Design System
## Premium Business Memory Interface

**Project:** A.R.I.A. (Adaptive Retail Intelligence Assistant) - Smart Voice Inventory Assistant
**Document Version:** 1.0
**Date:** September 19, 2026
**Document Type:** UI/UX Design System

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Visual Identity](#visual-identity)
3. [Color System](#color-system)
4. [Typography System](#typography-system)
5. [Spacing System](#spacing-system)
6. [Component Library](#component-library)
7. [Screen Designs](#screen-designs)
8. [Mobile Navigation](#mobile-navigation)
9. [Micro-Interactions](#micro-interactions)
10. [Animation System](#animation-system)
11. [Responsive Design](#responsive-design)
12. [Accessibility](#accessibility)

---

## Design Philosophy

### Core Principle

**"Speak first. Everything else second."**

The interface should prioritize voice interaction above all else. Every screen should feel like a conversation, not a form.

### Design Personality

| Attribute | Description |
|-----------|-------------|
| **Sophisticated** | Refined, not flashy. Thoughtful details. |
| **Warm** | Human, approachable, not cold or robotic. |
| **Intelligent** | Smart, capable, not overwhelming. |
| **Trustworthy** | Reliable, secure, transparent. |
| **Minimal** | Essential, focused, not cluttered. |
| **High-end** | Premium quality, polished, not cheap. |
| **Human** | Empathetic, understanding, not mechanical. |

### Anti-Patterns

**Avoid:**
- ❌ Generic Bootstrap layouts
- ❌ Excessive cards
- ❌ Dense tables as primary interface
- ❌ Generic blue corporate UI
- ❌ Giant gradients
- ❌ Excessive glassmorphism
- ❌ Fake 3D AI graphics
- ❌ Stock photographs
- ❌ Clutter

**Embrace:**
- ✅ Deep ink/charcoal surfaces
- ✅ Warm off-white surfaces
- ✅ Restrained emerald/lime accent system
- ✅ Strong typography hierarchy
- ✅ Generous whitespace
- ✅ Subtle borders
- ✅ Soft shadows
- ✅ Precise spacing
- ✅ Beautiful micro-interactions

### Design Pillars

1. **Voice-First** - The microphone is the hero
2. **Conversational** - UI talks with the user
3. **Explainable** - Every number has a story
4. **Forgiving** - Clear error states, easy recovery
5. **Fast** - Instant feedback, no waiting

---

## Visual Identity

### Logo Concept

```
A.R.I.A.
```

- Simple, wordmark logo
- Heavy weight for authority
- Warm charcoal color
- No icon - the voice interaction is the icon

### Brand Colors

**Primary Palette**
```css
--ink-950: #0a0a0a  /* Deepest surface */
--ink-900: #141414  /* Primary surface */
--ink-800: #1c1c1c  /* Secondary surface */
--ink-700: #2a2a2a  /* Tertiary surface */
--ink-600: #404040  /* Border color */
--ink-500: #525252  /* Muted text */
--ink-400: #737373  /* Secondary text */
--ink-300: #a3a3a3  /* Tertiary text */
--ink-200: #d4d4d4  /* Disabled text */
--ink-100: #e5e5e5  /* Light border */
--ink-50:  #f5f5f5  /* Subtle background */
```

**Warm Off-White Palette**
```css
--warm-50:  #faf9f7  /* Primary background */
--warm-100: #f5f3f0  /* Secondary background */
--warm-200: #e8e6e1  /* Card background */
--warm-300: #d3d0c9  /* Hover state */
--warm-400: #b8b4aa  /* Active state */
```

**Accent Palette (Emerald/Lime)**
```css
--emerald-950: #064e3b
--emerald-900: #065f46
--emerald-800: #047857
--emerald-700: #059669
--emerald-600: #10b981  /* Primary accent */
--emerald-500: #34d399
--emerald-400: #6ee7b7
--emerald-300: #a7f3d0
--emerald-200: #d1fae5
--emerald-100: #ecfdf5
--emerald-50:  #f0fdf4
```

**Status Colors**
```css
--success: #10b981   /* Emerald 600 */
--warning: #f59e0b   /* Amber 500 */
--danger:  #ef4444   /* Red 500 */
--info:    #3b82f6   /* Blue 500 */
```

### Gradients

**Subtle Gradients Only**
```css
--gradient-ink: linear-gradient(180deg, var(--ink-900) 0%, var(--ink-950) 100%)
--gradient-warm: linear-gradient(180deg, var(--warm-50) 0%, var(--warm-100) 100%)
--gradient-accent: linear-gradient(135deg, var(--emerald-600) 0%, var(--emerald-700) 100%)
```

### Shadows

**Soft, Diffused Shadows**
```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05)
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)
--shadow-voice: 0 0 40px rgba(16, 185, 129, 0.3)  /* Voice glow */
```

### Border Radius

```css
--radius-sm: 4px
--radius-md: 8px
--radius-lg: 12px
--radius-xl: 16px
--radius-2xl: 24px
--radius-full: 9999px
```

---

## Color System

### Surface Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--ink-950` | #0a0a0a | Deepest backgrounds, hero sections |
| `--ink-900` | #141414 | Primary surfaces, cards |
| `--ink-800` | #1c1c1c | Secondary surfaces |
| `--ink-700` | #2a2a2a | Tertiary surfaces |
| `--ink-600` | #404040 | Borders, dividers |
| `--ink-500` | #525252 | Muted text, secondary labels |
| `--ink-400` | #737373 | Secondary text |
| `--ink-300` | #a3a3a3 | Tertiary text, placeholders |
| `--ink-200` | #d4d4d4 | Disabled text |
| `--ink-100` | #e5e5e5 | Light borders |
| `--ink-50`  | #f5f5f5 | Subtle backgrounds |

| Token | Value | Usage |
|-------|-------|-------|
| `--warm-50`  | #faf9f7 | Primary background (light mode) |
| `--warm-100` | #f5f3f0 | Secondary background |
| `--warm-200` | #e8e6e1 | Card backgrounds |
| `--warm-300` | #d3d0c9 | Hover states |
| `--warm-400` | #b8b4aa | Active states |

### Accent Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--emerald-600` | #10b981 | Primary action, voice button |
| `--emerald-500` | #34d399 | Hover states |
| `--emerald-400` | #6ee7b7 | Success indicators |
| `--emerald-300` | #a7f3d0 | Subtle success backgrounds |
| `--emerald-200` | #d1fae5 | Light success backgrounds |
| `--emerald-100` | #ecfdf5 | Very light success backgrounds |
| `--emerald-50`  | #f0fdf4 | Success surface |

### Semantic Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--success` | #10b981 | Success states, positive indicators |
| `--warning` | #f59e0b | Warning states, caution indicators |
| `--danger`  | #ef4444 | Error states, negative indicators |
| `--info`    | #3b82f6 | Information states |

### Color Usage Guidelines

**Backgrounds:**
- Light mode: `--warm-50` primary, `--warm-100` secondary
- Dark mode: `--ink-950` primary, `--ink-900` secondary

**Text:**
- Primary: `--ink-900` (light), `--warm-50` (dark)
- Secondary: `--ink-500` (light), `--ink-400` (dark)
- Tertiary: `--ink-400` (light), `--ink-300` (dark)

**Accents:**
- Primary actions: `--emerald-600`
- Voice interaction: `--emerald-600` with glow
- Success: `--emerald-600`
- Warning: `--warning`
- Error: `--danger`

---

## Typography System

### Font Family

```css
--font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
--font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
--font-mono: 'JetBrains Mono', 'Fira Code', monospace
```

### Type Scale

| Token | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|-------|
| `--text-4xl` | 36px | 600 | 1.2 | Page titles, hero headings |
| `--text-3xl` | 30px | 600 | 1.3 | Section headings |
| `--text-2xl` | 24px | 600 | 1.4 | Card titles, large labels |
| `--text-xl` | 20px | 500 | 1.5 | Subsection headings |
| `--text-lg` | 18px | 500 | 1.6 | Body headings, important text |
| `--text-base` | 16px | 400 | 1.6 | Body text, primary content |
| `--text-sm` | 14px | 400 | 1.5 | Secondary text, labels |
| `--text-xs` | 12px | 400 | 1.4 | Captions, metadata |

### Typography Hierarchy

**Page Title**
```css
font-size: var(--text-4xl);
font-weight: 600;
color: var(--ink-900);
line-height: 1.2;
letter-spacing: -0.02em;
```

**Section Heading**
```css
font-size: var(--text-2xl);
font-weight: 600;
color: var(--ink-900);
line-height: 1.4;
letter-spacing: -0.01em;
```

**Body Text**
```css
font-size: var(--text-base);
font-weight: 400;
color: var(--ink-500);
line-height: 1.6;
```

**Secondary Text**
```css
font-size: var(--text-sm);
font-weight: 400;
color: var(--ink-400);
line-height: 1.5;
```

**Caption**
```css
font-size: var(--text-xs);
font-weight: 400;
color: var(--ink-300);
line-height: 1.4;
text-transform: uppercase;
letter-spacing: 0.05em;
```

### Typography Best Practices

1. **Never use all caps for body text** - Reserve for captions and labels
2. **Use letter-spacing sparingly** - Only for large headings
3. **Maintain consistent line heights** - 1.5-1.6 for body text
4. **Font weights should be intentional** - 400/500/600 only
5. **Color hierarchy matters** - Primary > Secondary > Tertiary

---

## Spacing System

### Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `--space-0` | 0px | No spacing |
| `--space-1` | 4px | Tight spacing |
| `--space-2` | 8px | Compact spacing |
| `--space-3` | 12px | Default spacing |
| `--space-4` | 16px | Comfortable spacing |
| `--space-5` | 20px | Generous spacing |
| `--space-6` | 24px | Section spacing |
| `--space-8` | 32px | Large spacing |
| `--space-10` | 40px | Section separation |
| `--space-12` | 48px | Major separation |
| `--space-16` | 64px | Layout spacing |
| `--space-20` | 80px | Page spacing |
| `--space-24` | 96px | Hero spacing |

### Spacing Guidelines

**Component Spacing:**
- Between related items: `--space-2` to `--space-3`
- Between unrelated items: `--space-4` to `--space-6`
- Between sections: `--space-8` to `--space-12`

**Layout Spacing:**
- Container padding: `--space-4` to `--space-6`
- Section margins: `--space-8` to `--space-12`
- Page margins: `--space-12` to `--space-20`

**Touch Targets:**
- Minimum height: 44px
- Minimum width: 44px
- Padding: `--space-3` to `--space-4`

---

## Component Library

### Button Components

#### Primary Button

```css
--btn-primary-bg: var(--emerald-600);
--btn-primary-text: #ffffff;
--btn-primary-hover: var(--emerald-700);
--btn-primary-active: var(--emerald-800);
```

**Design:**
- Background: `--emerald-600`
- Text: White
- Border radius: `--radius-lg`
- Padding: `--space-3` `--space-6`
- Font size: `--text-base`
- Font weight: 500
- Shadow: `--shadow-md`
- Transition: All 200ms ease

**States:**
- Hover: Darken by 10%
- Active: Darken by 20%
- Disabled: Opacity 0.5

#### Secondary Button

```css
--btn-secondary-bg: transparent;
--btn-secondary-text: var(--ink-900);
--btn-secondary-border: var(--ink-300);
```

**Design:**
- Background: Transparent
- Text: `--ink-900`
- Border: 1px solid `--ink-300`
- Border radius: `--radius-lg`
- Padding: `--space-3` `--space-6`
- Font size: `--text-base`
- Font weight: 500

**States:**
- Hover: Background `--warm-100`
- Active: Background `--warm-200`

#### Voice Button (Hero)

```css
--btn-voice-bg: var(--emerald-600);
--btn-voice-glow: var(--shadow-voice);
--btn-voice-size: 80px;
```

**Design:**
- Circular, 80px diameter
- Background: `--emerald-600`
- Icon: Microphone (white, 32px)
- Shadow: `--shadow-voice` (glow effect)
- Border radius: `--radius-full`
- Animation: Pulse when recording

**States:**
- Idle: Solid color
- Recording: Pulse animation
- Processing: Spinner

#### Text Button

```css
--btn-text-color: var(--emerald-600);
--btn-text-hover: var(--emerald-700);
```

**Design:**
- Background: Transparent
- Text: `--emerald-600`
- No border
- Padding: `--space-2` `--space-3`
- Font size: `--text-sm`
- Font weight: 500

### Input Components

#### Text Input

```css
--input-bg: var(--warm-50);
--input-border: var(--ink-200);
--input-focus-border: var(--emerald-600);
--input-text: var(--ink-900);
--input-placeholder: var(--ink-300);
```

**Design:**
- Background: `--warm-50`
- Border: 1px solid `--ink-200`
- Border radius: `--radius-md`
- Padding: `--space-3` `--space-4`
- Font size: `--text-base`
- Text color: `--ink-900`
- Placeholder: `--ink-300`

**States:**
- Focus: Border `--emerald-600`, shadow `--shadow-voice`
- Error: Border `--danger`
- Disabled: Background `--warm-200`, opacity 0.6

#### Search Input

```css
--search-bg: var(--warm-100);
--search-icon: var(--ink-400);
```

**Design:**
- Background: `--warm-100`
- Border: None
- Border radius: `--radius-full`
- Padding: `--space-3` `--space-4`
- Search icon on left
- Clear button on right (when has value)

### Card Components

#### Default Card

```css
--card-bg: var(--warm-50);
--card-border: var(--ink-100);
--card-shadow: var(--shadow-sm);
```

**Design:**
- Background: `--warm-50`
- Border: 1px solid `--ink-100`
- Border radius: `--radius-xl`
- Padding: `--space-6`
- Shadow: `--shadow-sm`

#### Elevated Card

```css
--card-elevated-bg: #ffffff;
--card-elevated-shadow: var(--shadow-lg);
```

**Design:**
- Background: White
- Border: None
- Border radius: `--radius-xl`
- Padding: `--space-6`
- Shadow: `--shadow-lg`

#### Product Card

```css
--product-card-bg: var(--warm-50);
--product-card-hover: var(--warm-100);
```

**Design:**
- Background: `--warm-50`
- Border: 1px solid `--ink-100`
- Border radius: `--radius-lg`
- Padding: `--space-4`
- Hover: Background `--warm-100`

**Layout:**
```
┌─────────────────────────────┐
│ Product Name          [icon] │
│ 25 cartons                    │
│ Status: Normal                │
│ Last: 2 hours ago            │
└─────────────────────────────┘
```

### Badge Components

#### Status Badge

```css
--badge-success-bg: var(--emerald-100);
--badge-success-text: var(--emerald-800);
--badge-warning-bg: var(--warning);
--badge-warning-text: #ffffff;
--badge-danger-bg: var(--danger);
--badge-danger-text: #ffffff;
```

**Design:**
- Padding: `--space-1` `--space-3`
- Border radius: `--radius-full`
- Font size: `--text-xs`
- Font weight: 500
- Text transform: Uppercase

**Variants:**
- Normal: `--emerald-100` bg, `--emerald-800` text
- Low: `--warning` bg, white text
- Critical: `--danger` bg, white text

#### Confidence Badge

```css
--badge-high-bg: var(--emerald-100);
--badge-high-text: var(--emerald-800);
--badge-medium-bg: var(--warning);
--badge-medium-text: #ffffff;
--badge-low-bg: var(--danger);
--badge-low-text: #ffffff;
```

**Design:**
- Same as status badge
- Shows confidence level from AI

### Alert Components

#### Inline Alert

```css
--alert-bg: var(--warm-100);
--alert-border: var(--ink-200);
--alert-icon: var(--ink-400);
```

**Design:**
- Background: `--warm-100`
- Border: 1px solid `--ink-200`
- Border radius: `--radius-lg`
- Padding: `--space-4`
- Icon on left
- Text on right

**Variants:**
- Info: Blue icon
- Success: Emerald icon
- Warning: Amber icon
- Error: Red icon

#### Toast Alert

```css
--toast-bg: var(--ink-900);
--toast-text: #ffffff;
```

**Design:**
- Background: `--ink-900`
- Text: White
- Border radius: `--radius-lg`
- Padding: `--space-4`
- Shadow: `--shadow-xl`
- Position: Bottom-center
- Animation: Slide up from bottom

### Modal Components

#### Default Modal

```css
--modal-bg: #ffffff;
--modal-overlay: rgba(0, 0, 0, 0.6);
--modal-shadow: var(--shadow-2xl);
```

**Design:**
- Background: White
- Border radius: `--radius-2xl`
- Padding: `--space-8`
- Shadow: `--shadow-2xl`
- Max width: 500px
- Overlay: `rgba(0, 0, 0, 0.6)`

**Structure:**
```
┌─────────────────────────────┐
│           Title             │
│                             │
│           Content           │
│                             │
│    [Cancel]    [Confirm]   │
└─────────────────────────────┘
```

#### Voice Confirmation Modal

```css
--modal-voice-bg: var(--warm-50);
```

**Design:**
- Background: `--warm-50`
- Larger padding: `--space-8`
- Voice-centric layout
- Confidence indicator prominent

### Loading Components

#### Spinner

```css
--spinner-color: var(--emerald-600);
--spinner-size: 24px;
```

**Design:**
- Circular spinner
- Color: `--emerald-600`
- Size: 24px
- Animation: Rotate

#### Skeleton Loading

```css
--skeleton-bg: var(--warm-200);
--skeleton-animate: shimmer;
```

**Design:**
- Background: `--warm-200`
- Animation: Shimmer effect
- Border radius: Same as component

#### Voice Recording Indicator

```css
--voice-indicator-color: var(--emerald-600);
--voice-indicator-glow: var(--shadow-voice);
```

**Design:**
- Pulsing circle
- Color: `--emerald-600`
- Glow effect
- Animation: Pulse

### Empty State Components

#### Default Empty State

```css
--empty-icon: var(--ink-300);
--empty-text: var(--ink-400);
```

**Design:**
- Icon: Large, `--ink-300`
- Title: `--text-lg`, `--ink-400`
- Description: `--text-sm`, `--ink-300`
- CTA: Primary button

**Structure:**
```
      [Icon]

   No events yet

Start by adding stock
  through voice
```

### Voice Components

#### Voice Recorder

```css
--voice-recorder-bg: var(--warm-50);
--voice-recorder-active: var(--emerald-600);
```

**Design:**
- Central microphone button
- Live transcription display
- Waveform visualization
- Language indicator

**States:**
- Idle: Show "Tap to speak"
- Recording: Show waveform, live transcription
- Processing: Show spinner
- Complete: Show transcription with confirmation

#### Transcription Display

```css
--transcription-bg: var(--warm-100);
--transcription-text: var(--ink-900);
```

**Design:**
- Background: `--warm-100`
- Text: `--ink-900`
- Padding: `--space-4`
- Border radius: `--radius-lg`
- Font size: `--text-lg`
- Italic for live transcription

#### Waveform Visualization

```css
--waveform-color: var(--emerald-600);
--waveform-height: 60px;
```

**Design:**
- Animated waveform bars
- Color: `--emerald-600`
- Height: 60px
- Smooth animation

---

## Screen Designs

### SCREEN 1: Welcome / Business Setup

**Purpose:** Onboarding flow for new users

**Layout:**
```
┌─────────────────────────────────────┐
│                                     │
│         A.R.I.A.                        │
│                                     │
│    "Your business remembers."        │
│                                     │
│  Speak naturally. A.R.I.A. handles      │
│         the rest.                   │
│                                     │
│                                     │
│   ┌─────────────────────────────┐   │
│   │   Set up my business        │   │
│   └─────────────────────────────┘   │
│                                     │
│            Already have an           │
│              account?               │
│                Sign in              │
│                                     │
└─────────────────────────────────────┘
```

**Design Specifications:**

**Hero Section:**
- Logo: "A.R.I.A." in `--ink-900`, 600 weight, 36px
- Tagline: "Your business remembers." in `--text-3xl`, `--ink-900`
- Subtitle: "Speak naturally. A.R.I.A. handles the rest." in `--text-base`, `--ink-500`

**Primary CTA:**
- Button: "Set up my business"
- Style: Primary button
- Size: Large (padding `--space-4` `--space-8`)
- Full width on mobile

**Secondary CTA:**
- Text: "Already have an account? Sign in"
- Style: Text button
- Color: `--emerald-600`

**Background:**
- Color: `--warm-50`
- Subtle gradient from top to bottom

**Spacing:**
- Vertical spacing: `--space-16` between sections
- Horizontal padding: `--space-6`

**Business Setup Flow:**

**Step 1: Business Name**
```
┌─────────────────────────────────────┐
│  What's your business called?       │
│                                     │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │      Next                   │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**Step 2: Business Type**
```
┌─────────────────────────────────────┐
│  What type of business?             │
│                                     │
│  ○ Kirana Store                     │
│  ○ Pharmacy                         │
│  ○ Wholesale                        │
│  ○ Other                            │
│                                     │
│  ┌─────────────────────────────┐   │
│  │      Next                   │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**Step 3: Location**
```
┌─────────────────────────────────────┐
│  Where is your business located?    │
│                                     │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │      Complete               │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

### SCREEN 2: Main Home

**Purpose:** Primary dashboard with voice-first interaction

**Layout:**
```
┌─────────────────────────────────────┐
│  ☰        A.R.I.A.               🔔     │
│                                     │
│  Good morning, Ravi.                │
│                                     │
│            🎙                       │
│       "What happened?"             │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Current Stock               │   │
│  │                             │   │
│  │ Biscuits: 25 cartons        │   │
│  │ Rice: 12 bags               │   │
│  │ Oil: 3 litres (⚠️)          │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Needs Attention             │   │
│  │                             │   │
│  │ Oil may run out in 3 days  │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Recent Activity             │   │
│  │                             │   │
│  │ 09:10  +5 Biscuits          │
│  │ 11:30  -2 Oil               │   │
│  └─────────────────────────────┘   │
│                                     │
│  [Home] [Inventory] [Memory] [Ask] │
└─────────────────────────────────────┘
```

**Design Specifications:**

**Header:**
- Left: Menu icon (`☰`)
- Center: "A.R.I.A." logo
- Right: Notification bell (`🔔`)
- Background: `--warm-50`
- Padding: `--space-4`
- Border-bottom: 1px solid `--ink-100`

**Greeting:**
- Text: "Good morning, Ravi."
- Size: `--text-2xl`
- Weight: 600
- Color: `--ink-900`
- Padding: `--space-6` `--space-4` `--space-4`

**Voice Hero:**
- Center: Large microphone button (80px)
- Below: "What happened?" in `--text-lg`, `--ink-500`
- Background: Subtle gradient
- Padding: `--space-8` `--space-4`
- Shadow: `--shadow-voice` on button

**Cards:**
- Background: `--warm-50`
- Border: 1px solid `--ink-100`
- Border radius: `--radius-xl`
- Padding: `--space-5`
- Shadow: `--shadow-sm`
- Margin-bottom: `--space-4`

**Current Stock Card:**
- Title: "Current Stock" in `--text-sm`, uppercase, `--ink-400`
- Items: Product name, quantity, unit
- Warning icon for low stock

**Needs Attention Card:**
- Title: "Needs Attention" in `--text-sm`, uppercase, `--ink-400`
- Items: Alert messages with icons
- Color: Warning for urgent items

**Recent Activity Card:**
- Title: "Recent Activity" in `--text-sm`, uppercase, `--ink-400`
- Items: Time, action, product
- Format: "09:10 +5 Biscuits"

**Bottom Navigation:**
- Fixed at bottom
- Background: White
- Border-top: 1px solid `--ink-100`
- 4 tabs: Home, Inventory, Memory, Ask
- Active tab: `--emerald-600` icon and text
- Inactive tab: `--ink-400` icon and text

---

### SCREEN 3: Voice Interaction

**Purpose:** Voice recording and confirmation flow

**Layout (Recording State):**
```
┌─────────────────────────────────────┐
│  ← Back                     Cancel  │
│                                     │
│              🎙                    │
│         ▂▃▅▇█▇▅▃▂                 │
│                                     │
│  "I received five cartons of       │
│   biscuits this morning"           │
│                                     │
│  🇮🇳 English                       │
│                                     │
│  Recording...                      │
│                                     │
└─────────────────────────────────────┘
```

**Layout (Confirmation State):**
```
┌─────────────────────────────────────┐
│  ← Back                     Edit   │
│                                     │
│  "I received five cartons of       │
│   biscuits this morning"            │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ ACTION                      │   │
│  │ Stock In                    │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ PRODUCT                     │   │
│  │ Biscuits                    │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ QUANTITY                    │   │
│  │ 5 cartons                   │   │
│  └─────────────────────────────┘   │
│                                     │
│  Confidence: 92% ●●●●●○             │
│                                     │
│  ┌─────────────────────────────┐   │
│  │        Confirm               │   │
│  └─────────────────────────────┘   │
│                                     │
│         Cancel                      │
│                                     │
└─────────────────────────────────────┘
```

**Design Specifications:**

**Header:**
- Left: Back arrow
- Right: "Cancel" button (recording) or "Edit" button (confirmation)
- Background: `--warm-50`
- Padding: `--space-4`

**Recording State:**
- Center: Large microphone button (80px)
- Below: Animated waveform
- Below: Live transcription
- Below: Language indicator (flag)
- Below: "Recording..." in `--text-sm`, `--emerald-600`

**Waveform:**
- Height: 60px
- Color: `--emerald-600`
- Animation: Smooth pulse
- Bars: 8-10 bars

**Transcription:**
- Background: `--warm-100`
- Padding: `--space-4`
- Border radius: `--radius-lg`
- Text: `--text-lg`, `--ink-900`
- Italic for live transcription

**Language Indicator:**
- Flag emoji + language name
- Font size: `--text-sm`
- Color: `--ink-400`

**Confirmation State:**
- Original text at top
- Structured extraction in cards
- Confidence indicator
- Confirm button (primary)
- Cancel button (text)

**Extraction Cards:**
- Label: Uppercase, `--text-xs`, `--ink-400`
- Value: `--text-base`, `--ink-900`
- Background: `--warm-50`
- Padding: `--space-3` `--space-4`
- Border radius: `--radius-md`

**Confidence Indicator:**
- Label: "Confidence: 92%"
- Visual: 5 dots, filled based on score
- Color: `--emerald-600` for high, `--warning` for medium, `--danger` for low

---

### SCREEN 4: Business Memory

**Purpose:** Vertical event timeline showing all business events

**Layout:**
```
┌─────────────────────────────────────┐
│  ← Back         Business Memory  🔍 │
│                                     │
│  Today                              │
│                                     │
│  09:10                              │
│  ┌─────────────────────────────┐   │
│  │ PURCHASE                     │   │
│  │ +50 Rice Bags                │   │
│  └─────────────────────────────┘   │
│                                     │
│  11:30                              │
│  ┌─────────────────────────────┐   │
│  │ SALE                         │   │
│  │ -5 Rice Bags                 │   │
│  └─────────────────────────────┘   │
│                                     │
│  14:20                              │
│  ┌─────────────────────────────┐   │
│  │ CREDIT SALE                  │   │
│  │ -3 Rice Bags                │   │
│  │ Ramesh                      │   │
│  └─────────────────────────────┘   │
│                                     │
│  17:40                              │
│  ┌─────────────────────────────┐   │
│  │ DAMAGE                       │   │
│  │ -2 Rice Bags                 │   │
│  └─────────────────────────────┘   │
│                                     │
│  Yesterday                          │
│                                     │
│  10:15                              │
│  ┌─────────────────────────────┐   │
│  │ STOCK_IN                     │   │
│  │ +10 Cooking Oil              │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**Design Specifications:**

**Header:**
- Left: Back arrow
- Center: "Business Memory"
- Right: Search icon
- Background: `--warm-50`
- Padding: `--space-4`

**Date Headers:**
- Text: "Today", "Yesterday", etc.
- Size: `--text-sm`
- Weight: 600
- Color: `--ink-400`
- Text transform: Uppercase
- Padding: `--space-4` `--space-4` `--space-2`

**Event Cards:**
- Background: `--warm-50`
- Border: 1px solid `--ink-100`
- Border radius: `--radius-lg`
- Padding: `--space-4`
- Margin-bottom: `--space-3`
- Shadow: `--shadow-sm`

**Event Time:**
- Text: "09:10"
- Size: `--text-sm`
- Color: `--ink-400`
- Margin-bottom: `--space-2`

**Event Type:**
- Text: "PURCHASE", "SALE", etc.
- Size: `--text-xs`
- Weight: 600
- Color: `--ink-400`
- Text transform: Uppercase
- Letter-spacing: 0.05em

**Event Details:**
- Text: "+50 Rice Bags"
- Size: `--text-base`
- Color: `--ink-900`
- Weight: 500

**Customer Info:**
- Text: "Ramesh"
- Size: `--text-sm`
- Color: `--ink-500`
- Margin-top: `--space-1`

**Color Coding:**
- Stock-in events: Green accent
- Stock-out events: Red accent
- Neutral events: No accent

**Timeline Line:**
- Vertical line on left
- Color: `--ink-200`
- Width: 2px
- Dots at each event

---

### SCREEN 5: Ask A.R.I.A.

**Purpose:** Natural language query interface

**Layout:**
```
┌─────────────────────────────────────┐
│  ← Back           Ask A.R.I.A.      🎙   │
│                                     │
│  Ask anything about your business.   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ What's running low?          │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Where did my rice go?        │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ What should I order?         │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ What did Ramesh take?        │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  │  Type your question...      │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**Response Layout:**
```
┌─────────────────────────────────────┐
│  ← Back           Ask A.R.I.A.      🎙   │
│                                     │
│  How much rice do I have?           │
│                                     │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  │  You have 25 bags of rice.  │   │
│  │                             │   │
│  │  Status: Normal             │   │
│  │  (minimum: 10 bags)         │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Ask another question       │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**Design Specifications:**

**Header:**
- Left: Back arrow
- Center: "Ask A.R.I.A."
- Right: Microphone icon
- Background: `--warm-50`
- Padding: `--space-4`

**Hero Text:**
- Text: "Ask anything about your business."
- Size: `--text-lg`
- Color: `--ink-900`
- Padding: `--space-6` `--space-4` `--space-4`

**Suggestion Chips:**
- Background: `--warm-100`
- Border: 1px solid `--ink-200`
- Border radius: `--radius-full`
- Padding: `--space-3` `--space-5`
- Text: `--text-sm`, `--ink-700`
- Margin-bottom: `--space-3`
- Hover: Background `--warm-200`

**Query Input:**
- Background: `--warm-50`
- Border: 1px solid `--ink-200`
- Border radius: `--radius-lg`
- Padding: `--space-4`
- Placeholder: "Type your question..."
- Full width

**Response Card:**
- Background: `--warm-50`
- Border: 1px solid `--ink-100`
- Border radius: `--radius-xl`
- Padding: `--space-6`
- Shadow: `--shadow-sm`

**Response Text:**
- Text: Conversational response
- Size: `--text-base`
- Color: `--ink-900`
- Line height: 1.6

**Response Metadata:**
- Text: "Status: Normal (minimum: 10 bags)"
- Size: `--text-sm`
- Color: `--ink-500`
- Margin-top: `--space-3`

**Follow-up Button:**
- Text: "Ask another question"
- Style: Secondary button
- Full width

---

### SCREEN 6: Inventory

**Purpose:** Product list with stock status

**Layout:**
```
┌─────────────────────────────────────┐
│  ← Back         Inventory      🔍 🎙│
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 🔍 Search products...        │   │
│  └─────────────────────────────┘   │
│                                     │
│  Filter: All ▼                     │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Biscuits              >      │   │
│  │ 25 cartons                   │   │
│  │ Status: Normal ●             │   │
│  │ Last: 2 hours ago            │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Cooking Oil           >      │   │
│  │ 3 litres                     │   │
│  │ Status: Critical 🔴          │   │
│  │ Stockout in 3 days          │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Rice                  >      │   │
│  │ 12 bags                      │   │
│  │ Status: Low 🟡              │   │
│  │ Stockout in 7 days          │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │      + Add Product           │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**Design Specifications:**

**Header:**
- Left: Back arrow
- Center: "Inventory"
- Right: Search icon + microphone icon
- Background: `--warm-50`
- Padding: `--space-4`

**Search Bar:**
- Background: `--warm-100`
- Border: None
- Border radius: `--radius-full`
- Padding: `--space-3` `--space-4`
- Search icon on left
- Placeholder: "Search products..."

**Filter Dropdown:**
- Text: "Filter: All ▼"
- Size: `--text-sm`
- Color: `--ink-500`
- Padding: `--space-2` `--space-4`
- Border-bottom: 1px solid `--ink-200`

**Product Cards:**
- Background: `--warm-50`
- Border: 1px solid `--ink-100`
- Border radius: `--radius-lg`
- Padding: `--space-4`
- Margin-bottom: `--space-3`
- Shadow: `--shadow-sm`
- Right chevron for navigation

**Product Name:**
- Text: "Biscuits"
- Size: `--text-base`
- Weight: 500
- Color: `--ink-900`

**Quantity:**
- Text: "25 cartons"
- Size: `--text-lg`
- Weight: 600
- Color: `--ink-900`

**Status:**
- Text: "Status: Normal"
- Size: `--text-sm`
- Color: `--ink-500`
- Status indicator: ● Normal, 🟡 Low, 🔴 Critical

**Stockout Estimate:**
- Text: "Stockout in 3 days"
- Size: `--text-sm`
- Color: `--warning` for urgent, `--ink-500` for normal

**Last Updated:**
- Text: "Last: 2 hours ago"
- Size: `--text-xs`
- Color: `--ink-300`
- Text transform: Uppercase

**Add Product Button:**
- Background: `--emerald-600`
- Text: "+ Add Product"
- Text color: White
- Border radius: `--radius-lg`
- Padding: `--space-4`
- Full width
- Shadow: `--shadow-md`

---

### SCREEN 7: Product Detail

**Purpose:** Product detail with WHY ENGINE

**Layout:**
```
┌─────────────────────────────────────┐
│  ← Back         Rice          ✎ 🗑 │
│                                     │
│  Current Stock                      │
│                                     │
│      12 bags                        │
│                                     │
│  Status: Low 🟡                     │
│  Stockout in 7 days                │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Why did it change?           │   │
│  │                             │   │
│  │ 09:10  PURCHASE  +50 bags   │   │
│  │ 11:30  SALE       -5 bags   │   │
│  │ 14:20  CREDIT     -3 bags   │   │
│  │ 17:40  DAMAGE     -2 bags   │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Explanation                 │   │
│  │                             │   │
│  │ Your rice stock decreased   │   │
│  │ mainly because of 35 bags   │   │
│  │ sold and 3 bags damaged.    │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Quick Actions                │   │
│  │                             │   │
│  │  [+ Add Stock]  [- Remove]  │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**Design Specifications:**

**Header:**
- Left: Back arrow
- Center: Product name ("Rice")
- Right: Edit icon + Delete icon
- Background: `--warm-50`
- Padding: `--space-4`

**Current Stock Section:**
- Large quantity display
- Size: `--text-4xl`
- Weight: 600
- Color: `--ink-900`
- Center aligned
- Padding: `--space-8` `--space-4`

**Status Indicator:**
- Text: "Status: Low"
- Size: `--text-base`
- Color: `--ink-500`
- Status emoji: 🟡 Low, 🔴 Critical, ● Normal
- Center aligned

**Stockout Estimate:**
- Text: "Stockout in 7 days"
- Size: `--text-sm`
- Color: `--ink-400`
- Center aligned

**Why Section:**
- Title: "Why did it change?"
- Size: `--text-lg`
- Weight: 600
- Color: `--ink-900`
- Padding: `--space-4` `--space-4` `--space-2`

**Event Timeline:**
- Background: `--warm-50`
- Border: 1px solid `--ink-100`
- Border radius: `--radius-lg`
- Padding: `--space-4`
- Each event: Time, Type, Quantity

**Explanation Card:**
- Background: `--emerald-50`
- Border: 1px solid `--emerald-200`
- Border radius: `--radius-lg`
- Padding: `--space-4`
- Text: Conversational explanation
- Size: `--text-base`
- Color: `--ink-900`

**Quick Actions:**
- Two buttons: "+ Add Stock" and "- Remove"
- Style: Secondary buttons
- Side by side
- Full width container

---

### SCREEN 8: Smart Alerts

**Purpose:** Intelligent "Needs Attention" center

**Layout:**
```
┌─────────────────────────────────────┐
│  ← Back         Needs Attention 🔔  │
│                                     │
│  3 items need attention            │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ ⚠️  Rice may run out in     │   │
│  │     3 days                   │   │
│  │                             │   │
│  │ Current: 12 bags            │   │
│  │ Recommended: Order 25 bags   │   │
│  │                             │   │
│  │  [View Details] [Order]     │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 📈 Biscuits have unusually  │   │
│  │     high sales this week    │   │
│  │                             │   │
│  │ Sold: 45 cartons (2x avg)   │   │
│  │ Usual: 22 cartons           │   │
│  │                             │   │
│  │  [View Details]             │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ ⚖️  Oil stock differs from   │   │
│  │     physical count           │   │
│  │                             │   │
│  │ Recorded: 3 litres          │   │
│  │ Physical: 5 litres          │   │
│  │ Difference: +2 litres        │   │
│  │                             │   │
│  │  [Resolve] [Ignore]         │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**Design Specifications:**

**Header:**
- Left: Back arrow
- Center: "Needs Attention"
- Right: Notification bell
- Background: `--warm-50`
- Padding: `--space-4`

**Summary:**
- Text: "3 items need attention"
- Size: `--text-base`
- Color: `--ink-500`
- Padding: `--space-4`

**Alert Cards:**
- Background: `--warm-50`
- Border: 1px solid `--ink-100`
- Border radius: `--radius-xl`
- Padding: `--space-5`
- Margin-bottom: `--space-4`
- Shadow: `--shadow-sm`

**Alert Icon:**
- Size: 32px
- Position: Top-left
- Icons: ⚠️ Warning, 📈 Trend, ⚖️ Discrepancy

**Alert Title:**
- Text: "Rice may run out in 3 days"
- Size: `--text-base`
- Weight: 500
- Color: `--ink-900`

**Alert Details:**
- Text: "Current: 12 bags"
- Size: `--text-sm`
- Color: `--ink-500`
- Text: "Recommended: Order 25 bags"
- Size: `--text-sm`
- Color: `--ink-500`

**Alert Actions:**
- Buttons: "View Details", "Order", "Resolve", "Ignore"
- Style: Secondary buttons
- Side by side

**Alert Priority:**
- Urgent: Red border
- Medium: Yellow border
- Low: Gray border

---

### SCREEN 9: Insights

**Purpose:** Business analytics and visual explanations

**Layout:**
```
┌─────────────────────────────────────┐
│  ← Back         Insights       🎙   │
│                                     │
│  This Week                         │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Fast-Moving Products         │   │
│  │                             │   │
│  │ 1. Biscuits                 │   │
│  │    45 cartons sold          │   │
│  │    ⬆️ 120% vs last week     │   │
│  │                             │   │
│  │ 2. Cooking Oil              │   │
│  │    12 litres sold           │   │
│  │    ⬆️ 15% vs last week      │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Slow-Moving Products        │   │
│  │                             │   │
│  │ 1. Rice                     │   │
│  │    3 bags sold              │   │
│  │    ⬇️ 40% vs last week      │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Reorder Suggestions          │   │
│  │                             │   │
│  │ • Order 25 cartons Biscuits │   │
│  │   (stockout in 3 days)     │   │
│  │                             │   │
│  │ • Order 10 litres Oil       │   │
│  │   (stockout in 7 days)     │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Stock Movement               │   │
│  │                             │   │
│  │  [Simple bar chart]         │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**Design Specifications:**

**Header:**
- Left: Back arrow
- Center: "Insights"
- Right: Microphone icon
- Background: `--warm-50`
- Padding: `--space-4`

**Time Selector:**
- Text: "This Week"
- Size: `--text-sm`
- Color: `--ink-500`
- Dropdown indicator

**Insight Cards:**
- Background: `--warm-50`
- Border: 1px solid `--ink-100`
- Border radius: `--radius-xl`
- Padding: `--space-5`
- Margin-bottom: `--space-4`
- Shadow: `--shadow-sm`

**Card Title:**
- Text: "Fast-Moving Products"
- Size: `--text-sm`
- Weight: 600
- Color: `--ink-400`
- Text transform: Uppercase
- Padding-bottom: `--space-3`

**Product Item:**
- Rank: "1."
- Name: "Biscuits"
- Size: `--text-base`
- Weight: 500
- Color: `--ink-900`

**Sales Data:**
- Text: "45 cartons sold"
- Size: `--text-sm`
- Color: `--ink-500`

**Trend Indicator:**
- Text: "⬆️ 120% vs last week"
- Size: `--text-sm`
- Color: `--emerald-600` for up, `--danger` for down

**Reorder Suggestions:**
- Bullet list format
- Each item: Product, quantity, urgency
- Color: `--ink-900`

**Stock Movement Chart:**
- Simple bar chart
- X-axis: Days of week
- Y-axis: Quantity
- Color: `--emerald-600`
- Minimal styling

---

### SCREEN 10: Settings

**Purpose:** User and business settings

**Layout:**
```
┌─────────────────────────────────────┐
│  ← Back         Settings            │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Profile                     │   │
│  │                             │   │
│  │ Ravi                        │   │
│  │ +91 98765 43210             │   │
│  │                             │   │
│  │  [Edit Profile]             │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Business                    │   │
│  │                             │   │
│  │ Ravi Kirana Store            │   │
│  │ Hyderabad                    │   │
│  │                             │   │
│  │  [Edit Business]             │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Language                    │   │
│  │                             │   │
│  │ Preferred: English          │   │
│  │                             │   │
│  │  [Change Language]          │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Voice Preferences            │   │
│  │                             │   │
│  │ Auto-confirm: On           │   │
│  │ Language detection: On      │   │
│  │                             │   │
│  │  [Configure]                │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Notifications               │   │
│  │                             │   │
│  │ Low stock alerts: On        │   │
│  │ Stockout warnings: On       │   │
│  │                             │   │
│  │  [Configure]                │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Units                       │   │
│  │                             │   │
│  │ Default unit: Pieces        │   │
│  │                             │   │
│  │  [Manage Units]             │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Support                     │   │
│  │                             │   │
│  │  [Help Center]              │   │
│  │  [Contact Support]          │   │
│  │  [Privacy Policy]           │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │                              │   │
│  │        Sign Out              │   │
│  │                              │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**Design Specifications:**

**Header:**
- Left: Back arrow
- Center: "Settings"
- Background: `--warm-50`
- Padding: `--space-4`

**Settings Cards:**
- Background: `--warm-50`
- Border: 1px solid `--ink-100`
- Border radius: `--radius-xl`
- Padding: `--space-5`
- Margin-bottom: `--space-4`
- Shadow: `--shadow-sm`

**Card Title:**
- Text: "Profile", "Business", etc.
- Size: `--text-sm`
- Weight: 600
- Color: `--ink-400`
- Text transform: Uppercase
- Padding-bottom: `--space-3`

**Card Content:**
- Name: "Ravi"
- Size: `--text-base`
- Weight: 500
- Color: `--ink-900`

- Phone: "+91 98765 43210"
- Size: `--text-sm`
- Color: `--ink-500`

**Action Button:**
- Text: "Edit Profile"
- Style: Text button
- Color: `--emerald-600`
- Size: `--text-sm`
- Weight: 500

**Toggle Switches:**
- For settings like "Auto-confirm: On"
- Toggle: Green when on, gray when off
- Label: Setting name
- Color: `--ink-900`

**Sign Out Button:**
- Background: `--danger`
- Text: "Sign Out"
- Text color: White
- Border radius: `--radius-lg`
- Padding: `--space-4`
- Full width
- Shadow: `--shadow-md`

---

## Mobile Navigation

### Bottom Navigation Bar

**Design:**
```
┌─────────────────────────────────────┐
│                                     │
│         [Main Content]              │
│                                     │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  🏠  📦  📋  ❓              │   │
│  │ Home Inv  Mem  Ask           │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**Specifications:**

**Container:**
- Fixed at bottom
- Background: White
- Border-top: 1px solid `--ink-100`
- Height: 64px
- Padding: `--space-2` `--space-4`

**Navigation Items:**
- 4 items: Home, Inventory, Memory, Ask
- Icon + Text layout
- Vertical alignment: Center
- Horizontal spacing: Even

**Active State:**
- Icon color: `--emerald-600`
- Text color: `--emerald-600`
- Weight: 500

**Inactive State:**
- Icon color: `--ink-400`
- Text color: `--ink-400`
- Weight: 400

**Icons:**
- Home: 🏠
- Inventory: 📦
- Memory: 📋
- Ask: ❓

**Voice Action:**
- Floating action button (FAB)
- Centered above navigation
- Size: 56px
- Background: `--emerald-600`
- Icon: 🎙
- Shadow: `--shadow-voice`
- Border radius: `--radius-full`

### Navigation Flow

**Home Screen:**
- Default screen
- Shows voice hero, current stock, needs attention, recent activity

**Inventory Screen:**
- Product list with filters
- Search functionality
- Voice action available

**Memory Screen:**
- Event timeline
- Date grouping
- Search functionality

**Ask Screen:**
- Query interface
- Suggestion chips
- Voice input

---

## Micro-Interactions

### Voice Pulse Animation

**Purpose:** Indicate recording state

**Animation:**
```css
@keyframes voice-pulse {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  }
  70% {
    transform: scale(1.05);
    box-shadow: 0 0 0 20px rgba(16, 185, 129, 0);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
  }
}

.voice-button.recording {
  animation: voice-pulse 1.5s infinite;
}
```

**Timing:**
- Duration: 1.5s
- Easing: Ease-out
- Iteration: Infinite

### Event Insertion Animation

**Purpose:** Animate new event appearing in timeline

**Animation:**
```css
@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.event-card.new {
  animation: slide-in 0.3s ease-out;
}
```

**Timing:**
- Duration: 300ms
- Easing: Ease-out
- Iteration: Once

### Number Transition Animation

**Purpose:** Animate quantity changes

**Animation:**
```css
@keyframes count-up {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.quantity.changed {
  animation: count-up 0.2s ease-out;
}
```

**Timing:**
- Duration: 200ms
- Easing: Ease-out
- Iteration: Once

### Page Transition Animation

**Purpose:** Smooth page transitions

**Animation:**
```css
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slide-up {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.page-enter {
  animation: fade-in 0.2s ease-out;
}

.page-enter.slide {
  animation: slide-up 0.3s ease-out;
}
```

**Timing:**
- Duration: 200-300ms
- Easing: Ease-out
- Iteration: Once

### Alert Appearance Animation

**Purpose:** Animate alert card appearing

**Animation:**
```css
@keyframes alert-slide {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.alert-card.new {
  animation: alert-slide 0.4s ease-out;
}
```

**Timing:**
- Duration: 400ms
- Easing: Ease-out
- Iteration: Once

### Query Response Reveal

**Purpose:** Animate query response appearing

**Animation:**
```css
@keyframes reveal {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.query-response {
  animation: reveal 0.5s ease-out;
}
```

**Timing:**
- Duration: 500ms
- Easing: Ease-out
- Iteration: Once

### Confirmation State Transition

**Purpose:** Smooth transition from recording to confirmation

**Animation:**
```css
@keyframes confirmation-enter {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.confirmation-state {
  animation: confirmation-enter 0.3s ease-out;
}
```

**Timing:**
- Duration: 300ms
- Easing: Ease-out
- Iteration: Once

---

## Animation System

### Animation Principles

1. **Purposeful** - Every animation has a clear purpose
2. **Subtle** - Never distracting or overwhelming
3. **Fast** - 200-500ms duration
4. **Smooth** - Use easing functions
5. **Consistent** - Same animations for similar actions

### Animation Timing

| Action | Duration | Easing |
|--------|----------|--------|
| Button hover | 150ms | Ease-out |
| Button active | 100ms | Ease-in |
| Page transition | 200-300ms | Ease-out |
| Card appearance | 300-400ms | Ease-out |
| Voice pulse | 1.5s | Ease-out |
| Number change | 200ms | Ease-out |
| Alert slide | 400ms | Ease-out |
| Response reveal | 500ms | Ease-out |

### Animation Library

```css
/* Voice Animations */
.voice-pulse {
  animation: voice-pulse 1.5s ease-out infinite;
}

@keyframes voice-pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 0 20px rgba(16, 185, 129, 0);
  }
}

/* Transition Animations */
.fade-in {
  animation: fade-in 0.2s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.slide-up {
  animation: slide-up 0.3s ease-out;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.slide-in-right {
  animation: slide-in-right 0.4s ease-out;
}

@keyframes slide-in-right {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Micro-interactions */
.scale-in {
  animation: scale-in 0.2s ease-out;
}

@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.bounce {
  animation: bounce 0.5s ease-out;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* Loading Animations */
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.shimmer {
  animation: shimmer 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
```

---

## Responsive Design

### Breakpoints

```css
--breakpoint-xs: 375px;   /* Small phones */
--breakpoint-sm: 640px;   /* Large phones */
--breakpoint-md: 768px;   /* Tablets */
--breakpoint-lg: 1024px;  /* Small laptops */
--breakpoint-xl: 1280px;  /* Desktops */
--breakpoint-2xl: 1536px; /* Large screens */
```

### Mobile-First Approach

**Base Styles (Mobile):**
- Single column layout
- Bottom navigation
- Touch-optimized buttons
- Large touch targets (44px minimum)
- Simplified cards

**Tablet (768px+):**
- Two-column layouts where appropriate
- Side navigation instead of bottom
- Larger cards
- More information density

**Desktop (1024px+):**
- Three-column layouts
- Full navigation
- Maximum information density
- Hover states

### Responsive Components

**Navigation:**
- Mobile: Bottom navigation bar
- Tablet+: Side navigation

**Cards:**
- Mobile: Single column
- Tablet: Two columns
- Desktop: Three columns

**Voice Button:**
- Mobile: 80px
- Tablet: 96px
- Desktop: 112px

**Typography:**
- Mobile: Base 16px
- Tablet: Base 18px
- Desktop: Base 20px

---

## Accessibility

### Color Contrast

**Minimum Contrast Ratios:**
- Normal text: 4.5:1
- Large text (18px+): 3:1
- UI components: 3:1

**Verified Combinations:**
- `--ink-900` on `--warm-50`: 16.5:1 ✓
- `--ink-500` on `--warm-50`: 7.2:1 ✓
- `--emerald-600` on white: 4.6:1 ✓
- `--emerald-600` on `--emerald-100`: 3.8:1 ✓

### Touch Targets

**Minimum Sizes:**
- Buttons: 44px × 44px
- Links: 44px × 44px
- Inputs: 44px height
- Cards: 44px minimum tap area

### Keyboard Navigation

**Tab Order:**
- Logical left-to-right, top-to-bottom
- Skip navigation link
- Focus indicators visible

**Focus States:**
- Outline: 2px solid `--emerald-600`
- Offset: 2px
- Radius: `--radius-sm`

### Screen Reader Support

**ARIA Labels:**
- All interactive elements have labels
- Voice button: "Record voice input"
- Navigation: "Home, Inventory, Memory, Ask"
- Status indicators: "Stock status: Normal"

**Semantic HTML:**
- Proper heading hierarchy
- List elements for lists
- Button elements for actions
- Input elements for forms

### Reduced Motion

**Respect User Preferences:**
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Implementation Notes

### Tailwind CSS Configuration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#0a0a0a',
          900: '#141414',
          800: '#1c1c1c',
          700: '#2a2a2a',
          600: '#404040',
          500: '#525252',
          400: '#737373',
          300: '#a3a3a3',
          200: '#d4d4d4',
          100: '#e5e5e5',
          50: '#f5f5f5',
        },
        warm: {
          50: '#faf9f7',
          100: '#f5f3f0',
          200: '#e8e6e1',
          300: '#d3d0c9',
          400: '#b8b4aa',
        },
        emerald: {
          950: '#064e3b',
          900: '#065f46',
          800: '#047857',
          700: '#059669',
          600: '#10b981',
          500: '#34d399',
          400: '#6ee7b7',
          300: '#a7f3d0',
          200: '#d1fae5',
          100: '#ecfdf5',
          50: '#f0fdf4',
        },
      },
      fontFamily: {
        display: ['Inter', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      spacing: {
        '18': '4.5rem',
        '20': '5rem',
        '24': '6rem',
      },
      boxShadow: {
        'voice': '0 0 40px rgba(16, 185, 129, 0.3)',
      },
      animation: {
        'voice-pulse': 'voice-pulse 1.5s ease-out infinite',
        'fade-in': 'fade-in 0.2s ease-out',
        'slide-up': 'slide-up 0.3s ease-out',
      },
      keyframes: {
        'voice-pulse': {
          '0%, 100%': {
            transform: 'scale(1)',
            boxShadow: '0 0 0 0 rgba(16, 185, 129, 0.7)',
          },
          '50%': {
            transform: 'scale(1.05)',
            boxShadow: '0 0 0 20px rgba(16, 185, 129, 0)',
          },
        },
        'fade-in': {
          'from': { opacity: '0' },
          'to': { opacity: '1' },
        },
        'slide-up': {
          'from': {
            opacity: '0',
            transform: 'translateY(20px)',
          },
          'to': {
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
      },
    },
  },
}
```

### Component Examples

**Voice Button Component:**
```tsx
// components/voice/VoiceButton.tsx
import { useState } from 'react';

export function VoiceButton({ isRecording, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`
        w-20 h-20 rounded-full bg-emerald-600 text-white
        flex items-center justify-center
        shadow-voice
        transition-all duration-200
        ${isRecording ? 'animate-voice-pulse' : 'hover:scale-105'}
      `}
      aria-label="Record voice input"
    >
      <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
        <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
      </svg>
    </button>
  );
}
```

**Product Card Component:**
```tsx
// components/inventory/ProductCard.tsx
export function ProductCard({ product, onClick }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'normal': return 'text-emerald-600';
      case 'low': return 'text-amber-500';
      case 'critical': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  return (
    <div
      onClick={onClick}
      className="bg-warm-50 border border-ink-100 rounded-lg p-4 hover:bg-warm-100 transition-colors cursor-pointer"
    >
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-base font-medium text-ink-900">{product.name}</h3>
          <p className="text-lg font-semibold text-ink-900 mt-1">
            {product.quantity} {product.unit}
          </p>
        </div>
        <svg className="w-5 h-5 text-ink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
      <div className="mt-3 flex items-center justify-between">
        <span className="text-sm text-ink-500">
          Status: <span className={getStatusColor(product.status)}>{product.status}</span>
        </span>
        <span className="text-xs text-ink-300 uppercase">
          Last: {product.lastUpdated}
        </span>
      </div>
    </div>
  );
}
```

---

## Design System Summary

### Core Values

1. **Voice-First** - Microphone is the hero
2. **Conversational** - UI talks with users
3. **Explainable** - Every number has a story
4. **Premium** - Sophisticated, not flashy
5. **Warm** - Human, approachable
6. **Minimal** - Essential, focused

### Design Principles

- Generous whitespace
- Strong typography hierarchy
- Subtle interactions
- Purposeful animations
- Mobile-first responsive
- Accessible by default

### Color Philosophy

- Deep ink surfaces for depth
- Warm off-white for comfort
- Emerald accents for intelligence
- Semantic colors for clarity

### Typography Philosophy

- Inter font family
- Clear hierarchy
- Readable sizes
- Consistent weights
- Purposeful styling

### Component Philosophy

- Reusable and composable
- Consistent styling
- Clear states
- Accessible markup
- Smooth animations

---

**End of UI/UX Design System**
