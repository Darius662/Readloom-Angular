# Theming Guide

This document explains how theming works in the Readloom Angular frontend.

## Overview

Readloom uses a dual-layer theming approach:
1. **Angular Material 21** - Provides Material 3 design tokens and component styling
2. **CSS Custom Properties** - Provides theme-aware variables for custom components

## Architecture

```
src/styles.scss          # Global theme configuration
src/app/services/theme.service.ts  # Runtime theme switching
```

## Angular Material Theme

The app uses Angular Material 21's simplified theming API with Material 3 design tokens.

### Theme Configuration

```scss
// src/styles.scss
@use '@angular/material' as mat;

$readloom-theme: (
  color: mat.$blue-palette,
  typography: Roboto,
  density: 0
);

html {
  color-scheme: dark light;
  @include mat.theme($readloom-theme);

  // Override Material's auto-generated primary color with brand color
  @include mat.theme-overrides((
    primary: #0d6efd,
  ));
}
```

### Key Points

- `mat.theme()` applies all Material component themes at once
- `color-scheme: dark light` enables automatic dark/light mode detection
- `mat.theme-overrides()` customizes Material Design tokens (like primary color)

## CSS Custom Properties

Custom components should use CSS variables instead of hardcoded colors. This ensures they respond to theme changes.

### Available Variables

```css
/* Brand Colors */
--primary-color: #0d6efd;
--secondary-color: #757575;
--success-color: #4caf50;
--danger-color: #f44336;
--warning-color: #ff9800;
--info-color: #00bcd4;

/* Theme-Responsive Colors (change with light/dark) */
--bg-color        /* Main background */
--bg-card         /* Card/surface background */
--bg-hover        /* Hover state background */
--border-color    /* Border color */
--text-primary    /* Primary text color */
--text-secondary  /* Secondary/muted text color */

/* Utilities */
--border-radius: 4px;
--box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
--box-shadow-hover: 0 4px 12px rgba(0, 0, 0, 0.3);
```

### Dark Theme Values (Default)

```css
:root {
  --bg-color: #212529;
  --bg-card: #2c3034;
  --bg-hover: #373b3e;
  --border-color: #373b3e;
  --text-primary: #f8f9fa;
  --text-secondary: #adb5bd;
}
```

### Light Theme Values

```css
.light-theme {
  --bg-color: #fafafa;
  --bg-card: #ffffff;
  --bg-hover: #f5f5f5;
  --border-color: #e0e0e0;
  --text-primary: #212529;
  --text-secondary: #757575;
}
```

## Writing Theme-Aware Components

### DO: Use CSS Variables

```css
/* Good - responds to theme changes */
.my-component {
  background-color: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.my-component:hover {
  background-color: var(--bg-hover);
}
```

### DON'T: Use Hardcoded Colors

```css
/* Bad - won't respond to theme changes */
.my-component {
  background-color: #2c3034;
  color: #f8f9fa;
  border: 1px solid #373b3e;
}
```

### Component CSS Pattern

For component-specific styles, focus on **layout only**. Let Material components and CSS variables handle colors:

```css
/* my-component.component.css */

/* Layout */
.container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
  padding: 1rem;
}

/* Only add colors when necessary, using variables */
.custom-card {
  background-color: var(--bg-card);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
}

.custom-card:hover {
  box-shadow: var(--box-shadow-hover);
}
```

## Theme Service

The `ThemeService` handles runtime theme switching.

### Usage

```typescript
import { ThemeService } from './services/theme.service';

@Component({...})
export class MyComponent {
  constructor(private themeService: ThemeService) {}

  // Get current theme as observable
  theme$ = this.themeService.getTheme();

  // Get current theme synchronously
  currentTheme = this.themeService.getCurrentTheme(); // 'light' | 'dark'

  // Check if dark mode
  isDark = this.themeService.isDarkMode(); // boolean

  // Toggle between light and dark
  toggleTheme() {
    this.themeService.toggleTheme();
  }

  // Set specific theme
  setDark() {
    this.themeService.setTheme('dark');
  }
}
```

### How It Works

1. On initialization, checks for saved theme in localStorage
2. Falls back to system preference (`prefers-color-scheme`)
3. Applies theme by adding/removing `.light-theme` class on `<body>`
4. Persists selection to localStorage

## Material Component Overrides

Global Material component styling is in `src/styles.scss`:

```scss
// Cards
.mat-mdc-card {
  background-color: var(--bg-card) !important;
  border: 1px solid var(--border-color);
  box-shadow: var(--box-shadow) !important;
}

// Dialogs
.mat-mdc-dialog-container {
  --mat-dialog-container-color: var(--bg-card);
}

// Sidenav
.mat-sidenav {
  background-color: var(--bg-card);
}

// Toolbar
.mat-toolbar {
  background-color: var(--bg-card);
  color: var(--text-primary);
}
```

## Utility Classes

Available utility classes for quick styling:

```html
<!-- Text colors -->
<span class="text-primary">Primary</span>
<span class="text-success">Success</span>
<span class="text-danger">Danger</span>
<span class="text-warning">Warning</span>
<span class="text-info">Info</span>
<span class="text-muted">Muted</span>

<!-- Background colors -->
<div class="bg-primary">Primary background</div>
<div class="bg-success">Success background</div>
<div class="bg-danger">Danger background</div>
```

## Angular Material 21 Button Syntax

Angular Material 21 uses new button attribute syntax:

```html
<!-- Basic buttons -->
<button matButton>Basic</button>
<button matButton="outlined">Outlined</button>
<button matButton="filled">Filled (primary action)</button>
<button matButton="elevated">Elevated</button>
<button matButton="tonal">Tonal</button>

<!-- Icon buttons -->
<button matIconButton>
  <mat-icon>settings</mat-icon>
</button>

<!-- FAB -->
<button matFab>
  <mat-icon>add</mat-icon>
</button>
<button matMiniFab>
  <mat-icon>add</mat-icon>
</button>
```

## Migration Notes

### From Bootstrap/Tailwind

If migrating components from Bootstrap or Tailwind:

1. Remove `[data-bs-theme="dark"]` selectors
2. Replace Bootstrap color classes with CSS variables
3. Remove Tailwind utility classes
4. Use Material components where possible

### Deprecated Patterns

Avoid these deprecated patterns:

```css
/* DON'T use ::ng-deep */
::ng-deep .mat-component { }

/* DON'T use Bootstrap theme selectors */
[data-bs-theme="dark"] .card { }

/* DON'T use excessive !important */
.my-class {
  color: red !important;
}
```
