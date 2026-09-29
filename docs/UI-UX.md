# 🎨 UI/UX Design Guide

> **Project:** [Project Name]
> **Design Tool:** Figma
> **Figma Link:** [Paste Figma URL here]
> **Component Library:** shadcn/ui + Tailwind CSS
> **Last Updated:** [YYYY-MM-DD]
> **Designer:** [Name]

---

## 🎯 1. Design Philosophy

> Apne product ke design ke baare mein 2-3 lines mein philosophy likhon.

```
Example:
"[Project Name] ka design clean, minimal, aur purposeful hai.
Hum complexity ko hide karte hain aur simplicity ko celebrate karte hain.
Har element koi purpose serve karta hai — koi decoration nahi."
```

### Design Principles

| Principle | Description |
|-----------|-------------|
| ✨ **Clarity** | Har screen ek kaam kare aur clearly communicate kare |
| ⚡ **Speed** | User ko koi bhi action 3 clicks mein complete karna chahiye |
| 🤝 **Consistency** | Ek jaisi language, patterns, aur behaviors everywhere |
| ♿ **Accessibility** | WCAG 2.1 AA compliance — sab ke liye usable |
| 📱 **Mobile First** | Mobile se design karo, desktop pe expand karo |

---

## 🎨 2. Color System

### Brand Colors
```css
/* Primary Brand */
--color-primary-50:  #f0f9ff;
--color-primary-100: #e0f2fe;
--color-primary-500: #0ea5e9;   /* Main brand color */
--color-primary-600: #0284c7;   /* Hover state */
--color-primary-700: #0369a1;   /* Active state */
--color-primary-900: #0c4a6e;

/* Secondary */
--color-secondary-500: #8b5cf6;  /* Accent/highlight */
--color-secondary-600: #7c3aed;
```

### Semantic Colors
```css
/* Status Colors */
--color-success:  #22c55e;  /* Green — success messages */
--color-warning:  #f59e0b;  /* Amber — warnings */
--color-error:    #ef4444;  /* Red — errors */
--color-info:     #3b82f6;  /* Blue — info messages */

/* Neutral Grays */
--color-gray-50:  #f9fafb;   /* Page background */
--color-gray-100: #f3f4f6;   /* Card background */
--color-gray-200: #e5e7eb;   /* Border */
--color-gray-400: #9ca3af;   /* Placeholder text */
--color-gray-600: #4b5563;   /* Secondary text */
--color-gray-800: #1f2937;   /* Primary text */
--color-gray-900: #111827;   /* Headings */
```

### Dark Mode (If applicable)
```css
[data-theme="dark"] {
  --color-bg:       #0f172a;
  --color-surface:  #1e293b;
  --color-border:   #334155;
  --color-text:     #f1f5f9;
  --color-muted:    #94a3b8;
}
```

### Tailwind Config
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        }
      }
    }
  }
}
```


## 🔤 3. Typography

### Font Family
```css
/* Heading Font */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

/* Body Font */
font-family: 'Inter', sans-serif;

/* Mono (Code) */
font-family: 'JetBrains Mono', 'Fira Code', monospace;
```

### Type Scale
| Name | Size | Weight | Line Height | Usage |
|------|------|--------|-------------|-------|
| `display` | 48px / 3rem | 700 | 1.1 | Hero headlines |
| `h1` | 36px / 2.25rem | 700 | 1.2 | Page titles |
| `h2` | 30px / 1.875rem | 600 | 1.25 | Section titles |
| `h3` | 24px / 1.5rem | 600 | 1.3 | Card titles |
| `h4` | 20px / 1.25rem | 600 | 1.4 | Subsections |
| `body-lg` | 18px / 1.125rem | 400 | 1.7 | Lead paragraphs |
| `body` | 16px / 1rem | 400 | 1.6 | Body text |
| `body-sm` | 14px / 0.875rem | 400 | 1.5 | Secondary text |
| `caption` | 12px / 0.75rem | 400 | 1.4 | Labels, captions |
| `code` | 14px / 0.875rem | 400 | 1.5 | Code snippets |

---

## 📐 4. Spacing & Layout

### Spacing Scale (Tailwind defaults)
```
4px  = space-1
8px  = space-2
12px = space-3
16px = space-4   ← Base unit
24px = space-6
32px = space-8
48px = space-12
64px = space-16
```

### Layout Grid
```
Mobile (< 768px):  1 column, 16px gutters
Tablet (768–1024): 2 columns, 24px gutters
Desktop (> 1024):  12 column grid, 32px gutters, 1280px max-width
```

### Border Radius
```css
--radius-sm: 4px;    /* Badges, tags */
--radius-md: 8px;    /* Buttons, inputs */
--radius-lg: 12px;   /* Cards */
--radius-xl: 16px;   /* Modals */
--radius-full: 9999px; /* Avatars, pills */
```

---

## 🧱 5. Component Library

### Buttons

```jsx
// Primary Button
<Button variant="default" size="default">
  Save Changes
</Button>

// Secondary / Outline
<Button variant="outline">
  Cancel
</Button>

// Danger / Destructive
<Button variant="destructive">
  Delete Account
</Button>

// Loading State
<Button disabled>
  <Loader2 className="animate-spin mr-2" />
  Saving...
</Button>
```

**Button Sizes:**
| Size | Height | Padding | Font |
|------|--------|---------|------|
| `sm` | 32px | 12px | 14px |
| `default` | 40px | 16px | 16px |
| `lg` | 48px | 24px | 18px |

---

### Form Elements

```jsx
// Input
<div className="space-y-2">
  <Label htmlFor="email">Email</Label>
  <Input
    id="email"
    type="email"
    placeholder="you@example.com"
    className="w-full"
  />
  <p className="text-sm text-red-500">Error message here</p>
</div>

// Select
<Select>
  <SelectTrigger>
    <SelectValue placeholder="Select option" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="option1">Option 1</SelectItem>
  </SelectContent>
</Select>

// Textarea
<Textarea placeholder="Type your message..." rows={4} />

// Checkbox
<div className="flex items-center space-x-2">
  <Checkbox id="terms" />
  <label htmlFor="terms">I agree to terms</label>
</div>
```

---

### Cards

```jsx
// Standard Card
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card subtitle or description</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Card body content */}
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

---

### Feedback & States

```jsx
// Toast Notifications
toast.success("Profile updated successfully!")
toast.error("Something went wrong. Please try again.")
toast.info("New version available.")

// Alert Component
<Alert variant="destructive">
  <AlertTitle>Error</AlertTitle>
  <AlertDescription>Your session has expired. Please login again.</AlertDescription>
</Alert>

// Empty State
<div className="flex flex-col items-center justify-center py-16">
  <EmptyIcon className="h-16 w-16 text-gray-300 mb-4" />
  <h3 className="text-lg font-semibold text-gray-700">No items yet</h3>
  <p className="text-gray-500 text-sm mt-1">Create your first item to get started.</p>
  <Button className="mt-4">Create Item</Button>
</div>

// Loading Skeleton
<Skeleton className="h-4 w-full mb-2" />
<Skeleton className="h-4 w-3/4" />
```

