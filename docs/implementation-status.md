# PyO3 Implementation Status

## Overview
Python bindings for syntect's syntax highlighting library using PyO3 0.29.

## Completed Phases

### ✅ Phase 0: Foundation (COMPLETE)
- Initial PyO3 0.29 setup with stub implementations
- Module structure, build system (maturin)
- All 11 source files created

### ✅ Phase 1: Core Types (COMPLETE)
- `Color`, `FontStyle`, `Style`, `StyleModifier`
- `SyntaxSet`, `SyntaxReference`, `ThemeSet`, `Theme`, `ThemeSettings`
- Real highlighting engine integration with `Highlighter`
- All wrapper types properly extract data from syntect's internal types

### ✅ Phase 2: Loading Infrastructure (COMPLETE)
- `SyntaxSetBuilder` wrapper with `add_from_folder`, `build`, `warnings`
- `load_from_folder` static method
- `into_builder` for extending loaded SyntaxSets
- `find_syntax_by_scope`
- Custom error types: `LoadingError`, `ParsingError`, `DumpError`
- Real dump save/load for SyntaxSet and ThemeSet
- Theme key stored for proper Highlighter lookup

### ✅ Phase 3: Highlighting Engine (COMPLETE)
- Real `Highlighter` with colored token output using real `syntect::highlighting::Style`
- Real `ParseState` with full `syntect::parsing::ParseState` integration
- Real `ParseLineOutput` with ops, replayed, and warnings
- Real `Scope` with `from_string`, `to_string`, `len`, `is_prefix_of`
- Real `ScopeStack` with `push`, `pop`, `apply`, `as_string`
- Real `ScopeStackOp` with push, pop, clear, restore, noop operations
- Real `HighlightState` with syntax name and theme key storage
- `highlight_line` and `highlight_lines` now take `theme_set` parameter
- Tokens return real `PyStyle` objects (not formatted strings)

### ✅ Phase 4: Output Utilities (COMPLETE)
- **`as_terminal_escaped(tokens, include_bg)`** - 24-bit ANSI escape sequences
  - Properly blends foreground with background for alpha transparency
  - Supports background color output
  - Example: `\x1b[48;2;43;48;59m\x1b[38;2;180;142;173mfn\x1b[38;2;192;197;206m ...`

- **`as_html(tokens, include_bg)`** - HTML with inline styles
  - Merges adjacent tokens with same style into single `<span>`
  - Supports `include_bg` parameter: "no", "yes", "if_different"
  - Example: `<span style="background-color:#2B303B;color:#B48EAD;">fn</span>`

