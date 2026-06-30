"""Example: Basic syntax highlighting with all output formats."""
import syntect

# Load default syntaxes and themes
ss = syntect.SyntaxSet.load_defaults(True)
ts = syntect.ThemeSet.load_defaults()

# Get Rust syntax and a theme
rust = ss.find_syntax_by_name("Rust")
theme = ts.get_theme("base16-ocean.dark")

# Create highlighter
hl = syntect.Highlighter(rust, theme)

# Highlight a line
code = "fn main() {\n    println!(\"Hello, World!\");\n}"
tokens = hl.highlight_lines(code, ss, ts)

# Print tokens with colors
print("=== Tokens ===")
for i, line_tokens in enumerate(tokens):
    print(f"Line {i}:")
    for style, text in line_tokens:
        print(f"  [{style.foreground.to_hex()}] {repr(text)}")

# Get full HTML output
result = syntect.highlight_string(code, "Rust", "base16-ocean.dark", ss, ts)
print(f"\n=== HTML ({len(result.html)} chars) ===")
print(result.html[:200] + "...")

# Get terminal escape codes
escaped = result.as_terminal_escaped(True)
print(f"\n=== Terminal Escape ({len(escaped)} chars) ===")
print(f"Contains escape codes: {chr(0x1b) in escaped}")

# Get LaTeX output
latex = result.as_latex_escaped()
print(f"\n=== LaTeX ({len(latex)} chars) ===")
print(latex[:200] + "...")

# Test as_html with different background modes
print("\n=== as_html modes ===")
print(f"  no: {len(result.as_html('no', None))} chars")
print(f"  yes: {len(result.as_html('yes', None))} chars")
print(f"  if_different: {len(result.as_html('if_different', None))} chars")

print("\n=== Done ===")