---

## 📱 6. Screen Layouts

### Authenticated App Layout
```
┌─────────────────────────────────────────────┐
│              Top Navigation Bar              │
│  [Logo]   [Nav Links]    [User Avatar ▼]    │
├───────────┬─────────────────────────────────┤
│           │                                 │
│  Sidebar  │         Main Content            │
│           │                                 │
│  - Link 1 │  [Page Title]                   │
│  - Link 2 │                                 │
│  - Link 3 │  [Content Area]                 │
│  - Link 4 │                                 │
│           │                                 │
│  [User]   │                                 │
│  [Logout] │                                 │
│           │                                 │
└───────────┴─────────────────────────────────┘
```

### Auth Pages Layout
```
┌─────────────────────────────────────────────┐
│                                             │
│              [Logo]                         │
│                                             │
│         ┌─────────────────┐                 │
│         │                 │                 │
│         │    Auth Form    │                 │
│         │                 │                 │
│         │  [Input field]  │                 │
│         │  [Input field]  │                 │
│         │                 │                 │
│         │  [Submit Btn]   │                 │
│         │                 │                 │
│         │  "Already have  │                 │
│         │   an account?"  │                 │
│         └─────────────────┘                 │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🗺️ 7. User Flows

### New User Onboarding Flow
```
Landing Page
     ↓
Sign Up (Email + Password)
     ↓
Email Verification Sent
     ↓
Verify Email (Click link)
     ↓
Welcome Screen / Onboarding Tour
     ↓
Setup Profile (name, avatar)
     ↓
Dashboard (First Visit)
     ↓
Empty State with CTA
     ↓
Create First [Feature]
     ↓
Success! 🎉
```

### Happy Path — Core Feature
```
User on Dashboard
     ↓
Click "Create New" button
     ↓
Fill Form (Validation feedback)
     ↓
Submit → Loading state
     ↓
Success toast + redirect
     ↓
See new item in list
     ↓
Click item → Detail view
     ↓
Edit / Delete options
```

---

## ♿ 8. Accessibility Checklist

- [ ] All interactive elements have focus states
- [ ] Color contrast ratio ≥ 4.5:1 (WCAG AA)
- [ ] All images have descriptive `alt` text
- [ ] Forms have proper `label` associations
- [ ] Error messages are descriptive (not just "required")
- [ ] Screen reader compatible (ARIA labels where needed)
- [ ] Keyboard navigation works on all interactive elements
- [ ] Font sizes not smaller than 14px
- [ ] Clickable areas ≥ 44x44px (mobile)
- [ ] No content relies solely on color to convey meaning

---

## 📱 9. Responsive Breakpoints

| Breakpoint | Width | Target Device |
|-----------|-------|---------------|
| `xs` | < 480px | Small phones |
| `sm` | 480–767px | Large phones |
| `md` | 768–1023px | Tablets |
| `lg` | 1024–1279px | Small laptops |
| `xl` | 1280–1535px | Desktops |
| `2xl` | ≥ 1536px | Large monitors |

### Responsive Rules
- Sidebar → Bottom nav on mobile
- Tables → Card list on mobile
- Multi-column grid → Single column on mobile
- Modal → Full screen on mobile
- Font sizes scale down by 2–4px on mobile

---

## 🔗 Related Documents

| Document | Link |
|----------|------|
| 📋 PRD | [00_PRD.md](./00_PRD.md) |
| 🔌 API | [03_API.md](./03_API.md) |
| ✅ Testing | [05_TESTING.md](./05_TESTING.md) |
| 🎨 Figma | [Insert Figma Link] |

# 🚀 Expert-Level UI/UX Remake Specification

> **Upgrade target:** production-grade UI/UX, motion system, React/JSX architecture, realtime/WebRTC UX, accessibility, responsive behavior, and implementation-ready standards.

The original foundation is retained: shadcn/ui + Tailwind CSS, the defined color system, Inter/JetBrains Mono typography, 4px spacing rhythm, responsive breakpoints, core component anatomy, user flows, accessibility checklist, and responsive rules.

The upgrade below adds the missing expert layer: intentional motion, GSAP orchestration, state-driven interaction, WebRTC-specific UX, performance constraints, component contracts, design QA, and engineering handoff.

## Expert Rule

**Do not add an effect unless it improves hierarchy, feedback, continuity, discoverability, or trust.**

**Do not implement a realtime feature without designing its permission, connection, degraded, recovery, and ended states.**

**Do not call a component complete until default, hover, focus, pressed, loading, disabled, error, success, responsive, and reduced-motion behavior have been considered.**

---

# 10. Premium UI Direction

Use quiet surfaces, strong type hierarchy, controlled contrast, intentional whitespace, and a small number of signature interactions. The interface should feel premium because its decisions are coherent, not because every section glows.

### Visual hierarchy
- Level 1: page purpose and primary action.
- Level 2: supporting context and key metrics.
- Level 3: secondary actions and detail.
- Level 4: diagnostics, advanced controls, and metadata.

### Visual restraint
- One dominant accent.
- One secondary accent.
- Semantic colors reserved for semantic meaning.
- Shadows used for layering.
- Blur used selectively.
- Motion used as feedback, not decoration.

---

# 11. Motion Architecture

Motion is divided into four layers: CSS microinteraction, GSAP component choreography, ScrollTrigger narrative motion, and realtime state animation. Each layer has an owner.

```text
CSS                 → tiny state changes
GSAP timeline       → coordinated component motion
ScrollTrigger       → scroll-linked storytelling
Realtime state      → connection / presence / media feedback
```

Never use a global animation script that reaches into unrelated components.

---

# 12. GSAP Installation

```bash
npm i gsap @gsap/react
```

```jsx
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useGSAP } from '@gsap/react';

gsap.registerPlugin(ScrollTrigger, useGSAP);
```

Use `useGSAP()` inside React components so selectors and cleanup remain scoped.

---

# 13. GSAP Component Contract

```jsx
const root = useRef(null);

