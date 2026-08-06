# Design — Smart-Spam-Detector: Design System & UX Principles

| Field | Value |
|---|---|
| Version | v0.1 |
| Last Updated | 2026-08-06 |
| Owner | Lead Designer |
| Status | In Review |

---

## 1. Design Principles

1. **Clarity over cleverness** — verdicts must be instantly legible (green = ham, red = spam). *Do:* big label + score. *Don't:* nested menus to reveal the result.
2. **Explainability first** — always show *why* (top tokens). *Do:* token chips. *Don't:* bare probability number.
3. **Calm defaults** — neutral palette so red/green remain meaningful. *Do:* gray chrome. *Don't:* rainbow accents.
4. **Zero-input friction** — paste → classify in one action. *Do:* single textarea + button. *Don't:* multi-step wizards.
5. **Honest failure** — errors state what broke in plain language. *Do:* "Could not reach API — retry". *Don't:* stack traces.

## 2. Brand & Visual Identity

- **Tone of voice:** direct, technical, trustworthy. No jargon without explanation.
- **Imagery:** minimal; icons for verdicts (shield/alert), no stock photography.
- **Logo:** shield motif with check/cross; safe-area padding ≥ 8px.

## 3. Color System

| Token | Hex | Usage | Contrast vs bg |
|---|---|---|---|
| bg-canvas | #F7F8FA | App background | — |
| bg-surface | #FFFFFF | Cards, inputs | — |
| text-primary | #1A1D21 | Body text | ≥ 7:1 |
| text-muted | #5C6670 | Secondary text | ≥ 4.5:1 |
| brand-accent | #2F5CFF | Primary button, links | ≥ 4.5:1 |
| success | #157F4B | Ham / safe verdict | ≥ 4.5:1 |
| danger | #C02A2A | Spam / error verdict | ≥ 4.5:1 |
| warning | #B45309 | Uncertain verdict | ≥ 4.5:1 |
| border | #DDE1E6 | Dividers, outlines | N/A |

## 4. Typography Scale

| Token | Font | Size | Weight | Line-height | Usage |
|---|---|---|---|---|---|
| display | Inter | 32px | 700 | 1.2 | Verdict headline |
| title | Inter | 20px | 600 | 1.3 | Screen titles |
| body | Inter | 16px | 400 | 1.5 | Copy, inputs |
| caption | Inter | 13px | 400 | 1.4 | Help text, tokens |
| mono | JetBrains Mono | 14px | 400 | 1.5 | Message preview |

## 5. Spacing & Grid System

- Base unit: 4px. Scale: 4 / 8 / 12 / 16 / 24 / 32 / 48.
- Content max-width: 720px (single-column classify focus).
- Breakpoints: mobile < 640px; tablet 640–1024px; desktop > 1024px.

## 6. Component Library

### 6.1 Verdict Badge

| State | Style |
|---|---|
| Default (ham) | Green pill: "HAM — 97% confident" |
| Spam | Red pill: "SPAM — 99% confident" |
| Uncertain | Amber pill: "UNCERTAIN — 54% confident" |

```
┌───────────────────────────────┐
│  [SPAM] 99% confident   [copy]│
│  top tokens:  prize  win  free │
└───────────────────────────────┘
```

### 6.2 Buttons

| State | Style |
|---|---|
| Default | Accent bg, white text, 8px radius |
| Hover | Darken 6% |
| Active | Scale 0.98 |
| Disabled | 40% opacity, no pointer |
| Loading | Spinner replaces label |

### 6.3 Inputs (textarea)

| State | Style |
|---|---|
| Default | 1px border, white bg |
| Focus | 2px accent border |
| Error | 1.5px danger border + message |

### 6.4 Toast

- Success: green left border, icon check.
- Error: red left border, icon alert.
- Auto-dismiss 5s; respects reduced-motion.

## 7. Iconography & Imagery

- Source: Feather/Lucide-style 24px stroke icons.
- Sizes: 16/20/24/32px only.
- Verdicts: check-circle (ham), alert-triangle (spam), help-circle (uncertain).

## 8. Accessibility Standards

- Target: WCAG 2.1 AA.
- Keyboard: full tab order; Enter submits form; Esc clears.
- Screen readers: verdicts announced with aria-live="polite".
- Motion: all animations ≤ 200 ms; `prefers-reduced-motion` disables transitions.

## 9. Responsive Behavior

| Breakpoint | Layout |
|---|---|
| < 640px | Single column; verdict badge full-width |
| 640–1024px | Two columns (input | result) |
| > 1024px | Centered 720px column |

## 10. Motion & Micro-interactions

| Token | Value |
|---|---|
| Duration | 150–200 ms |
| Easing | cubic-bezier(0.2, 0, 0, 1) |
| Animated | Badge appear (fade+rise 8px), toast slide-in |
| Never animated | Verdict color changes (instant) |

## 11. Dark Mode / Theming

Not in v1 (Streamlit default theme only). Reserved token mapping for future:

| Light token | Dark token |
|---|---|
| bg-canvas | #101418 |
| bg-surface | #1A1F26 |
| text-primary | #E6E9EC |

## 12. Related Documents

| Document | Relationship |
|---|---|
| AppFlow.md | Screens consuming these components |
| PRD.md | UX requirements driving principles |
| Rules.md | UI build conventions for agents |
