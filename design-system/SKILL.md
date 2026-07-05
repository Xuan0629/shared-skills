# Design System — Agent-Generated UI Consistency

## Design Tokens

```yaml
colors:
  primary: "hsl(0, 0%, 88%)"
  secondary: "hsl(0, 0%, 47%)"
  tertiary: "hsl(38, 70%, 60%)"
  neutral: "hsl(0, 0%, 4%)"
  surface:
    bg: "hsl(0, 0%, 4%)"
    card: "hsl(0, 0%, 8%)"
    sidebar: "hsl(0, 0%, 5%)"
    raised: "hsl(0, 0%, 11%)"
  semantic:
    red: "hsl(0, 65%, 55%)"
    orange: "hsl(30, 80%, 52%)"
    blue: "hsl(210, 60%, 55%)"
    green: "hsl(120, 40%, 50%)"
typography:
  body: {fontFamily: "system-ui, sans-serif", fontSize: "14px"}
  heading: {fontFamily: "system-ui, sans-serif", fontSize: "20px", weight: "600"}
  mono: {fontFamily: "ui-monospace, monospace", fontSize: "13px"}
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
spacing:
  xs: "4px" | sm: "8px" | md: "12px" | lg: "16px"
  xl: "24px" | xxl: "32px" | xxxl: "48px"
border:
  default: "hsl(0, 0%, 16%)"
  focus: "hsl(38, 70%, 55%)"
```

## Rules for All Agents

When generating HTML/CSS/JS:
1. Use CSS custom properties matching the tokens — never inline styles
2. 4.5:1 minimum contrast ratio for all text
3. Use predictable class naming (BEM or similar) — no auto-generated hash classes
4. Dark mode default, light mode via `[data-theme="light"]`
5. Responsive: mobile-first, sidebar collapses at 768px
6. Zero external dependencies — no webfont CDNs, no CSS frameworks
7. JS: diff-based DOM patching, no full re-renders
