# PyO3 Implementation Status

## Overview
Python bindings for syntect's syntax highlighting library using PyO3 0.29.

## Completed Phases

### ✅ Phase 0: Foundation (COMPLETE)
**Status:** Build succeeds, module imports correctly

**What was built:**
- `pyext/` sub-crate with PyO3 0.29 bindings
- 11 source files with stub implementations
- maturin build configuration
- Feature flags for minimal build

**Files created:**
```
pyext/
├── Cargo.toml
├── pyproject.toml
└── src/
    ├── lib.rs
    ├── style.rs
    ├── syntax_set.rs
    ├── theme_set.rs
    ├── highlighter.rs
    ├── parse_state.rs
    ├── html.rs
    ├── util.rs
    ├── dumps.rs
    └── converters.rs
```

**Verified working:**
- Module imports: `import syntect` ✅
- `SyntaxSet.load_defaults()` - 192 syntaxes loaded ✅
- `ThemeSet.load_defaults()` - 7 themes loaded ✅
- Basic type constructors ✅

---

### ✅ Phase 1: Core Types (COMPLETE)
**Status:** All core types properly convert from syntect's internal types

**What was implemented:**
- `Color` - RGBA color with hex conversion
- `FontStyle` - Bold/Italic/Underline with bitwise operations
- `Style` - Foreground/background/font style
- `StyleModifier` - Partial style changes
- `SyntaxSet` - Syntax set with find methods
- `SyntaxReference` - Syntax reference wrapper
- `ThemeSet` - Theme set with theme lookup
- `Theme` - Theme with settings and scopes
- `ThemeSettings` - Theme default colors
- `ThemeItem` - Theme scope rules
- `Highlighter` - Real highlighting using syntect's `HighlightLines`
- `Scope` - Scope string wrapper
- `ScopeStack` - Scope stack management
- `ParseState` - Parser state stub

**Key improvements over Phase 0:**
- All wrapper types now properly extract data from syntect's internal types
- `Highlighter` actually highlights code using syntect's `HighlightLines`
- `highlight_string()` and `highlight_line()` return real syntect-style tokens
- Tokens include actual foreground/background colors from the theme

**Verified working:**
```python
# Real highlighting results
tokens = hl.highlight_line("fn main() {", ss)
# Returns: [(Style { fg: Color{...}, bg: Color{...}, ... }, "fn"), ...]
```

---

### ✅ Phase 2: Loading Infrastructure (COMPLETE)
**Status:** All loading infrastructure implemented

**What was implemented:**
- `SyntaxSetBuilder` - Full wrapper around syntect's `SyntaxSetBuilder`
  - `add_from_folder(path, lines_include_newline)` - Load .sublime-syntax files
  - `add_plain_text_syntax()` - Add plain text syntax
  - `build()` - Build final SyntaxSet
  - `warnings()` - Get loading warnings
- `SyntaxSet.add_from_folder` via `SyntaxSetBuilder` pattern
- `SyntaxSet.load_from_folder(path, lines_include_newline)` - Static convenience method
- `SyntaxSet.into_builder()` - Convert SyntaxSet back to builder for extension
- `ThemeSet.add_from_folder(path)` - Load .tmTheme files from folder
- `find_syntax_by_scope(scope_string)` - Find syntax by scope string
- Custom error types: `LoadingError`, `ParsingError`, `DumpError`
- Real dump save/load: `dump_syntax_set()`, `load_syntax_set()`, `dump_theme_set()`, `load_theme_set()`

**Files modified:**
```
pyext/src/
├── lib.rs              # Added error type registration, renamed classes
├── syntax_set.rs       # Added SyntaxSetBuilder, load_from_folder, into_builder, find_syntax_by_scope
├── theme_set.rs        # Added add_from_folder, gutter settings, theme key
├── dumps.rs            # Real dump load/save using syntect's serialization
├── errors.rs           # NEW: Custom exception types
├── style.rs            # Renamed classes (PyColor → Color, etc.)
├── highlighter.rs      # Renamed classes
├── parse_state.rs      # Renamed classes
```

