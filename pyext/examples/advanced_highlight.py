"""Example: Advanced syntax highlighting with parsing and themes"""
import syntect

# Load default syntaxes and themes
ss = syntect.SyntaxSet.load_defaults(True)
ts = syntect.ThemeSet.load_defaults()

# Get Python syntax and a theme
python = ss.find_syntax_by_name("Python")
theme = ts.get_theme("base16-ocean.dark")

print("=== Theme Information ===")
print(f"Name: {theme.name}")
print(f"Key: {theme.key}")
print(f"Author: {theme.author}")
print(f"Settings: {theme.settings}")
print(f"Number of scopes: {len(theme.scopes)}")
print("\nFirst 5 theme scopes:")
for item in theme.scopes[:5]:
    print(f"  {item.scope[:60]}... fg={item.foreground}, bg={item.background}, font={item.font_style}")

print("\n=== Parsing ===")
# Parse a line
parse_state = syntect.ParseState("Python")
code = "def hello(name: str) -> str:\n    return f'Hello, {name}!'"
output = parse_state.parse_line(code, ss)

print(f"Ops: {len(output.ops)}")
for pos, op in output.ops[:10]:
    print(f"  pos={pos}: {op}")

print(f"\nWarnings: {output.warnings}")

print("\n=== Scope Stack ===")
# Use a scope stack
stack = syntect.ScopeStack()
stack.push(syntect.Scope("source.python"))
stack.push(syntect.Scope("meta.function.python"))
stack.push(syntect.Scope("keyword.declaration.def.python"))
print(f"Stack: {stack.as_string()}")
print(f"Length: {stack.len()}")

# Apply a pop operation
pop_op = syntect.ScopeStackOp.pop(1)
stack.apply(pop_op)
print(f"After pop(1): {stack.as_string()}")

print("\n=== Highlighting ===")
# Highlight with the highlighter
hl = syntect.Highlighter(python, theme)
tokens = hl.highlight_line(code, ss, ts)

print(f"Tokens: {len(tokens)}")
for style, text in tokens[:10]:
    print(f"  [{style.foreground.to_hex()}] {repr(text)}")

# Get full HTML
result = syntect.highlight_string(code, "Python", "base16-ocean.dark", ss, ts)
print(f"\n=== HTML Output ===")
print(f"Length: {len(result.html)} chars")
print(result.html[:300] + "...")

# Get CSS for the theme
css = syntect.css_for_theme(theme, "spaced")
print(f"\n=== CSS Output ===")
print(f"Length: {len(css)} chars")
print(css[:300] + "...")

# Get HTML with line numbers
line_html = syntect.highlighted_html_at_line_and_column_number(code, python, theme, ss, ts, 1)
print(f"\n=== HTML with Line Numbers ===")
print(f"Length: {len(line_html)} chars")
print(line_html[:300] + "...")

print("\n=== All Done ===")
