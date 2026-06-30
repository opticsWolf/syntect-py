"""Example: Generate CSS from theme."""
import syntect

# Load theme set
ts = syntect.ThemeSet.load_defaults()

# Get a theme
theme = ts.get_theme('base16-ocean.dark')

print("=== CSS Generation Demo ===")
print()

# Generate CSS with different class styles
for style_name in ['spaced', 'spaced_prefixed', 'class_attribute']:
    print(f"--- {style_name} ---")
    css = syntect.css_for_theme(theme, style_name)
    print(f"Length: {len(css)} chars")
    print(f"First 200 chars:")
    print(css[:200])
    print()

# Also use the generate_css alias
print("=== Using generate_css alias ===")
css = syntect.generate_css(theme, 'spaced')
print(f"Length: {len(css)} chars")
print(f"Contains scope selectors: {'variable' in css}")