useGSAP(() => {
  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
  tl.from('.eyebrow', { y: 12, opacity: 0, duration: 0.3 })
    .from('.title', { y: 40, opacity: 0, duration: 0.7 }, '-=0.1')
    .from('.copy', { y: 18, opacity: 0, duration: 0.45 }, '-=0.35')
    .from('.actions > *', { y: 10, opacity: 0, stagger: 0.06, duration: 0.3 }, '-=0.2');
}, { scope: root });
```

Rules: scope selectors, avoid layout properties, reuse timing tokens, kill observers on teardown, and respect reduced motion.

---

# 14. ScrollTrigger System

Scroll motion should be sparse and narrative.

```jsx
gsap.from('.reveal', {
  y: 32,
  opacity: 0,
  duration: 0.6,
  ease: 'power3.out',
  scrollTrigger: {
    trigger: '.reveal',
    start: 'top 86%',
    once: true,
  },
});
```

Use `scrub` for relationships, not applause. Use `pin` only for deliberate storytelling.

---

# 15. Reduced Motion

```jsx
const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (!reduce) {
  // non-essential animation
}
```

When reduced motion is active, preserve the state change but remove large travel, parallax, endless loops, and heavy choreography.

---

# 16. Motion Token Table

| Token | Value | Use |
|---|---:|---|
| fast | 160ms | press, icon |
| standard | 280ms | popover, menu |
| slow | 520ms | cards, sections |
| cinematic | 900ms | hero, narrative |
| enter | power3.out | entrance |
| exit | power2.in | removal |
| scrub | none | scroll relation |

---

# 17. JSX Architecture

```text
components/
  ui/
  navigation/
  feedback/
  motion/
  forms/
  realtime/
hooks/
  useReducedMotion.js
  useWebRTC.js
  useConnectionState.js
lib/
  motion.js
  realtime.js
styles/
  globals.css
  motion.css
```

A component is reusable only when its visual states and behavior are also reusable.

---

# 18. Component Contract

Every component specification must contain:

```text
Purpose
Anatomy
Props
Variants
States
Responsive behavior
Keyboard behavior
Motion behavior
Reduced-motion behavior
Loading behavior
Error behavior
```

---

# 19. Button Motion

Keep button feedback local and fast.

```css
button {
  transition: transform 160ms ease, box-shadow 160ms ease, background-color 160ms ease;
}

button:active {
  transform: scale(.985);
}
```

Arrow icons can translate 3–5px to communicate direction. Do not shift the whole button dramatically.

---

# 20. Interactive Card Motion

```css
.card {
  transition: transform 280ms cubic-bezier(.2,.8,.2,1), box-shadow 280ms ease;
}

.card:hover {
  transform: translateY(-2px);
}
```

For premium showcase cards, optional GSAP pointer tracking can create a subtle 3D response. Keep rotation tiny.

---

# 21. Magnetic CTA

```jsx
function MagneticCTA({ children }) {
  const ref = useRef(null);
  useGSAP(() => {
    const el = ref.current;
    const move = (e) => {
      const r = el.getBoundingClientRect();
      const x = e.clientX - r.left - r.width / 2;
      const y = e.clientY - r.top - r.height / 2;
      gsap.to(el, { x: x * .08, y: y * .08, duration: .28, ease: 'power2.out' });
    };
    const leave = () => gsap.to(el, { x: 0, y: 0, duration: .45, ease: 'power3.out' });
    el.addEventListener('pointermove', move);
    el.addEventListener('pointerleave', leave);
    return () => { el.removeEventListener('pointermove', move); el.removeEventListener('pointerleave', leave); };
  }, { scope: ref });
  return <button ref={ref}>{children}</button>;
}
```

Use only for pointer-capable devices and non-critical actions.

---

# 22. WebRTC UX Architecture

WebRTC is not an animation system. It is a realtime media layer whose invisible technical states must become clear human-facing UI states.

```text
IDLE
  ↓
PREFLIGHT
  ↓
PERMISSION
  ↓
CONNECTING
  ↓
CONNECTED
 ↙      ↘
RECONNECT  ENDED
 ↓
FAILED
```

---

# 23. WebRTC State Matrix

| State | UI | Action |
|---|---|---|
| idle | Ready to join | Join |
| preflight | Device preview | Test / Join |
| permission | Permission context | Allow / Retry |
| connecting | Progress | Wait |
| connected | Normal call | Controls |
| reconnecting | Calm degraded status | Wait / Retry |
| failed | Error explanation | Retry / Diagnostics |
| ended | Call summary | Rejoin / Exit |

---

# 24. WebRTC Preflight

```text
Join meeting

[ Camera preview ]

Camera      [ Integrated Camera ]
Microphone  [ USB Microphone ]

Mic level   ███████░░

[ Join now ]
```

Ask for permission in context. Preserve selected devices when safe. Never silently retry blocked permissions forever.

---

# 25. WebRTC Media Capture

```jsx
const stream = await navigator.mediaDevices.getUserMedia({
  audio: true,
  video: true,
});

