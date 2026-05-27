---
name: Rhine Professional Light
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#43474f'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#737780'
  outline-variant: '#c3c6d1'
  surface-tint: '#3a5f94'
  primary: '#001e40'
  on-primary: '#ffffff'
  primary-container: '#003366'
  on-primary-container: '#799dd6'
  inverse-primary: '#a7c8ff'
  secondary: '#3e6184'
  on-secondary: '#ffffff'
  secondary-container: '#b1d5fe'
  on-secondary-container: '#395c7f'
  tertiary: '#171f24'
  on-tertiary: '#ffffff'
  tertiary-container: '#2c3439'
  on-tertiary-container: '#949ca3'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d5e3ff'
  primary-fixed-dim: '#a7c8ff'
  on-primary-fixed: '#001b3c'
  on-primary-fixed-variant: '#1f477b'
  secondary-fixed: '#cfe4ff'
  secondary-fixed-dim: '#a6caf2'
  on-secondary-fixed: '#001d34'
  on-secondary-fixed-variant: '#24496b'
  tertiary-fixed: '#dbe3ea'
  tertiary-fixed-dim: '#bfc8ce'
  on-tertiary-fixed: '#151d22'
  on-tertiary-fixed-variant: '#40484d'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  headline-xl:
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
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
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
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 64px
  container-max: 1280px
---

## Brand & Style
The brand personality is authoritative yet accessible, embodying the precision and reliability of European professional services. It targets a corporate and analytical audience that values clarity and structured information.

The design style is **Corporate / Modern** with a subtle **Glassmorphic** influence. It utilizes a predominantly light, airy surface palette to ensure readability, accented by deep professional blues. The interface evokes a sense of calm confidence and clinical precision, moving away from high-energy vibrance toward a more grounded, institutional aesthetic.

## Colors
The palette is centered around **Rhine Blue (#003366)**, a deep, professional navy used for primary actions, branding, and high-emphasis states. 

- **Primary:** Rhine Blue (#003366) for core interactive elements and key brand moments.
- **Secondary:** A muted slate blue (#4D7094) for supportive UI elements and inactive states.
- **Surface:** Off-white and light grey backgrounds provide a clean canvas.
- **Gradients:** Background accents and header areas should use a soft linear gradient transitioning from Rhine Blue (#003366) at low opacity (5-10%) to a pure white or transparent finish, replacing any previous warm or pink-based transitions.

## Typography
This design system utilizes **Plus Jakarta Sans** across all levels to maintain a welcoming yet modern professional tone. The typography relies on generous line heights and slight negative letter spacing on larger headings to ensure a compact, editorial feel. 

Headlines should primarily use Rhine Blue to anchor the page hierarchy. Body text is kept in a dark charcoal (near-black) for optimal contrast against the light surfaces.

## Layout & Spacing
The layout follows a **Fixed Grid** model on desktop, centered within a 1280px container. It utilizes a 12-column system with 24px gutters.

- **Desktop:** 12 columns, 64px side margins.
- **Tablet:** 8 columns, 32px side margins.
- **Mobile:** 4 columns, 16px side margins.

Vertical rhythm is strictly maintained using a 4px base unit. Component padding should scale in increments of 8px (e.g., 8px, 16px, 24px) to ensure consistent internal breathing room.

## Elevation & Depth
Depth is communicated through **Tonal Layers** and **Glassmorphism**. Rather than heavy black shadows, this design system uses:

1.  **Low-Intensity Tinted Shadows:** Shadows are soft, using a diluted Rhine Blue tint (e.g., `#003366` at 8% opacity) with a large blur radius (16px to 32px).
2.  **Glass Surfaces:** Cards and modals feature a background blur (12px to 20px) with a semi-transparent white fill (80-90% opacity).
3.  **Thin Outlines:** Elements are often defined by a 1px border in a very light grey or a subtle Rhine Blue tint to provide structure without visual weight.

## Shapes
The design system employs a **Rounded** aesthetic to balance the professional blue palette with a modern, approachable feel. 

- **Standard Components:** Buttons and input fields use a 0.5rem (8px) corner radius.
- **Containers:** Cards and large surfaces use a 1rem (16px) corner radius.
- **Interactive Accents:** Selection indicators or small tags may use a 1.5rem (24px) radius to differentiate them from structural layout blocks.

## Components
Consistent application of Rhine Blue across interactive elements is critical for the "Professional Light" theme.

- **Buttons:** Primary buttons are solid Rhine Blue with white text. Secondary buttons use a Rhine Blue outline with a 5% blue tint fill on hover.
- **Active Tabs/States:** Indicated by a 3px thick Rhine Blue bottom border or a soft blue background pill.
- **Input Fields:** Use a 1px light grey border that transitions to Rhine Blue on focus. Labels are consistently set in Plus Jakarta Sans Semi-Bold.
- **Cards:** Light, glassmorphic surfaces with a subtle 1px border. They should not use heavy shadows, but rather a "lift" effect on hover using a soft blue-tinted glow.
- **Chips/Tags:** Small, rounded-xl elements using light blue backgrounds with Rhine Blue text for high legibility.
- **Data Visualizations:** Charts and graphs should utilize a monochromatic scale of Rhine Blue, supplemented by neutral greys to maintain the professional analytical aesthetic.