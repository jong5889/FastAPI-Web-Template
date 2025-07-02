"""Simple design tokens and theme utilities for the Streamlit frontend."""

import streamlit as st

# Optional Tailwind CSS CDN for utility classes
TAILWIND_CDN = "https://cdn.jsdelivr.net/npm/tailwindcss@3.4.1/dist/tailwind.min.css"

# Color palette
COLORS = {
    "primary": "#1E90FF",
    "secondary": "#FF7F50",
    "background": "#FFFFFF",
    "text": "#333333",
}

# Dark mode color palette
DARK_COLORS = {
    "primary": "#93c5fd",
    "secondary": "#fcd34d",
    "background": "#1f2937",
    "text": "#f9fafb",
}

# Spacing scale in pixels
SPACING = {
    "small": 4,
    "medium": 8,
    "large": 16,
}

# Font settings
FONTS = {
    "family": "sans-serif",
    "size_body": "16px",
    "size_heading": "24px",
}


def apply_theme(*, dark_mode: bool = False) -> None:
    """Inject CSS variables and Tailwind CSS for consistent styling.

    Parameters
    ----------
    dark_mode: bool
        When ``True`` the dark color palette will be used.
    """

    palette = DARK_COLORS if dark_mode else COLORS
    css = f"""
    <style>
    @import url('{TAILWIND_CDN}');
    :root {{
        --color-primary: {palette['primary']};
        --color-secondary: {palette['secondary']};
        --color-background: {palette['background']};
        --color-text: {palette['text']};
        --spacing-small: {SPACING['small']}px;
        --spacing-medium: {SPACING['medium']}px;
        --spacing-large: {SPACING['large']}px;
        --font-family-base: {FONTS['family']};
        --font-size-body: {FONTS['size_body']};
        --font-size-heading: {FONTS['size_heading']};
    }}
    body {{
        background-color: var(--color-background);
        color: var(--color-text);
        font-family: var(--font-family-base);
        font-size: var(--font-size-body);
    }}
    h1, h2, h3, h4, h5, h6 {{
        font-size: var(--font-size-heading);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