stream.getTracks().forEach(track => track.stop());
```

Media lifecycle is part of UX. Starting, stopping, switching, and failing media must have visible state.

---

# 26. Screen Share

```jsx
const screen = await navigator.mediaDevices.getDisplayMedia({
  video: true,
  audio: false,
});
```

The interface must show which surface is currently shared and expose a clear stop action.

---

# 27. Connection Status Component

```jsx
function ConnectionStatus({ state }) {
  const label = {
    idle: 'Ready',
    checking: 'Checking connection',
    connecting: 'Connecting',
    connected: 'Connected',
    reconnecting: 'Reconnecting',
    failed: 'Connection problem',
    ended: 'Call ended',
  }[state] ?? 'Unknown';

  return <div role="status" aria-live="polite">{label}</div>;
}
```

Use text plus icon or shape. Never rely on color alone.

---

# 28. Participant Tile

```jsx
function ParticipantTile({ participant, speaking }) {
  return (
    <article className={speaking ? 'participant speaking' : 'participant'}>
      <video autoPlay playsInline muted={participant.isLocal} />
      <footer>
        <span>{participant.name}</span>
        <span>{participant.micEnabled ? 'Mic on' : 'Muted'}</span>
      </footer>
    </article>
  );
}
```

Stable participant identity matters more than animated rearrangement.

---

# 29. Call Controls

Recommended grouping:

```text
Mic | Camera | Share | Participants | More        Leave
```

Keep leave/end-call visually separated from routine controls. Use 44px+ hit areas where applicable.

---

# 30. Reconnect UX

Do not turn transient instability into a modal every time the network changes. Use a visible but calm status strip or badge.

```text
Connection is unstable
Reconnecting…
```

When recovery succeeds, replace the state quietly with normal connected status.

---

# 31. Realtime Motion

Good use:
- participant enters
- participant leaves
- speaker highlight
- connection recovery
- screen-share transition
- mic/camera icon state

Bad use:
- moving the entire call grid on every packet
- endless scaling of the active speaker
- flashing red status on transient loss

---

# 32. Audio Level Feedback

```jsx
function AudioMeter({ level }) {
  const p = Math.max(0, Math.min(1, level));
  return <div aria-label={`Microphone level ${Math.round(p * 100)} percent`}>
    <div style={{ transform: `scaleX(${p})`, transformOrigin: 'left' }} />
  </div>;
}
```

The meter should be readable but not become the dominant visual.

---

# 33. WebRTC Error Map

```text
Permission denied → explain recovery
Device busy       → suggest alternate device
No device         → explain missing hardware
Network failure   → retry / diagnostics
Browser issue     → browser-specific recovery
```

Raw exception strings belong in diagnostics, not the primary UI.

---

# 34. WebRTC Hook Skeleton

```jsx
export function useWebRTC() {
  const peer = useRef(null);
  const [connection, setConnection] = useState('idle');

  const connect = useCallback(() => {
    const pc = new RTCPeerConnection();
    peer.current = pc;
    pc.addEventListener('connectionstatechange', () => {
      setConnection(pc.connectionState);
    });
  }, []);

  const disconnect = useCallback(() => {
    peer.current?.close();
    peer.current = null;
    setConnection('ended');
  }, []);

  return { connection, connect, disconnect };
}
```

A complete production call still needs signaling, ICE/TURN configuration, track lifecycle, permissions, retries, and browser testing.

---

# 35. Responsive Design Enforcement

The original breakpoints remain the reference: xs <480, sm 480–767, md 768–1023, lg 1024–1279, xl 1280–1535, 2xl ≥1536.

Responsive work must alter grouping, controls, density, and navigation where needed, not just reduce width.

---

# 36. Responsive Component Matrix

| Component | Mobile | Tablet | Desktop |
|---|---|---|---|
| Sidebar | bottom nav / sheet | compact | full |
| Modal | full screen | centered | centered |
| Table | cards | compact table | full table |
| Grid | 1 col | 2 col | 3–4 col |
| Call controls | bottom dock | bottom dock | dock / float |

---

# 37. Mobile UX Rules

Critical actions stay reachable.

Hover is never required.

Fixed controls respect safe areas.

Long labels may wrap.

Dense utilities move into sheets or menus.

---

# 38. Dark Mode

Use semantic tokens, not duplicated hardcoded palettes.

```css
[data-theme='dark'] {
  --bg: #0f172a;
  --surface: #1e293b;
  --border: #334155;
  --text: #f1f5f9;
  --muted: #94a3b8;
}
```

Audit focus, chart, overlay, video, shadow, and glow states separately.

---

# 39. Accessibility Upgrade

The source guide already calls for visible focus, contrast, descriptive alt text, correct labels, descriptive errors, keyboard navigation, adequate touch targets, and non-color-only meaning. The upgraded implementation must treat those as component-level contracts, not end-of-project checks.

---

# 40. Focus Management

```css
:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 3px;
}
```

Dialogs return focus to their trigger. Dynamic lists preserve logical focus. Keyboard order follows interaction order.

---

# 41. Semantic HTML

Prefer native controls and landmarks.

```html
<header>
<nav>
<main>
<section>
<aside>
<footer>
```

Use buttons for actions and links for navigation.

---

# 42. Form Accessibility

```jsx
<label htmlFor="email">Email</label>
<input id="email" name="email" type="email" aria-describedby="email-help email-error" />
<p id="email-help">Use the email connected to your account.</p>
<p id="email-error" role="alert">Enter a valid email address.</p>
```

Error text should explain what is wrong and what to do.

---

# 43. Loading Architecture

Every async component should choose the correct loading pattern:

```text
known structure → skeleton
known progress  → progress bar
short unknown    → spinner
optimistic safe  → immediate state + rollback
```

Do not show a full-page spinner for a small local request.

---

# 44. Skeleton Geometry

Skeleton dimensions should approximate the final layout. This reduces visual movement and preserves scanning.

```css
.skeleton {
  border-radius: 8px;
  background: color-mix(in srgb, currentColor 8%, transparent);
}
```

---

# 45. Error Architecture

```text
Field error       → local
Section error     → section fallback
Request failure   → contextual banner / toast
Fatal UI error    → recovery page
Realtime failure  → connection state + recovery
```

---

# 46. Empty State Architecture

Every empty state contains: context, explanation, first action, and optional next-best action.

```text
Nothing here yet
Create your first project to get started.
[Create project]
```

---

# 47. Success State Architecture

Confirm the outcome and provide the next useful action.

```text
Project created
Your workspace is ready.
[Open project]
```

Do not celebrate longer than the user needs to understand what happened.

---

# 48. Toast Rules

Use local feedback before global feedback when possible.

Do not create repeated toasts for repeated background events.

Critical information belongs in persistent UI, not a disappearing toast.

---

# 49. Modal Rules

Use dialogs for short, focused interruption.

Use sheets for contextual side tasks.

On mobile, full-screen sheets are often easier to scan and operate.

Animation is secondary to focus management.

---

# 50. Drawer Animation

```js
gsap.fromTo(panelRef.current,
  { x: 24, opacity: 0 },
  { x: 0, opacity: 1, duration: .28, ease: 'power3.out' }
);
```

The main task should remain visually anchored.

---

# 51. Navigation Motion

Page transitions should preserve orientation. Avoid cinematic full-screen wipes for ordinary task navigation.

Use a subtle content reveal after route change.

---

# 52. Hero Motion

Hero choreography order:

```text
atmosphere → eyebrow → headline → copy → CTA → product visual
```

Do not reveal the CTA before the user knows what the CTA means.

---

# 53. Scroll Storytelling

Use pinned narratives for product walkthroughs, visual decomposition, or stepwise explanations. Avoid pinning long forms and dense tables.

---

# 54. Parallax

Keep parallax subtle.

```js
gsap.to(layer, {
  yPercent: -10,
  ease: 'none',
  scrollTrigger: { trigger: section, start: 'top bottom', end: 'bottom top', scrub: true }
});
```

Disable or simplify it for reduced-motion users.

---

# 55. 3D Hover

Use tiny rotation and local lighting only on showcase cards.

```js
gsap.to(card, { rotateX, rotateY, duration: .3, ease: 'power2.out' });
```

If the effect makes reading harder, remove it.

---

# 56. SVG Motion

Good candidates:
- icon morph
- progress path
- network diagram
- visual state machine

Use SVG for geometry, not as an excuse to animate everything.

---

# 57. Canvas Motion

Canvas is justified for waveforms, particles, or dense visualizations where DOM rendering becomes inefficient. Always provide accessible text when canvas carries essential information.

---

# 58. AI Interface Motion

For streaming AI, show received, processing, generating, complete, stopped, and failed states. Avoid fake typing when actual streaming is already visible.

---

# 59. Realtime Voice UX

```text
Idle → Listening → Thinking → Speaking → Idle
                       ↘ Interrupted
                       ↘ Error
