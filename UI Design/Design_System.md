# UI Design System: "Indigo Cloud"

## 1. Design Philosophy
A friendly, approachable, yet professional aesthetic. Combining the softness of pastel trends with the trust and stability of Indigo Blue.
- **Keywords**: Soft, Airy, Trustworthy, Modern, Fluid.
- **Shapes**: Rounded, Pill-shaped, Soft Shadows.

## 2. Color Palette

### Primary (Indigo Focus)
- **Primary Main**: `#6366F1` (Indigo-500) - Main Buttons, Active States
- **Primary Soft**: `#A5B4FC` (Indigo-300) - Secondary accents, borders
- **Primary Deep**: `#4338CA` (Indigo-700) - Text heavy headers, Hover states

### Backgrounds
- **Canvas**: `#FDFBF7` (Warm Cream) - Main page background (reduces eye strain)
- **Surface**: `#FFFFFF` (White) - Cards, Input fields

### Accents (Pastel Support)
- **Success/Safe**: `#34D399` (Emerald-400) - Soft Mint
- **Warning/Attention**: `#FCD34D` (Amber-300) - Soft Butter
- **Error/Critical**: `#F87171` (Red-400) - Soft Coral
- **Gradient**: Linear Gradient (Top-Left to Bottom-Right) from `#6366F1` to `#818CF8`.

## 3. Typography
- **Font Family**: `Quicksand` or `Nunito` (Rounded Sans-serif).
- **Headings**: Bold, Soft Indigo (`#4338CA`).
- **Body**: Dark Grayish Blue (`#374151`).

## 4. Component Styles

### Buttons
- **Shape**: Pill-shaped (Full rounded corners).
- **Style**: Soft Shadow (`shadow-lg`, `shadow-indigo-500/30`).
- **Hover**: Slight lift (`-translate-y-0.5`).

### Cards / Containers
- **Shape**: `rounded-2xl` or `rounded-3xl`.
- **Border**: Very subtle (`border-indigo-100` or no border).
- **Shadow**: Large, diffuse, soft shadow (`shadow-xl`, `shadow-indigo-100`).
- **Texture**: Optional "Glassmorphism" overlay for header.

### Inputs
- **Shape**: Pill-shaped or heavily rounded (`rounded-xl`).
- **Background**: White.
- **Border**: Default `border-gray-200`, Focus `ring-2 ring-indigo-300`.

## 5. Tailwind Configuration (Mental Model)
```javascript
theme: {
  extend: {
    colors: {
      cream: '#FDFBF7',
      indigo: {
        350: '#818CF8', // Custom soft steps
      }
    },
    fontFamily: {
      sans: ['Nunito', 'sans-serif'],
    },
    borderRadius: {
      '4xl': '2rem',
    }
  }
}
```
