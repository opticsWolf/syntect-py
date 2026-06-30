"""Example: Demonstrate incremental highlighting with real state."""
import syntect

# Load syntax set and theme set
ss = syntect.SyntaxSet.load_defaults(True)
ts = syntect.ThemeSet.load_defaults()

# Get Rust syntax and theme
rust = ss.find_syntax_by_name("Rust")
theme = ts.get_theme("base16-ocean.dark")

# Code to highlight
code = """fn main() {
    let x = 42;
    let y = x * 2;
    println!("Result: {}", y);
}"""

lines = code.split("\n")

print("=== Incremental Highlighting Demo ===\n")

# Create highlighter and highlight first line
hl = syntect.Highlighter(rust, theme)
print("Highlighting first line...")
tokens = hl.highlight_line(lines[0], ss, ts)
print(f"  Line 0: {len(tokens)} tokens")

# Save state after first line
state = hl.save_state(ss, ts)
print(f"  State saved: path_scope_stack has {len(state.path_scope_stack)} scopes\n")

# Create new highlighter from saved state
hl2 = syntect.Highlighter.from_state(state, theme)
print(f"  New highlighter from state: {hl2}\n")

# Highlight remaining lines
print("Highlighting remaining lines...")
for i, line in enumerate(lines[1:], start=1):
    tokens = hl.highlight_line(line, ss, ts)
    print(f"  Line {i}: {len(tokens)} tokens")

print("\n=== CRLF Line Endings ===")
# Test CRLF handling
crlf_code = "fn main() {\r\n    let x = 42;\r\n}"
tokens = hl.highlight_lines(crlf_code, ss, ts)
for i, line_tokens in enumerate(tokens):
    for _, text in line_tokens:
        assert "\r" not in text, f"Found \\r in text: {repr(text)}"
print("  CRLF handling verified: no \\r in token text")

print("\n=== Done ===")
