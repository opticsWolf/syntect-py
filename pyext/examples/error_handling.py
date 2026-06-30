"""Example: Demonstrate error handling patterns in syntect-py."""
import syntect

# Load syntax set and theme set
ss = syntect.SyntaxSet.load_defaults(True)
ts = syntect.ThemeSet.load_defaults()

print("=== Error Handling Demo ===\n")

# 1. LoadingError - when a file cannot be loaded
print("1. LoadingError - File not found")
try:
    ss = syntect.SyntaxSet.load_from_folder("/nonexistent/path", True)
except (syntect.LoadingError, OSError) as e:
    print(f"   Caught {type(e).__name__}: {e}")

# 2. ParsingError - when syntax parsing fails
print("\n2. ParsingError - Builder with valid input")
try:
    builder = syntect.SyntaxSetBuilder()
    builder.add_plain_text_syntax()
    ss_minimal = builder.build()
    print(f"   Built minimal syntax set: {len(ss_minimal.syntaxes())} syntaxes")
except syntect.ParsingError as e:
    print(f"   Caught ParsingError: {e}")

# 3. DumpError - when dump file is invalid
print("\n3. DumpError - Invalid dump file")
try:
    ss = syntect.load_syntax_set("/nonexistent/path.packdump")
except (syntect.DumpError, OSError) as e:
    print(f"   Caught {type(e).__name__}: {e}")

# 4. ParseSyntaxError - custom exception for parse errors
print("\n4. ParseSyntaxError - Parse error handling")
try:
    raise syntect.ParseSyntaxError("test parse error")
except syntect.ParseSyntaxError as e:
    print(f"   Caught ParseSyntaxError: {e}")

# 5. ValueError - user input errors
print("\n5. ValueError - Missing theme handling")
theme = ts.get_theme("nonexistent_theme")
if theme is None:
    print("   get_theme returns None for missing theme (no exception)")

# 6. RuntimeError - internal syntect errors
print("\n6. RuntimeError - Internal highlighting errors")
try:
    rust = ss.find_syntax_by_name("Rust")
    theme = ts.get_theme("base16-ocean.dark")
    hl = syntect.Highlighter(rust, theme)
    tokens = hl.highlight_line("fn main() {}", ss, ts)
    print(f"   Highlighting succeeded: {len(tokens)} tokens")
except RuntimeError as e:
    print(f"   Caught RuntimeError: {e}")

print("\n=== Error Types Summary ===")
print("  syntect.LoadingError    - File loading failures")
print("  syntect.ParsingError    - Syntax definition parse failures")
print("  syntect.DumpError       - Dump file read/write failures")
print("  syntect.ParseSyntaxError - Custom parse error type")
print("  ValueError               - User input validation errors")
print("  RuntimeError             - Internal syntect errors")

print("\n=== Done ===")