```

The visual indicator and accessible status must tell the same story.

---

# 60. Presence UX

Presence can use avatar, name, status, and current activity. Color is supplemental.

```text
Nishant · Online
```

---

# 61. Live Data Motion

Animate the changed value, not the whole dashboard.

```css
.value-updated {
  animation: value-update 700ms ease;
}
@keyframes value-update {
  from { opacity: .65; transform: translateY(2px); }
  to { opacity: 1; transform: translateY(0); }
}
```

---

# 62. Layout Shift Prevention

Reserve image space.
Reserve skeleton space.
Keep button widths stable during loading.
Do not inject toolbars above the current scroll position without intent.

---

# 63. Performance Rules

Animate transforms and opacity first.

Avoid large filter stacks.

Pause hidden loops.

Lazy-load heavy media.

Destroy GSAP contexts.

Stop WebRTC tracks on teardown.

---

# 64. React Performance

Avoid unstable keys, unnecessary context updates, repeated event attachment, and animation setup during render. Memoize only when it prevents real work.

---

# 65. WebRTC Performance

Stable participant keys, localized state updates, sensible media constraints, explicit cleanup, and graceful degradation are mandatory.

---

# 66. Realtime Grid Rules

Do not rerender all tiles for a single mic-state change.

Do not reorder the entire grid unless participant priority genuinely changed.

Use stable layout slots.

---

# 67. FLIP Motion

Use FLIP for reordering when spatial continuity matters.

```text
First → Last → Invert → Play
```

It is appropriate for sortable cards, dashboard rearrangement, and participant grids.

---

# 68. Gesture Rules

Gestures are optional enhancements. Essential actions remain available through buttons and keyboard equivalents where relevant.

---

# 69. Safe Areas

```css
.bottom-dock {
  padding-bottom: max(12px, env(safe-area-inset-bottom));
}
```

Critical mobile controls must not be hidden behind system UI.

---

# 70. Mobile Call Layout

```text
Main speaker
────────────────
P1 | P2 | P3 | +n
────────────────
Mic Camera Share More Leave
```

The primary speaker stays visually dominant.

---

# 71. Desktop Call Layout

```text
┌──────────────┬──────────────┐
│ Participant 1│ Participant 2│
├──────────────┼──────────────┤
│ Participant 3│ Shared screen │
└──────────────┴──────────────┘
             Controls
```

---

# 72. Realtime Side Panel

Chat, participant list, and diagnostics can open in a side panel without destroying the primary call context.

---

# 73. Diagnostics Drawer

For expert tools, expose connection facts separately from the consumer-facing state.

```text
Connection  Connected
RTT         112 ms
Packet loss 0.4%
Device      USB Mic
```

---

# 74. Connection State Copy

Use: `Connecting…`, `Reconnecting…`, `Connection is unstable`, `Microphone blocked`, `Camera unavailable`.

Avoid raw protocol language in the primary UI.

---

# 75. Permission UX

Explain what is requested, why, and how to recover if the browser blocks it.

---

# 76. Device Switch UX

Switching should preserve call context, acknowledge the change, and fall back gracefully when a device disappears.

---

# 77. Screen Share Stop UX

Stop sharing must be obvious and local. Never bury it three menus deep.

---

# 78. Participant Join Motion

```text
opacity: 0 → 1
scale: .985 → 1
y: 12px → 0
```

Keep it under normal interaction latency and disable it for reduced motion.

---

# 79. Participant Leave Motion

```text
opacity: 1 → 0
scale: 1 → .985
```

Use a short exit and immediately reclaim layout space when it improves responsiveness.

---

# 80. Speaker Highlight

Use a restrained ring, border, or local glow. Do not continuously scale the speaker tile with voice level.

---

# 81. Video Fallback

```text
[Avatar]
Name
Camera off
```

Identity and state remain visible even when media is unavailable.

---

# 82. Audio-Only Tile

An audio-only participant should not look disconnected. Use an identity-centric composition instead of an empty black box.

---

# 83. Network Quality

A network icon can summarize quality. Use precise numbers only when the system actually calculates them.

---

# 84. Call End State

```text
Call ended
Duration: 28 min
Participants: 5

[Rejoin] [Back to workspace]
```

---

# 85. Error Recovery

Every user-visible failure should answer: what happened, what is affected, and what can I do next?

---

# 86. Undo Pattern

For reversible actions, prefer low-friction undo over unnecessary confirmation dialogs.

```text
Archived project                         Undo
```

---

# 87. Destructive Actions

Use stronger contrast, explicit labels, and context. Avoid vague `Are you sure?` prompts.

---

# 88. Unsaved Changes

Use local status first. Intercept navigation only when meaningful work can actually be lost.

---

# 89. Autosave

```text
Saving…
Saved just now
Offline
Sync required
```

Trust is communicated through status clarity.

---

# 90. Search UX

Search should distinguish recent queries, suggestions, results, filters, loading, and no-results states.

---

# 91. Command Palette

Use a command palette for power users. Provide keyboard hints and predictable grouping.

```text
⌘/Ctrl K  Open command palette
Esc       Close overlay
```

---

# 92. Tooltips

Tooltips explain. They do not hide core actions.

---

# 93. Tabs

Tabs switch between sibling views. Animate the active indicator rather than the whole page by default.

---

# 94. Filters

Applied filters remain visible. Complex filters become a sheet on mobile.

---

# 95. Tables

Desktop tables optimize comparison. Mobile often needs card-based transformation instead of tiny columns.

---

# 96. Large Data Sets

Virtualization is useful at scale, but it adds complexity. Use it when rendering cost actually warrants it.

---

# 97. Content Resilience

Test long names, long labels, empty arrays, zero values, large numbers, missing images, and slow responses.

---

# 98. Localization

Do not hardcode widths around English text. Labels should be able to grow. Prefer logical CSS properties for future RTL support.

---

# 99. Semantic State Names

```js
connection === 'reconnecting'
```

Prefer semantic state names over presentation state names such as `isYellow`.

---

# 100. Z-Index Tokens

```css
:root {
  --z-base: 0;
  --z-header: 30;
  --z-popover: 50;
  --z-drawer: 60;
  --z-modal: 70;
  --z-toast: 80;
  --z-tooltip: 90;
}
```

Avoid random `z-[9999]` values.

---

# 101. Glass Surfaces

Glass is appropriate for select floating controls. It is not a default card style. Provide a solid fallback.

---

# 102. Glow System

Keep glow low-contrast. It should reinforce a focal region without degrading text contrast.

---

# 103. Gradient Mesh

```css
.ambient {
  background:
    radial-gradient(circle at 15% 20%, rgba(14,165,233,.14), transparent 35%),
    radial-gradient(circle at 85% 80%, rgba(139,92,246,.12), transparent 35%);
}
```

Use gradients as atmosphere, not as information.

---

# 104. Design-to-Code Mapping

```text
Button              → Button
Connection badge    → ConnectionStatus
Call controls       → CallControls
Participant card    → ParticipantTile
Motion wrapper      → AnimatedSection
Side panel          → Sheet / Drawer
Modal               → Dialog
```

---

# 105. Variant Strategy

Use variants before duplication. A component should become a new component only when its behavior or semantic contract is genuinely different.

---

# 106. Motion Ownership

The component that owns the interaction should own the animation lifecycle. Global helpers should provide presets, not page-specific selectors.

---

# 107. Motion Utility

```js
export const MOTION = {
  fast: { duration: .16, ease: 'power2.out' },
  standard: { duration: .28, ease: 'power3.out' },
  slow: { duration: .52, ease: 'power3.out' },
  cinematic: { duration: .9, ease: 'expo.out' },
};
```

---

# 108. Animated Section Utility

```jsx
export function AnimatedSection({ children }) {
  const ref = useRef(null);
  const reduce = useReducedMotion();
  useGSAP(() => {
    if (reduce) return;
    gsap.from(ref.current, { y: 28, opacity: 0, duration: .58, ease: 'power3.out', scrollTrigger: { trigger: ref.current, start: 'top 88%', once: true } });
  }, { scope: ref, dependencies: [reduce] });
  return <section ref={ref}>{children}</section>;
}
```

---

# 109. Loading Button

```jsx
<Button disabled={pending} aria-busy={pending}>
  {pending ? <> <Loader2 className="animate-spin" /> Saving… </> : 'Save changes'}
