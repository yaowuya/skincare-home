---
name: Cosmetic Insights Portfolio
colors:
  surface: '#f8f9ff'
  surface-dim: '#d0dbed'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e6eeff'
  surface-container-high: '#dee9fc'
  surface-container-highest: '#d9e3f6'
  on-surface: '#121c2a'
  on-surface-variant: '#5b3f44'
  inverse-surface: '#27313f'
  inverse-on-surface: '#eaf1ff'
  outline: '#8f6f74'
  outline-variant: '#e4bdc3'
  surface-tint: '#bc0051'
  primary: '#b7004f'
  on-primary: '#ffffff'
  primary-container: '#e40a65'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb1c0'
  secondary: '#b6155e'
  on-secondary: '#ffffff'
  secondary-container: '#fd5393'
  on-secondary-container: '#5d002c'
  tertiary: '#6448b3'
  on-tertiary: '#ffffff'
  tertiary-container: '#7e62ce'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffd9df'
  primary-fixed-dim: '#ffb1c0'
  on-primary-fixed: '#3f0017'
  on-primary-fixed-variant: '#90003d'
  secondary-fixed: '#ffd9e1'
  secondary-fixed-dim: '#ffb1c6'
  on-secondary-fixed: '#3f001b'
  on-secondary-fixed-variant: '#8e0046'
  tertiary-fixed: '#e8ddff'
  tertiary-fixed-dim: '#cebdff'
  on-tertiary-fixed: '#21005e'
  on-tertiary-fixed-variant: '#4f319c'
  background: '#f8f9ff'
  on-background: '#121c2a'
  surface-variant: '#d9e3f6'
  bg-soft-lavender: '#F5F3FF'
  bg-soft-pink: '#FFF1F2'
  glass-white: rgba(255, 255, 255, 0.7)
  data-border: '#E5E7EB'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-padding-desktop: 40px
  container-padding-mobile: 20px
  gutter: 24px
  section-gap: 80px
---

## Brand & Style

The visual identity of the design system is rooted in **Modern Minimalism** fused with **Glassmorphism**. It is designed to mirror the sophistication of the cosmetic industry while maintaining the analytical rigor of a data professional. 

The aesthetic is characterized by:
- **Luminous Clarity:** Utilizing high levels of whitespace and translucent layers to create an "airy" and "clean" feel.
- **Trend-Forward Professionalism:** A balance of vibrant editorial accents against a structured, data-driven layout.
- **Soft Precision:** High roundedness (2xl/3xl) on containers paired with sharp, legible typography to convey both approachability and expertise.

## Colors

The palette is anchored by a **Vibrant Pink** primary accent, symbolizing energy and the beauty sector's vibrancy. 

- **Primary & Secondary:** Used for calls-to-action, active states, and data highlights.
- **Surface Gradients:** The design utilizes subtle linear gradients (e.g., from `bg-soft-lavender` to `bg-soft-pink`) to define content areas without using harsh lines.
- **Glassmorphism:** A specific `glass-white` token is used for elevated cards, intended to be paired with a backdrop-blur for a frosted effect.
- **Neutrality:** Grays are kept cool and minimal to ensure that trend data and product photography remain the focal point.

## Typography

**Plus Jakarta Sans** is the exclusive typeface for the design system. Its modern, geometric construction and slightly rounded terminals perfectly complement the "Beauty" aesthetic while maintaining the "Data" clarity required for professional reporting.

- **Headlines:** Use tighter letter spacing and bold weights to create a strong visual hierarchy.
- **Data Visualization:** Labels use the semi-bold weight for readability at smaller scales (12-14px).
- **Body Copy:** Maintains a generous line height (1.5x - 1.6x) to ensure long-form trend reports are easy to digest.

## Layout & Spacing

The design system employs a **Fluid Grid** with fixed-width maximums for readability on large displays.

- **Grid Model:** A 12-column layout for desktop with 24px gutters. Elements should span 4 columns for small cards and 6 columns for primary data visualizations.
- **Whitespace:** Large vertical gaps (`section-gap`) are intentional, allowing the user's eye to rest between distinct trend insights.
- **Responsive Behavior:** On mobile, columns collapse to a single stack. Horizontal padding shrinks from 40px to 20px to maximize screen real estate for product imagery.

## Elevation & Depth

This design system moves away from traditional heavy shadows in favor of **Tonal Layers and Glassmorphism**:

- **Tier 1 (Base):** Subtle pastel gradients or pure white.
- **Tier 2 (Glass Cards):** Use `glass-white` with a `20px` backdrop-blur and a 1px white border at 20% opacity. This creates a "frosted glass" effect that feels premium and light.
- **Tier 3 (Active Elements):** For hovered buttons or focused cards, use an **Ambient Shadow**: a very soft, diffused pink-tinted shadow (`rgba(255, 45, 120, 0.12)`) with a 30px blur and 10px offset.

## Shapes

The shape language is defined by high-radius curves to evoke a "soft-touch" feel common in cosmetic packaging.

- **Small Components (Buttons, Inputs):** Use `rounded-lg` (1rem / 16px).
- **Main Cards & Containers:** Use `rounded-xl` (1.5rem / 24px) or higher for a "bubble" or "pill" inspired look (3xl).
- **Images:** All product photography must use the same corner radius as their parent containers to maintain the organic, soft aesthetic.

## Components

### Buttons
- **Primary:** Solid `primary-color` with white text. Rounded-pill shape. No sharp corners.
- **Secondary:** Transparent background with a `primary-color` border and text.

### Glass Cards
- Used for filters and product listings.
- Background: `glass-white`.
- Border: 1px `data-border` or low-opacity white.
- Backdrop Filter: `blur(12px)`.

### Inputs & Selects
- Background should be a very light gray or off-white.
- Focus state uses a 2px `primary-color` outer glow.
- Labels are always positioned above the input in `label-md` style.

### Chips/Tags
- Used for "Trend Categories" (e.g., #Skincare, #Vegan).
- Soft pastel backgrounds (lavender or pink) with slightly darker text of the same hue.
- Fully rounded ends (pill-shaped).

### Data Visualizations
- Charts should use a mix of the primary pink, secondary pink, and tertiary lavender.
- Grid lines should be kept at 5% opacity to minimize visual noise.