- **`as_latex_escaped(tokens)`** - LaTeX `\textcolor` output
  - Properly escapes LaTeX special characters (`\`, `{`, `}`)
  - Skips spaces/newlines when style hasn't changed
  - Example: `\textcolor[RGB]{180,142,173}{fn}\textcolor[RGB]{192,197,206}{ }...`

- **`css_for_theme(theme, class_style)`** - CSS generation
  - Uses syntect's real `css_for_theme_with_class_style`
  - Supports "spaced", "spaced_prefixed", "class_attribute" styles
  - Generates complete CSS with scope selectors

- **`highlighted_html_for_string_py(code, syntax_ref, theme, syntax_set, theme_set, include_bg, start_line)`** - Full HTML
  - Uses syntect's real `highlighted_html_for_string`
  - Returns `<pre>` block with inline styles
  - Properly handles all syntax highlighting and theme application

- **`highlighted_html_at_line_and_column_number(code, syntax_ref, theme, syntax_set, theme_set, start_line)`** - HTML with line numbers
  - Each line gets `data-line` attribute
  - Uses syntect's `HighlightLines` and `start_highlighted_html_snippet`
  - Example: `<pre style="background-color:#2b303b;"><span data-line="1">...</span></pre>`

- **`ClassStyle`** enum - CSS class style for HTML output
  - `ClassStyle.spaced()` - Scope atoms as space-separated classes
  - `ClassStyle.spaced_prefixed(prefix)` - Prefixed class names
  - `ClassStyle.class_attribute()` - Class attribute style

- **`IncludeBg`** enum - Controls background color in HTML output
  - `IncludeBg.no()` - No background color
  - `IncludeBg.yes()` - Always include background
  - `IncludeBg.if_different()` - Only if different from default

- **`PyStyle`** - Added `#[getter]` for `foreground`, `background`, `font_style`
- **`PyFontStyle`** - Added `#[getter]` for `bits`
- **`PyColor`** - Added `#[getter]` for `r`, `g`, `b`, `a`
- All tokens now return real `PyStyle` objects instead of formatted strings

### ✅ Phase 5: Convenience & Polish (COMPLETE)
- **Enhanced `HighlightResult`** with convenience methods:
  - `as_html(include_bg)` - Convert tokens to HTML
  - `as_terminal_escaped(include_bg)` - Convert tokens to terminal escapes
  - `as_latex_escaped()` - Convert tokens to LaTeX output
  - All methods work on the result's tokens directly

- **`ThemeItem`** with real style data:
  - `foreground` - Foreground color hex string
  - `background` - Background color hex string
  - `font_style` - Font style bits
  - `style_modifier` - Full style modifier debug string

- **`Style.from_hex_styles(fg, bg, font_bits)`** - Static factory for creating styles
- **`Style.__eq__`** - Equality comparison for styles
- **`Color.from_hex(hex_str)`** - Parse hex color strings
- **`FontStyle` bitwise operations** - `|`, `&`, `^`, `~`

- **Type stubs** - `syntect.pyi` with complete type hints for all classes and functions
- **Tests** - 36 pytest tests covering all major functionality
  - Color, FontStyle, Style tests
  - SyntaxSet, ThemeSet tests
  - Highlighter tests
  - ParseState, Scope, ScopeStack tests
  - Output utility tests
  - Dump utility tests
  - Error type tests
  - ClassStyle, IncludeBg tests

- **Examples**:
  - `basic_highlight.py` - Basic syntax highlighting
  - `advanced_highlight.py` - Advanced parsing, themes, and output
  - `benchmark.py` - Performance benchmarking

## Architecture

### Module Structure
```
pyext/
├── Cargo.toml              # PyO3 extension crate
├── pyproject.toml          # maturin configuration
├── syntect.pyi             # Type stubs
├── src/
│   ├── lib.rs              # Module entry point
│   ├── errors.rs           # Custom exception types
│   ├── style.rs            # Color, FontStyle, Style, StyleModifier (with getters)
│   ├── syntax_set.rs       # SyntaxSet, SyntaxReference, SyntaxSetBuilder
│   ├── theme_set.rs        # ThemeSet, Theme, ThemeSettings, ThemeItem (with real style data)
│   ├── highlighter.rs      # Highlighter, HighlightState (uses convenience::PyHighlightResult)
│   ├── convenience.rs      # PyHighlightResult with output methods
│   ├── parse_state.rs      # ParseState, ScopeStack, Scope, ScopeStackOp
│   ├── html.rs             # CSS, HTML output, ClassStyle, IncludeBg
│   ├── util.rs             # Terminal, LaTeX, HTML output utilities
│   ├── dumps.rs            # Dump load/save utilities
│   └── converters.rs       # Shared conversion helpers (stub)
├── tests/
│   └── test_syntect.py     # 36 pytest tests
└── examples/
    ├── basic_highlight.py  # Basic syntax highlighting
    ├── advanced_highlight.py  # Advanced parsing and themes
    └── benchmark.py        # Performance benchmarking
```

### API Surface

#### High-Level API
```python
import syntect

# Quick highlight with convenience methods
result = syntect.highlight_string(
    code="fn main() {}",
    syntax="Rust",
    theme="base16-ocean.dark"
)
print(result.tokens)       # [(PyStyle, text), ...]
print(result.html)         # HTML output

# Convert result to different formats
html = result.as_html("if_different")
escaped = result.as_terminal_escaped(True)
latex = result.as_latex_escaped()

# Terminal output
tokens = hl.highlight_line("fn main() {}", ss, ts)
escaped = syntect.as_terminal_escaped(tokens, True)
# \x1b[38;2;180;142;173mfn\x1b[38;2;192;197;206m ...

# HTML output
html = syntect.as_html(tokens, "if_different")
# <span style="background-color:#2B303B;color:#B48EAD;">fn</span>...

# LaTeX output
latex = syntect.as_latex_escaped(tokens)
# \textcolor[RGB]{180,142,173}{fn}\textcolor[RGB]{192,197,206}{ }...

# Full HTML with line numbers
full_html = syntect.highlighted_html_for_string_py(
    code="fn main() {}",
    syntax_ref=rust,
    theme=theme,
    syntax_set=ss,
    theme_set=ts
)
# <pre style="background-color:#2b303b;">...</pre>

# CSS for theme
css = syntect.css_for_theme(theme, "spaced")
# /* theme "Base16 Ocean Dark" generated by syntect */
# .code { color: #C0C5CE; background-color: #2B303B; }
# .source .rust { color: #8FA1B3; }
# ...
```

#### Class-Based API
```python
# Load syntax set and theme set
ss = syntect.SyntaxSet.load_defaults()
ts = syntect.ThemeSet.load_defaults()

# Custom syntax loading
builder = syntect.SyntaxSetBuilder()
builder.add_from_folder("/path/to/syntaxes", False)
ss = builder.build()

# Get syntax and theme
rust = ss.find_syntax_by_name("Rust")
theme = ts.get_theme("base16-ocean.dark")

# Create highlighter and highlight
hl = syntect.Highlighter(rust, theme)
tokens = hl.highlight_line("fn main() {", ss, ts)
# Returns: [(PyStyle(fg=#B48EAD, bg=#2B303B, font=0), "fn"), ...]

# Parse a line
parse_state = syntect.ParseState("Rust")
output = parse_state.parse_line("fn main() {", ss)
# ops: [(0, "Push(source.rust)"), (0, "Push(meta.function.rust)"), ...]

# Access style properties
for style, text in tokens:
    print(f"{style.foreground.to_hex()} {style.background.to_hex()} {style.font_style.bits} | {text}")

# ThemeItem with real style data
for item in theme.scopes:
    print(f"{item.scope}: fg={item.foreground}, bg={item.background}, font={item.font_style}")
```

## Build Configuration

### Cargo.toml (pyext/Cargo.toml)
```toml
[package]
name = "syntect-py"
version = "5.3.0"

[lib]
name = "syntect"
crate-type = ["cdylib"]

[dependencies]
syntect = { path = "..", features = [
    "parsing",
    "yaml-load",
    "plist-load",
    "dump-load",
    "dump-create",
    "regex-fancy",
    "metadata",
    "html",
    "default-syntaxes",
    "default-themes",
] }
pyo3 = { version = "0.29", features = ["macros", "abi3-py39"] }
```

### Key Design Decisions
- **Regex engine:** fancy-regex (pure Rust, no C library dependency)
- **PyO3 version:** 0.29
- **Python version:** 3.9+ (ABI3)
- **Build system:** maturin
- **Ownership model:** Python objects own data, Rust borrows during method calls
- **Token format:** `(PyStyle, str)` tuples with real color/font data
- **Type stubs:** `syntect.pyi` for IDE autocomplete

## Known Issues & Limitations

### Current Limitations
1. `HighlightState` serialization is a stub - stores syntax name but not real highlighting state
2. `PyHighlightState.single_caches_json` and `styles_json` are stub fields (empty strings)

### Warnings
- None! All warnings cleaned up in Phase 6
- No deprecation warnings (all `#[pyclass]` types use `skip_from_py_object` or `from_py_object`)
- No unused imports or variables

## Test Results

### pytest Results
```
50 passed in 0.67s
```

### Test Coverage
- Core types (Color, FontStyle, Style, StyleModifier)
- SyntaxSet, SyntaxReference, SyntaxSetBuilder
- ThemeSet, Theme, ThemeSettings, ThemeItem
- Highlighter, ParseState, Scope, ScopeStack, ScopeStackOp
- Output utilities (terminal, HTML, LaTeX, CSS)
- Dump utilities (load/save roundtrip)
- Error types
- ClassStyle, IncludeBg enums
- Integration: full pipeline, file highlighting, CSS, dump roundtrips
- Integration: ThemeItem.style, ThemeSettings colors, ParseLineOutput ops
- Integration: all output formats, file extension detection, Style equality

## Version History

### v5.3.0-py0 (Phase 0)
- Initial PyO3 0.23 setup
- Stub implementations for all types
- Basic module structure

### v5.3.0-py1 (Phase 1)
- Upgraded to PyO3 0.29
- Proper conversions from syntect types
- Real highlighting engine integration
- All core types working

### v5.3.0-py2 (Phase 2)
- Added `SyntaxSetBuilder` wrapper class
- Implemented `add_from_folder` for SyntaxSet and ThemeSet
- Implemented `load_from_folder` static method
- Implemented `into_builder` for extending loaded SyntaxSets
- Implemented `find_syntax_by_scope`
- Added custom error types (LoadingError, ParsingError, DumpError)
- Implemented real dump save/load for SyntaxSet and ThemeSet
- Renamed all Py*-prefixed classes to clean Python names
- Added gutter settings to ThemeSettings

### v5.3.0-py3 (Phase 3)
- Real `Highlighter` with colored token output using real `syntect::highlighting::Style`
- Real `ParseState` with full `syntect::parsing::ParseState` integration
- Real `ParseLineOutput` with ops, replayed, and warnings
- Real `Scope` with `from_string`, `to_string`, `len`, `is_prefix_of`
- Real `ScopeStack` with `push`, `pop`, `apply`, `as_string`
- Real `ScopeStackOp` with push, pop, clear, restore, noop operations
- Real `HighlightState` with syntax name and theme key storage
- Theme key stored in `PyTheme` for proper `Highlighter` lookup
- `highlight_line` and `highlight_lines` now take `theme_set` parameter
- Tokens return real `PyStyle` objects instead of formatted strings

### v5.3.0-py4 (Phase 4)
- **Terminal escape:** `as_terminal_escaped()` returns 24-bit ANSI escape sequences with proper alpha blending
- **HTML output:** `as_html()` returns inline-styled HTML, merging adjacent same-style tokens
- **LaTeX output:** `as_latex_escaped()` returns `\textcolor[RGB]{...}{...}` with proper escaping
- **CSS generation:** `css_for_theme()` uses syntect's real CSS generation
- **Full HTML:** `highlighted_html_for_string_py()` uses syntect's real HTML generation
- **Line numbers:** `highlighted_html_at_line_and_column_number()` adds `data-line` attributes
- **ClassStyle enum:** `spaced()`, `spaced_prefixed()`, `class_attribute()`
- **IncludeBg enum:** `no()`, `yes()`, `if_different()`
- **PyStyle getters:** `foreground`, `background`, `font_style` exposed to Python
- **PyFontStyle getter:** `bits` exposed to Python
- **PyColor getters:** `r`, `g`, `b`, `a` exposed to Python

### v5.3.0-py5 (Phase 5)
- **Enhanced HighlightResult** with `as_html()`, `as_terminal_escaped()`, `as_latex_escaped()` methods
- **ThemeItem** with real `foreground`, `background`, `font_style` data
- **Style.from_hex_styles()** - Static factory for creating styles
- **Style.__eq__** - Equality comparison
- **Color.from_hex()** - Parse hex color strings
- **FontStyle bitwise operations** - `|`, `&`, `^`, `~`
- **Type stubs** - `syntect.pyi` with complete type hints
- **Tests** - 36 pytest tests covering all functionality
- **Examples** - Basic highlighting, advanced parsing, benchmarking

### v5.3.0-py6 (Phase 6)
- **StyleModifier** - Added Python-accessible getters for `foreground`, `background`, `font_style`
- **css_for_theme** - Now uses real theme scopes instead of empty stub
  - Parses scope strings from PyThemeItem into proper ScopeSelectors
  - Generates valid CSS with scope selectors
- **highlight_string** - Fixed terminal output to use real escape sequences
- **HighlightState** - Added getters for `styles_json`, `single_caches_json`, `path_scope_string`
- **find_syntax_for_file** - Fixed to return None for unknown files instead of throwing error
- **SyntaxReference.hidden** - Property verified working
- **Deprecation warnings** - All `#[pyclass]` types now use `skip_from_py_object` or `from_py_object`
  - Types creatable from Python use `from_py_object` (Color, FontStyle, Style, StyleModifier)
  - Types not creatable from Python use `skip_from_py_object` (all others)
- **Cleaned up all warnings**:
  - Removed unused imports (BufRead, SyntectColor, etc.)
  - Removed unused functions (syntect_color_to_py, syntect_font_style_to_py)
  - Added `#[allow(unused_assignments)]` where needed
  - Fixed move errors with `.clone()` on PyColor fields
- **Zero warnings** - Build produces clean output with no warnings

### v5.3.0-py7 (Phase 7)
- **ThemeItem.style** - Added `style` property returning `StyleModifier` object
- **ThemeSettings** - All color properties now return `Color` objects instead of hex strings
  - `foreground`, `background`, `selection_background`, `gutter_foreground`, `gutter_background`
- **ParseLineOutput** - Added `get_scope_stack_op(index)` and `get_op_type(index)` methods
- **converters.rs** - Real conversion module with:
  - `syntect_style_to_py`, `syntect_color_to_py`, `syntect_font_style_to_py`
  - `py_color_to_syntect`, `py_font_style_to_syntect`, `py_style_to_syntect`
  - `default_font_style`, `font_style_from_bits`

### v5.3.0-py8 (Phase 8)
- **Highlighter.highlight_file(path)** - Highlight all lines in a file
  - Reads file content and highlights each line
  - Returns `Vec<Vec<(PyStyle, String)>>` (one token list per line)
- **LinesWithEndings** - `split_lines_with_endings()` helper function
  - Splits content into lines with ending characters (`\n`, `\r\n`, `\r`, or empty)
  - Handles all line ending types correctly

### v5.3.0-py9 (Phase 9)
- **generate_css** - Alias for `css_for_theme`
- **create_html_file** - Alias for `highlighted_html_for_string_py`
- **SyntaxSet.from_dump(path)** - Load SyntaxSet from .packdump file
- **SyntaxSet.to_dump(path)** - Save SyntaxSet to .packdump file
- **ThemeSet.from_dump(path)** - Load ThemeSet from .themedump file
- **ThemeSet.to_dump(path)** - Save ThemeSet to .themedump file

### v5.3.0-py10 (Phase 10)
- **Examples** - 7 example scripts:
  - `basic_highlight.py` - Basic syntax highlighting
  - `advanced_highlight.py` - Advanced parsing and themes
  - `benchmark.py` - Performance benchmarking
  - `highlight_file.py` - Highlight a file to terminal
  - `highlight_html.py` - Highlight code to full HTML file
  - `incremental.py` - Demonstrate incremental highlighting state
  - `css_generator.py` - Generate CSS from theme
- **Integration tests** - 14 integration tests covering:
  - Full highlight pipeline
  - File highlighting
  - CSS generation
  - Dump roundtrips
  - ThemeItem.style and ThemeSettings colors
  - ParseLineOutput ops
  - All output formats
  - File extension detection
  - Style equality and FontStyle bitwise ops
- **Total tests: 50** (36 unit + 14 integration)
- **Zero warnings** - Build produces clean output

---

*Last updated: 2026-06-30*