</Button>
```

Keep dimensions stable while loading.

---

# 110. Animated Number

Count-up animation is acceptable for meaningful metrics. It should not suggest continuous live change when values update discretely.

---

# 111. Live Data Highlight

Use a short local highlight when a value changes. Avoid flashing the entire dashboard.

---

# 112. Route Transition

```jsx
gsap.fromTo(mainRef.current,
  { y: 10, opacity: 0 },
  { y: 0, opacity: 1, duration: .34, ease: 'power2.out' }
);
```

Navigation must not be blocked by the transition.

---

# 113. Focus Return

```jsx
const previous = document.activeElement;
triggerCloseButton.focus();
return () => previous?.focus?.();
```

Use established dialog primitives for full focus trapping.

---

# 114. Error Boundary

Provide a recovery action and avoid exposing a blank screen. Diagnostics belong behind an explicit detail path.

---

# 115. API Error Mapping

Map backend errors into human categories rather than rendering raw server payloads.

---

# 116. Retry UX

Retry should preserve the user's intent and form content wherever recovery is safe.

---

# 117. Async Race Safety

When newer requests supersede older ones, stale responses must not overwrite current UI state.

---

# 118. Interaction Interruption

Animations can be interrupted. User state wins over animation completion.

---

# 119. Animation Cleanup

```jsx
useGSAP(() => {
  // animations
  return () => {
    // custom listeners if any
  };
}, { scope: root });
```

Use context cleanup and remove custom listeners.

---

# 120. Event Listener Discipline

Never attach pointer, resize, scroll, or media listeners repeatedly on every render.

---

# 121. Scroll Refresh

Async images, expanded panels, and dynamic data can change layout. Scroll-based animation should be refreshed or designed to tolerate content changes.

---

# 122. Image Stability

```css
.media-frame {
  aspect-ratio: 16 / 9;
  overflow: hidden;
}
```

Reserve media space before loading.

---

# 123. Video Stability

Use stable aspect ratios for participant tiles so joining/leaving does not create chaotic layout shifts.

---

# 124. Performance Tiers

```text
Tier A → CSS transform / opacity
Tier B → GSAP / SVG / modest blur
Tier C → canvas / particle system / complex realtime visualization
```

Tier C effects require explicit product value and profiling.

---

# 125. Particle System

Particles are decorative. Bound the count, pause when hidden, and simplify for reduced motion.

---

# 126. Video Background

Background video should not compete with content, should have a stable poster state, and should respect reduced-motion preferences.

---

# 127. Audio Visualizer

Use waveforms and meters to communicate audio state. Do not turn every voice input into a dramatic equalizer.

---

# 128. Form Motion

Use subtle focus, validation, and completion motion. Never make an invalid field shake for an extended duration.

---

# 129. Wizard Motion

Animate the changing step region, preserve the shared shell, and communicate forward/back direction only when it helps orientation.

---

# 130. Progress UX

Use determinate progress only when the system can provide meaningful progress. Never invent fake percentages.

---

# 131. Upload UX

```text
Selecting → Validating → Uploading → Processing → Complete
                                      ↘ Failed
```

Keep the file context visible throughout.

---

# 132. Drag and Drop

Drop zones activate when a drag is present. Provide a keyboard-accessible file picker as the primary fallback.

---

# 133. Undo vs Confirmation

Use undo for reversible actions. Use confirmation for irreversible or high-impact actions.

---

# 134. Notification Hierarchy

```text
Critical → persistent / interrupt
High     → prominent
Normal   → toast / inbox
Low      → quiet inbox
```

---

# 135. Session Expiry

```text
Your session expired

Sign in again to continue.