**Verified working:**
```python
# Builder pattern
builder = syntect.SyntaxSetBuilder()
warnings = builder.add_from_folder("/path/to/syntaxes", False)
ss = builder.build()

# Static convenience
ss = syntect.SyntaxSet.load_from_folder("/path/to/syntaxes", False)

# Extension
ss = syntect.SyntaxSet.load_defaults()
builder = ss.into_builder()
builder.add_from_folder("/custom/syntaxes", False)
ss = builder.build()

# Dump/load round-trip
syntect.dump_syntax_set(ss, "syntaxes.packdump")
ss = syntect.load_syntax_set("syntaxes.packdump")

# Error types
try:
    syntect.load_syntax_set("nonexistent.packdump")
except syntect.DumpError:
    pass
```

---

### ✅ Phase 3: Highlighting Engine (COMPLETE)
**Status:** All highlighting engine types implemented with real syntect integration

**What was implemented:**

#### `PyHighlighter` (real implementation)
- `highlight_line(line, syntax_set, theme_set)` - Returns colored tokens with real `syntect::highlighting::Style`
- `highlight_lines(code, syntax_set, theme_set)` - Multi-line highlighting
- Real theme lookup using `theme.key` (map key, not display name)
- `save_state()` - Returns `HighlightState`
- `from_state(state, theme)` - Static factory for state restoration

#### `PyHighlightState` (real implementation)
- Stores syntax name and theme key for state restoration
- Ready for full `syntect::highlighting::HighlightState` serialization

#### `PyParseState` (real implementation)
- `parse_line(line, syntax_set)` - Returns real `ParseLineOutput` with scope stack operations
- `is_speculative()` - Check if parser is in branch mode
- Full integration with `syntect::parsing::ParseState`

#### `PyParseLineOutput` (real implementation)
- `ops` - List of (position, operation_string) tuples
- `replayed` - Cross-line fail replay operations
- `warnings` - Parser warnings (e.g., branch point expiry)

#### `PyScope` (real implementation)
- `from_string(scope_string)` - Parse scope from string
- `to_string()` - Convert to string representation
- `len()` - Number of atoms in scope
- `is_empty()` - Check if scope is empty
- `is_prefix_of(other)` - Check prefix relationship
- `__eq__` - Equality comparison

#### `PyScopeStack` (real implementation)
- `push(scope)` - Push scope onto stack
- `pop()` - Pop scope from stack
- `apply(op)` - Apply `ScopeStackOp`
- `as_string()` - Space-separated scope string
- `len()` / `is_empty()` - Stack size checks

#### `PyScopeStackOp` (real implementation)
- `push(scope)` - Create Push operation
- `pop(count)` - Create Pop operation
- `clear_all()` / `clear_top(n)` - Create Clear operations
- `restore()` - Create Restore operation
- `noop()` - Create Noop operation

**Files modified:**
```
pyext/src/
├── highlighter.rs      # Real Highlighter with colored output, HighlightState
├── parse_state.rs      # Real ParseState, ParseLineOutput, ScopeStack, ScopeStackOp, Scope
├── theme_set.rs        # Added theme key for Highlighter lookup
└── style.rs            # Made PyFontStyle.bits public
```

**Verified working:**
```python
# Real colored highlighting
hl = syntect.Highlighter(rust, theme)
tokens = hl.highlight_line("fn main() {", ss, ts)
# Returns: [(Style(fg=#B48EAD, bg=#2B303B, font=0), "fn"), ...]

# Real parsing
parse_state = syntect.ParseState("Rust")
output = parse_state.parse_line("fn main() {", ss)
# ops: [(0, "Push(source.rust)"), (0, "Push(meta.function.rust)"), ...]

# Real scope stack
stack = syntect.ScopeStack()
stack.push(syntect.Scope("source.rust"))
stack.push(syntect.Scope("keyword"))
# "source.rust keyword"
```

---

### 🔄 Phase 4: Output Utilities (NOT STARTED)
**TODO:**
- [ ] `as_terminal_escaped` - 24-bit ANSI escape sequences
- [ ] `as_html` - HTML with inline styles
- [ ] `as_latex_escaped` - LaTeX \textcolor output
- [ ] `css_for_theme` - CSS generation
- [ ] `highlighted_html_for_string` - Full HTML output
- [ ] `highlighted_html_at_line_and_column_number` - Line numbers

**Current status:** All output functions return stub/simplified output

---

### 🔄 Phase 5: Convenience & Polish (NOT STARTED)
**TODO:**
- [ ] `HighlightResult` dataclass (combines tokens, HTML, terminal)
- [ ] Exception types (LoadingError, ParsingError, etc.)
- [ ] Documentation and type stubs (.pyi)
- [ ] Tests (pytest)
- [ ] Example Python scripts
- [ ] Benchmark comparison with pure Python highlighters

