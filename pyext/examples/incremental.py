"""Example: Demonstrate incremental highlighting state."""
import syntect

# Load syntax set and theme set
ss = syntect.SyntaxSet.load_defaults(True)
ts = syntect.ThemeSet.load_defaults()

# Get Rust syntax and theme
rust = ss.find_syntax_by_name('Rust')
theme = ts.get_theme('base16-ocean.dark')

# Create highlighter
hl = syntect.Highlighter(rust, theme)

# Code to highlight
code = """fn main() {
    let x = 42;
    println!("Hello, World!");
}"""

lines = code.split('\n')

print("=== Incremental Highlighting Demo ===")
print()

# Highlight first few lines and save state
print("Highlighting first 2 lines...")
for i, line in enumerate(lines[:2]):
    tokens = hl.highlight_line(line, ss, ts)
    print(f"  Line {i}: {len(tokens)} tokens")

# Save state (for future use)
state = hl.save_state()
print(f"  Saved state: {state}")
print()

# Highlight remaining lines
print("Highlighting remaining lines...")
for i, line in enumerate(lines[2:], start=2):
    tokens = hl.highlight_line(line, ss, ts)
    print(f"  Line {i}: {len(tokens)} tokens")

print()
print("=== State Demo ===")
print(f"State path_scope_string: {state.path_scope_string}")
print(f"State styles_json length: {len(state.styles_json)}")
print(f"State single_caches_json length: {len(state.single_caches_json)}")

# Create a new highlighter from state
print()
print("Creating new highlighter from state...")
hl2 = syntect.Highlighter.from_state(state, theme)
print(f"  New highlighter: {hl2}")

# Note: In a real implementation, the state would preserve the exact
# parsing position for true incremental highlighting. Currently, the
# state stores the syntax name and can be used to create a new highlighter.