[Sign in]
```

Preserve safe context when practical.

---

# 136. Auth UI

Authentication should be calm, focused, and predictable. Avoid decorative motion that competes with the credential task.

---

# 137. OTP UX

Support paste, clear focus progression, resend timing, and recoverable errors.

---

# 138. Password UX

Provide visibility toggle and meaningful requirements. Avoid arbitrary complexity requirements without a security reason.

---

# 139. Onboarding

The first meaningful task should arrive before a long tour. Contextual education is preferred over mandatory walkthroughs.

---

# 140. Command Search

Keyboard shortcuts are discoverability features. Display them in the command palette and shortcut reference.

---

# 141. Localization Ready Components

Buttons, tabs, nav items, badges, and errors must tolerate longer strings. Never design around a single screenshot length.

---

# 142. RTL Ready CSS

Prefer `margin-inline`, `padding-inline`, `inset-inline`, and logical border properties where practical.

---

# 143. Design QA

```text
Structure → Visual → Interaction → Motion → Responsive → Accessibility → Performance → Realtime
```

---

# 144. QA: Visual

Check alignment, rhythm, typography, contrast, density, hierarchy, borders, radii, and elevation.

---

# 145. QA: Interaction

Check hover, focus, press, disabled, loading, validation, error, success, and cancellation.

---

# 146. QA: Motion

Check timing, easing, interruption, cleanup, reduced motion, and whether animation communicates anything useful.

---

# 147. QA: Responsive

Check 390px, 768px, 1280px, and 1536px as explicit review widths in addition to project-supported sizes.

---

# 148. QA: WebRTC

Check permissions, no-device, device switching, join, leave, reconnect, failed connection, backgrounding, screen share, and audio-only fallback.

---

# 149. QA: Accessibility

```text
Keyboard only
Focus visible
Dialog focus
Labels
Error association
Contrast
Reduced motion
Touch target
Screen reader landmark spot-check
```

---

# 150. QA: Performance

```text
No layout jank
No animation leaks
No stale event listeners
No unnecessary rerenders
No media track leaks
No expensive effects without profiling
```

---

# 151. Figma Handoff

Figma should mirror engineering concepts: named components, variants, variables, Auto Layout, responsive notes, and motion annotations.

---

# 152. Figma Variable Map

```text
Color / Brand / Surface / Text / Status
Spacing / 1 / 2 / 3 / 4 / 6 / 8 / 12 / 16
Radius / sm / md / lg / xl / full
Motion / duration / easing / distance
```

---

# 153. Design-to-Dev Handoff Checklist

```text
[ ] tokens mapped
[ ] components named
[ ] variants named
[ ] states documented
[ ] motion documented
[ ] responsive documented
[ ] accessibility documented
[ ] realtime states documented
[ ] error paths documented
```

---

# 154. Design Debt

Every one-off color, spacing hack, animation, and duplicated component should be visible as debt.

---

# 155. Component Duplication Test

Before creating a component, ask: is the behavior different, is the semantic role different, or is this just a variant?

---

# 156. Content Hierarchy Audit

If every heading is heavy, every card has an icon, and every section has a gradient, hierarchy has collapsed.

---

# 157. Visual Silence

Whitespace is a tool. Keep empty areas intentional and use them to frame high-priority content.

---

# 158. Density Tuning

Marketing pages can breathe. Operational dashboards should support scanning. Do not force the same density across every route.

---

# 159. Expert Mode

Expert users may benefit from command shortcuts, diagnostics, compact density, and advanced controls. These belong behind progressive disclosure when the audience is mixed.

---

# 160. Trust UX

Saving, syncing, connection, processing, and permission states should always be explicit enough that the user does not need to guess whether the system acted.

---

# 161. Final Quality Bar

The output is not complete when all screens exist. It is complete when the states between screens are designed too.

```text
Visual system ✓
Component system ✓
Motion system ✓
Responsive system ✓
Accessibility ✓
Loading / error / success ✓
Realtime / WebRTC states ✓ where applicable
Performance ✓
QA ✓
Engineering handoff ✓
```

---

# 162. AI Coding Agent Prompt

```text
Build the interface from this specification as a production-grade React/Next.js system.

Use shadcn/ui + Tailwind for primitives. Use semantic tokens.
Use GSAP for coordinated motion and ScrollTrigger for intentional scroll narratives.
Use CSS for simple state transitions.
Scope and clean every animation.
Respect prefers-reduced-motion.

Every async task must have loading, success, error, and recovery states.
Every realtime feature must expose permission, connecting, connected, reconnecting, failed, and ended states.

Do not produce generic rounded-card dashboards.
Do not invent decorative motion that adds no UX value.
Do not rely on color alone.
Do not hide core actions behind hover-only behavior.

Treat mobile as a first-class composition.
Test long labels, slow data, empty data, device failure, network loss, and rapid user interaction.