---

## Architecture

### Module Structure
```
pyext/
├── Cargo.toml              # PyO3 extension crate
├── pyproject.toml          # maturin configuration
└── src/
    ├── lib.rs              # Module entry point
    ├── errors.rs           # Custom exception types
    ├── style.rs            # Color, FontStyle, Style, StyleModifier
    ├── syntax_set.rs       # SyntaxSet, SyntaxReference, SyntaxSetBuilder
    ├── theme_set.rs        # ThemeSet, Theme, ThemeSettings, ThemeItem
    ├── highlighter.rs      # Highlighter, HighlightState, HighlightResult
    ├── parse_state.rs      # ParseState, ScopeStack, Scope, ScopeStackOp
    ├── html.rs             # HTML output utilities
    ├── util.rs             # Terminal, LaTeX, CSS utilities
    ├── dumps.rs            # Dump load/save utilities
    └── converters.rs       # Shared conversion helpers (stub)
```

### API Surface

#### High-Level API
```python
import syntect

# Quick highlight
result = syntect.highlight_string(
    code="fn main() {}",
    syntax="Rust",
    theme="base16-ocean.dark"
)
print(result.tokens)       # [(Style, text), ...]
print(result.html)         # HTML output
print(result.terminal_escaped)  # ANSI escape string
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
# Returns colored tokens: [(Style(fg=#B48EAD, bg=#2B303B, font=0), "fn"), ...]

# Parse a line
parse_state = syntect.ParseState("Rust")
output = parse_state.parse_line("fn main() {", ss)
print(output.ops)  # [(0, "Push(source.rust)"), (0, "Push(meta.function.rust)"), ...]
```

---

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

---

## Known Issues & Limitations

### Current Limitations
1. `HighlightState` serialization not fully implemented (stub)
2. Output utilities (terminal, HTML, LaTeX, CSS) return stub/simplified output
3. `ScopeStack` doesn't track `clear_scopes` state (clear_stack not exposed)

### Warnings
- `#[pyclass]` with `Clone` triggers deprecation warning (PyO3 0.29)
- Unused imports in style.rs (Color, FontStyle, etc.)
- Unused variables in html.rs
- `PyStyleModifier` fields never read
- `PyHighlightState.single_caches_json` never read

---

## Next Steps

### Immediate (Phase 4)
1. Implement `as_terminal_escaped` - 24-bit ANSI escape sequences
2. Implement `as_html` - HTML with inline styles
3. Implement `as_latex_escaped` - LaTeX output
4. Implement `css_for_theme` - CSS generation
5. Implement `highlighted_html_for_string` - Full HTML output

### Medium-term (Phase 5)
1. Add comprehensive tests
2. Add type stubs
3. Add documentation
4. Benchmark against pure Python highlighters

---

## Files Modified in Phase 3

### Updated Files
- `pyext/src/highlighter.rs` - Real Highlighter with colored output, HighlightState
- `pyext/src/parse_state.rs` - Real ParseState, ParseLineOutput, ScopeStack, ScopeStackOp, Scope
- `pyext/src/theme_set.rs` - Added theme key for Highlighter lookup
- `pyext/src/style.rs` - Made PyFontStyle.bits public

### Build Commands
```bash
# Build
cd pyext && maturin build --release

# Install
pip install --force-reinstall target/wheels/syntect-5.3.0-cp39-abi3-win_amd64.whl

# Test
python -c "import syntect; print(dir(syntect))"
```

---

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
- Real `PyHighlighter` with colored token output using real `syntect::highlighting::Style`
- Real `PyParseState` with full `syntect::parsing::ParseState` integration
- Real `PyParseLineOutput` with ops, replayed, and warnings
- Real `PyScope` with `from_string`, `to_string`, `len`, `is_prefix_of`
- Real `PyScopeStack` with `push`, `pop`, `apply`, `as_string`
- Real `PyScopeStackOp` with push, pop, clear, restore, noop operations
- Real `PyHighlightState` with syntax name and theme key storage
- Theme key stored in `PyTheme` for proper `Highlighter` lookup
- `highlight_line` and `highlight_lines` now take `theme_set` parameter

---

*Last updated: 2026-06-30*
