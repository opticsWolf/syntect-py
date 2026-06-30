"""Example: Generate CSS from theme with different class styles."""
import syntect

# Load theme set
ts = syntect.ThemeSet.load_defaults()

# Get a theme
theme = ts.get_theme("base16-ocean.dark")

print("=== CSS Generation Demo ===\n")

# Generate CSS with different class styles
for style_name in ["spaced", "class_attribute"]:
    print(f"--- {style_name} ---")
    css = syntect.css_for_theme(theme, style_name)
    print(f"Length: {len(css)} chars")
    print(f"First 200 chars:")
    print(css[:200])
    print()

# Use spaced_prefixed style
print("--- spaced_prefixed (custom-) ---")
class_style = syntect.ClassStyle.spaced_prefixed("syn-")
css = syntect.css_for_theme(theme, "spaced_prefixed")
print(f"Length: {len(css)} chars")
print(f"Contains 'syn-' prefix: {'syn-' in css}")
print(css[:200])

print("\n=== Done ===")
