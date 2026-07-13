# UX Design Deep Knowledge - For uxdesign-agent

## Design System Foundation

### 1. CSS Custom Properties (Design Tokens)

```css
/* design-tokens.css */
:root {
  /* Colors */
  --color-primary-50: #EFF6FF;
  --color-primary-100: #DBEAFE;
  --color-primary-500: #3B82F6;
  --color-primary-600: #2563EB;
  --color-primary-700: #1D4ED8;
  
  --color-gray-50: #F9FAFB;
  --color-gray-100: #F3F4F6;
  --color-gray-200: #E5E7EB;
  --color-gray-300: #D1D5DB;
  --color-gray-400: #9CA3AF;
  --color-gray-500: #6B7280;
  --color-gray-600: #4B5563;
  --color-gray-700: #374151;
  --color-gray-800: #1F2937;
  --color-gray-900: #111827;
  
  /* Typography */
  --font-family-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-family-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;    /* 16px */
  --font-size-lg: 1.125rem;  /* 18px */
  --font-size-xl: 1.25rem;   /* 20px */
  --font-size-2xl: 1.5rem;   /* 24px */
  --font-size-3xl: 1.875rem; /* 30px */
  --font-size-4xl: 2.25rem;  /* 36px */
  
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
  
  /* Spacing */
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-5: 1.25rem;  /* 20px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */
  --space-10: 2.5rem;  /* 40px */
  --space-12: 3rem;    /* 48px */
  --space-16: 4rem;    /* 64px */
  
  /* Border Radius */
  --radius-none: 0;
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-2xl: 1rem;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  
  /* Transitions */
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 200ms ease-in-out;
  --transition-slow: 300ms ease-in-out;
}
```

### 2. Typography Scale

```css
/* typography.css */
.text-display {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
  letter-spacing: -0.025em;
}

.text-h1 {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
}

.text-h2 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-tight);
}

.text-h3 {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-normal);
}

.text-body {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-normal);
  line-height: var(--line-height-relaxed);
}

.text-small {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
  line-height: var(--line-height-normal);
}

.text-caption {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-normal);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

### 3. Component Patterns

```css
/* button.css */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  font-family: var(--font-family-sans);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  line-height: 1;
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
  cursor: pointer;
  border: none;
  outline: none;
}

.btn:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Variants */
.btn-primary {
  background-color: var(--color-primary-600);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-700);
}

.btn-secondary {
  background-color: var(--color-gray-100);
  color: var(--color-gray-700);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--color-gray-200);
}

.btn-outline {
  background-color: transparent;
  border: 1px solid var(--color-gray-300);
  color: var(--color-gray-700);
}

.btn-outline:hover:not(:disabled) {
  background-color: var(--color-gray-50);
  border-color: var(--color-gray-400);
}

.btn-ghost {
  background-color: transparent;
  color: var(--color-gray-600);
}

.btn-ghost:hover:not(:disabled) {
  background-color: var(--color-gray-100);
}

/* Sizes */
.btn-sm { padding: var(--space-1) var(--space-3); font-size: var(--font-size-xs); }
.btn-md { padding: var(--space-2) var(--space-4); }
.btn-lg { padding: var(--space-3) var(--space-6); font-size: var(--font-size-base); }

/* Input styles */
.input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  font-size: var(--font-size-base);
  line-height: var(--line-height-normal);
  color: var(--color-gray-900);
  background-color: white;
  border: 1px solid var(--color-gray-300);
  border-radius: var(--radius-lg);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.input:disabled {
  background-color: var(--color-gray-100);
  cursor: not-allowed;
}

.input-error {
  border-color: var(--color-red-500);
}

.input-error:focus {
  box-shadow: 0 0 0 3px var(--color-red-100);
}
```

## Layout Systems

### 1. Grid System

```css
/* grid.css */
.grid {
  display: grid;
  gap: var(--space-4);
}

/* Auto-fit responsive grid */
.grid-auto {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

/* 12-column grid */
.grid-cols-12 { grid-template-columns: repeat(12, 1fr); }
.col-span-1 { grid-column: span 1 / span 1; }
.col-span-2 { grid-column: span 2 / span 2; }
.col-span-3 { grid-column: span 3 / span 3; }
.col-span-4 { grid-column: span 4 / span 4; }
.col-span-6 { grid-column: span 6 / span 6; }
.col-span-8 { grid-column: span 8 / span 8; }
.col-span-12 { grid-column: span 12 / span 12; }

/* Flex utilities */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.items-start { align-items: flex-start; }
.items-end { align-items: flex-end; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.justify-end { justify-content: flex-end; }
.gap-1 { gap: var(--space-1); }
.gap-2 { gap: var(--space-2); }
.gap-3 { gap: var(--space-3); }
.gap-4 { gap: var(--space-4); }
.gap-6 { gap: var(--space-6); }
.gap-8 { gap: var(--space-8); }

/* Responsive */
@media (max-width: 640px) {
  .sm\:flex-col { flex-direction: column; }
  .sm\:grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
}

@media (max-width: 768px) {
  .md\:flex-col { flex-direction: column; }
  .md\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
}
```

### 2. Responsive Breakpoints

```css
/* breakpoints.css */
/* Mobile: 320px - 639px */
/* Tablet: 640px - 1023px */
/* Desktop: 1024px - 1279px */
/* Large Desktop: 1280px+ */

.container {
  width: 100%;
  max-width: 1280px;
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--space-4);
  padding-right: var(--space-4);
}

@media (min-width: 640px) {
  .container { padding-left: var(--space-6); padding-right: var(--space-6); }
}

@media (min-width: 1024px) {
  .container { padding-left: var(--space-8); padding-right: var(--space-8); }
}
```

## Accessibility

### 1. Focus Management

```css
/* Focus visible for keyboard navigation */
:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

/* Skip link */
.skip-link {
  position: absolute;
  top: -100%;
  left: 0;
  padding: var(--space-2) var(--space-4);
  background: var(--color-primary-600);
  color: white;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}

/* Screen reader only */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

### 2. Color Contrast

```css
/* WCAG AA Compliance */
/* Text on white background */
.text-primary { color: var(--color-gray-900); } /* 21:1 contrast */
.text-secondary { color: var(--color-gray-600); } /* 5.7:1 contrast - OK */

/* Minimum contrast for small text (under 18px or bold 14px) */
.text-small { color: var(--color-gray-700); } /* 7:1 contrast - OK */

/* Interactive elements */
.btn { color: white; } /* 9:1 contrast on blue */
.link { color: var(--color-primary-600); } /* 4.6:1 contrast - OK */
```

### 3. Animations

```css
/* Respect prefers-reduced-motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Subtle animations for those who allow */
@media (prefers-reduced-motion: no-preference) {
  .fade-in {
    animation: fadeIn 200ms ease-out;
  }
  
  .slide-up {
    animation: slideUp 300ms ease-out;
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { 
    opacity: 0; 
    transform: translateY(10px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}
```