Before finishing, perform a visual, interaction, accessibility, responsive, motion, performance, and realtime audit.
```

---

# 163. Reviewer Prompt

```text
Audit the implementation against this design specification.
Find the weakest parts first.
Check hierarchy, spacing, typography, component reuse, responsive composition, accessibility, motion restraint, GSAP cleanup, layout stability, loading/error/success states, and WebRTC recovery UX.
Return specific defects and code-level fixes.
Do not judge by screenshot beauty alone.
```

---

# 164. Release Definition

```text
Light mode      ✓
Dark mode       ✓
Mobile          ✓
Tablet          ✓
Desktop         ✓
Keyboard        ✓
Reduced motion  ✓
Loading         ✓
Errors          ✓
Success         ✓
Realtime        ✓ when applicable
Performance     ✓
QA              ✓
```

---

# 165. Final Design Principle

**The interface should not try to prove that it is sophisticated. Its sophistication should be visible in the quality of its decisions.**

---

## 167. Navigation Expert State Matrix

| State / Concern | Required behavior |
|---|---|
| active state | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| collapsed state | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| mobile state | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| keyboard order | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| route continuity | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |

### Navigation review questions
- What is the user trying to accomplish at the navigation level?
- What happens if the action is interrupted halfway?
- What happens when the network is slow or unavailable?
- What happens when the content is longer or missing?
- What changes on mobile, keyboard, touch, and reduced motion?

## 168. Buttons Expert State Matrix

| State / Concern | Required behavior |
|---|---|
| default | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| hover | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| focus | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| pressed | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| loading | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| disabled | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| destructive | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| icon-only | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |

### Buttons review questions
- What is the user trying to accomplish at the buttons level?
- What happens if the action is interrupted halfway?
- What happens when the network is slow or unavailable?
- What happens when the content is longer or missing?
- What changes on mobile, keyboard, touch, and reduced motion?

## 169. Forms Expert State Matrix

| State / Concern | Required behavior |
|---|---|
| empty | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| focus | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| filled | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| validation | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| error | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| success | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| disabled | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| loading | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |

### Forms review questions
- What is the user trying to accomplish at the forms level?
- What happens if the action is interrupted halfway?
- What happens when the network is slow or unavailable?
- What happens when the content is longer or missing?
- What changes on mobile, keyboard, touch, and reduced motion?

## 170. Cards Expert State Matrix

| State / Concern | Required behavior |
|---|---|
| static | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| interactive | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| selected | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| disabled | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| loading | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| error | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| responsive | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| hover | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |

### Cards review questions
- What is the user trying to accomplish at the cards level?
- What happens if the action is interrupted halfway?
- What happens when the network is slow or unavailable?
- What happens when the content is longer or missing?
- What changes on mobile, keyboard, touch, and reduced motion?

## 171. Dialogs Expert State Matrix

| State / Concern | Required behavior |
|---|---|
| open | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| close | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| focus trap | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| focus return | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| scroll | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| escape | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| mobile | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| reduced motion | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |

### Dialogs review questions
- What is the user trying to accomplish at the dialogs level?
- What happens if the action is interrupted halfway?
- What happens when the network is slow or unavailable?
- What happens when the content is longer or missing?
- What changes on mobile, keyboard, touch, and reduced motion?

## 172. Toasts Expert State Matrix

| State / Concern | Required behavior |
|---|---|
| success | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| error | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| info | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| undo | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| dedupe | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| queue | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| dismiss | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| accessibility | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |

### Toasts review questions
- What is the user trying to accomplish at the toasts level?
- What happens if the action is interrupted halfway?
- What happens when the network is slow or unavailable?
- What happens when the content is longer or missing?
- What changes on mobile, keyboard, touch, and reduced motion?

## 173. Search Expert State Matrix

| State / Concern | Required behavior |
|---|---|
| idle | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| typing | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| loading | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| results | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| no results | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| keyboard | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| filters | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| mobile | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |

### Search review questions
- What is the user trying to accomplish at the search level?
- What happens if the action is interrupted halfway?
- What happens when the network is slow or unavailable?
- What happens when the content is longer or missing?
- What changes on mobile, keyboard, touch, and reduced motion?

## 174. Tables Expert State Matrix

| State / Concern | Required behavior |
|---|---|
| sort | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| filter | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| pagination | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| empty | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| loading | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| error | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| responsive | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| selection | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |

### Tables review questions
- What is the user trying to accomplish at the tables level?
- What happens if the action is interrupted halfway?
- What happens when the network is slow or unavailable?
- What happens when the content is longer or missing?
- What changes on mobile, keyboard, touch, and reduced motion?

## 175. Uploads Expert State Matrix

| State / Concern | Required behavior |
|---|---|
| select | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| validate | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| upload | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| progress | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| processing | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| success | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| fail | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| cancel | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |

### Uploads review questions
- What is the user trying to accomplish at the uploads level?
- What happens if the action is interrupted halfway?
- What happens when the network is slow or unavailable?
- What happens when the content is longer or missing?
- What changes on mobile, keyboard, touch, and reduced motion?

## 176. WebRTC Expert State Matrix

| State / Concern | Required behavior |
|---|---|
| preflight | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| permission | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| connecting | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| connected | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| reconnecting | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| failed | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| ended | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| device switch | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |

### WebRTC review questions
- What is the user trying to accomplish at the webrtc level?
- What happens if the action is interrupted halfway?
- What happens when the network is slow or unavailable?
- What happens when the content is longer or missing?
- What changes on mobile, keyboard, touch, and reduced motion?

## 177. Realtime Media Expert State Matrix

| State / Concern | Required behavior |
|---|---|
| mic | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| camera | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| screen share | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| audio-only | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| speaker | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| quality | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| fallback | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| cleanup | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |

### Realtime Media review questions
- What is the user trying to accomplish at the realtime media level?
- What happens if the action is interrupted halfway?
- What happens when the network is slow or unavailable?
- What happens when the content is longer or missing?
- What changes on mobile, keyboard, touch, and reduced motion?

## 178. Animation Expert State Matrix

| State / Concern | Required behavior |
|---|---|
| enter | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| active | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| exit | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| interrupt | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| cleanup | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| reduced motion | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| scroll | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| hover | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |

### Animation review questions
- What is the user trying to accomplish at the animation level?
- What happens if the action is interrupted halfway?
- What happens when the network is slow or unavailable?
- What happens when the content is longer or missing?
- What changes on mobile, keyboard, touch, and reduced motion?

## 179. Responsive Expert State Matrix

| State / Concern | Required behavior |
|---|---|
| 390px | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| 480px | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| 768px | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| 1024px | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| 1280px | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| 1536px | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| landscape | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| safe area | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |

### Responsive review questions
- What is the user trying to accomplish at the responsive level?
- What happens if the action is interrupted halfway?
- What happens when the network is slow or unavailable?
- What happens when the content is longer or missing?
- What changes on mobile, keyboard, touch, and reduced motion?

## 180. Accessibility Expert State Matrix

| State / Concern | Required behavior |
|---|---|
| focus | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| labels | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| contrast | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| keyboard | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| screen reader | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| touch target | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| live region | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| reduced motion | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |

### Accessibility review questions
- What is the user trying to accomplish at the accessibility level?
- What happens if the action is interrupted halfway?
- What happens when the network is slow or unavailable?
- What happens when the content is longer or missing?
- What changes on mobile, keyboard, touch, and reduced motion?

## 181. Performance Expert State Matrix

| State / Concern | Required behavior |
|---|---|
| layout shift | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| render cost | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| memory | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| event listeners | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| media | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| animation | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| network | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |
| lazy load | Define visual state, interaction rule, feedback, accessibility, and responsive behavior. |

### Performance review questions
- What is the user trying to accomplish at the performance level?
- What happens if the action is interrupted halfway?
- What happens when the network is slow or unavailable?
- What happens when the content is longer or missing?
- What changes on mobile, keyboard, touch, and reduced motion?

### Implementation Rule 1
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 2
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 3
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 4
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 5
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 6
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 7
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 8
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 9
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 10
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 11
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 12
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 13
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 14
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 15
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 16
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 17
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 18
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 19
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 20
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 21
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 22
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 23
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 24
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 25
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 26
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 27
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 28
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 29
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 30
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 31
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 32
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 33
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 34
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 35
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 36
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 37
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 38
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 39
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 40
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 41
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 42
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 43
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 44
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 45
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 46
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 47
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 48
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 49
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 50
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 51
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 52
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 53
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 54
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 55
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 56
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 57
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 58
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 59
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 60
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 61
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 62
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 63
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 64
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 65
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 66
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 67
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 68
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 69
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 70
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 71
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 72
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 73
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 74
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 75
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 76
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 77
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 78
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 79
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 80
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 81
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 82
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 83
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 84
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 85
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 86
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 87
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 88
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 89
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 90
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 91
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 92
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 93
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 94
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 95
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 96
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 97
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 98
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 99
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 100
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 101
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 102
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 103
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 104
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 105
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 106
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 107
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 108
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 109
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 110
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 111
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 112
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 113
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 114
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 115
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 116
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 117
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 118
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 119
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 120
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 121
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 122
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 123
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 124
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 125
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 126
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 127
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 128
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 129
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 130
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 131
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 132
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 133
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 134
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 135
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 136
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 137
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 138
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 139
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 140
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 141
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 142
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 143
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 144
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.

### Implementation Rule 145
Prefer semantic tokens over raw visual values. Keep the code aligned with the design system.

### Implementation Rule 146
Animation must preserve function if it is disabled. The end state must remain usable and understandable.

### Implementation Rule 147
Treat loading, error, success, empty, disabled, and degraded states as first-class UI, not edge cases.

### Implementation Rule 148
When realtime behavior exists, communicate invisible system state with concise, stable status language.

### Implementation Rule 149
Use responsive composition, not just responsive dimensions. Re-group information when screen constraints change.

### Implementation Rule 150
Before shipping, test the interaction at realistic content lengths and on real touch hardware where relevant.


# 340. Related Documents

| Document | Link |
|---|---|
| 📋 PRD | [00_PRD.md](./00_PRD.md) |
| 🔌 API | [03_API.md](./03_API.md) |
| ✅ Testing | [05_TESTING.md](./05_TESTING.md) |
| 🎨 Figma | [Insert Figma Link] |
| 🧩 Components | [COMPONENTS.md](./COMPONENTS.md) |
| 🎬 Motion | [MOTION.md](./MOTION.md) |
| 📡 WebRTC | [WEBRTC.md](./WEBRTC.md) |

# End

Build less noise, more hierarchy, clearer state, better feedback, and motion with intent.
