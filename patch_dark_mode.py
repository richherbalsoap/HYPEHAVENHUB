import os

css_patch = """
/* =========================================================================
   PERMANENT DARK MODE CONTRAST FIXES
   Ensures all buttons, inputs, badges, and icons have readable contrast
   ========================================================================= */

/* Fix inline styles on ALL buttons using attribute selectors */
html.dark .btn[style*="background-color: var(--primary)"],
html.dark .btn[style*="background-color: var(--primary-fixed)"],
html.dark .btn-pink,
html.dark .btn-artisan-primary,
html.dark .btn-glamour-primary,
html.dark .btn-pink-solid,
html.dark .btn-add-to-cart,
html.dark .btn-buy-now,
html.dark .btn-emerald {
  background-color: var(--primary) !important;
  color: #190a0a !important; /* Dark text for contrast against light pink primary */
  border-color: var(--primary) !important;
}

/* Specific fix for inputs and quantity selectors */
html.dark input, 
html.dark select, 
html.dark textarea,
html.dark .form-control {
  background-color: var(--surface-container-low) !important;
  color: #ffffff !important;
  border-color: var(--outline-variant) !important;
}

html.dark input::placeholder, 
html.dark textarea::placeholder,
html.dark .form-control::placeholder {
  color: #b0b0b0 !important;
  opacity: 1 !important;
}

html.dark .quantity-selector {
  background-color: var(--surface-container-low) !important;
  border-color: var(--outline-variant) !important;
}
html.dark .quantity-selector input,
html.dark .quantity-selector button,
html.dark .quantity-selector .btn {
  color: #ffffff !important;
  background: transparent !important;
}

/* Fix USP Icons (Image 2) */
html.dark .usp-icon-wrapper,
html.dark [style*="background: #fdf2f2"],
html.dark [style*="background-color: #fdf2f2"],
html.dark [style*="background: #dcfce7"],
html.dark [style*="background-color: #dcfce7"] {
  background-color: var(--surface-container-high) !important;
  color: #ffffff !important;
}

/* Fix specific hardcoded inline backgrounds */
html.dark [style*="background: #ffffff"],
html.dark [style*="background-color: #ffffff"],
html.dark [style*="background-color: #fff"],
html.dark [style*="background: #fff"],
html.dark .glamour-form-card {
  background-color: var(--surface-container-lowest) !important;
}

/* Fix badges */
html.dark .badge {
  background-color: var(--surface-container-high) !important;
  color: #ffffff !important;
}
"""

style_path = os.path.join('static', 'css', 'style.css')
with open(style_path, 'a', encoding='utf-8') as f:
    f.write(css_patch)

print("CSS appended successfully!")
