# PyO3 Python Bindings Implementation Plan

## Overview

Add PyO3 bindings to expose syntect's syntax highlighting capabilities to Python.
This plan covers the module architecture, class design, API surface, and implementation order.

## Design Decisions

### 1. Regex Engine Choice
**Recommendation: `fancy-regex` (pure Rust)**
- Avoids the Oniguruma C library dependency (oniguruma requires libonig, causing build issues on Windows)
- Pure Rust = simpler cross-compilation, no system library requirements
- Trade-off: ~2x slower than oniguruma, but still fast enough for Python use
- Can be made a feature flag so users can choose

### 2. Ownership Model
- Python objects **own** their underlying data (strings, syntax set, theme set)
- Rust borrows from Python objects during method calls
- `SyntaxSet` and `ThemeSet` are expensive to create → cache them in Python objects
- Use `#[pyclass]` / `#[pyfunction]` with `&self` for most methods

### 3. Feature Flags
The PyO3 build will use a **minimal feature set** to keep the binary small:
```
features = ["parsing", "yaml-load", "dump-load", "dump-create", "fancy-regex", "metadata", "plist-load"]
```
- `default-syntaxes` / `default-themes`: **Optional** — includes embedded dumps (~200KB each).
  Can be toggled via a separate feature `pyo3-embedded-assets` for users who want zero-config defaults.
- `html`: **Included** — for `highlight_to_html` output
- `dump-load` / `dump-create`: **Included** — for loading/saving `.packdump` and `.themedump`

### 4. Threading
- `SyntaxSet` is `Send + Sync` — safe to share across Python threads
- `Highlighter` / `ParseState` are **not** thread-safe — each highlight call gets its own state
- The Python `SyntaxSet` wrapper can be shared; `Highlighter` is created per-call

### 5. Error Handling
- Rust `Error` types → Python exceptions via PyO3's `thiserror` integration
- `LoadingError` → `syntect.LoadingError`
- `ParsingError` → `syntect.ParsingError`
- `DumpError` → `syntect.DumpError`

---

## Module Architecture

```
src/
├── lib.rs                    # Main entry point (existing Rust library)
├── pymod/                    # NEW: PyO3 bindings
│   ├── mod.rs                # Module definition, PyO3 bootstrap
│   ├── syntax_set.rs         # SyntaxSet, SyntaxReference
│   ├── theme_set.rs          # ThemeSet, Theme, ThemeSettings
│   ├── style.rs              # Style, Color, FontStyle, StyleModifier
│   ├── highlighter.rs        # Highlighter, HighlightLines, HighlightState
│   ├── parse_state.rs        # ParseState, ParseLineOutput, ScopeStack
│   ├── html.rs               # HTML output utilities
│   ├── util.rs               # Terminal escape, LaTeX, LinesWithEndings
│   ├── dumps.rs              # Dump load/save utilities
│   └── converters.rs         # Shared Py↔Rust type conversions
```

---

## Cargo.toml Changes

Add PyO3 dependency and build configuration:

```toml
[features]
# ... existing features ...

# PyO3 bindings feature
pyo3 = ["dep:pyo3"]

# Embedded default assets (optional, for zero-config Python usage)
pyo3-embedded-assets = ["default-syntaxes", "default-themes"]

[dependencies]
pyo3 = { version = "0.23", optional = true, features = ["module"] }

[build-dependencies]
pyo3-build-config = { version = "0.23", optional = true }

# NEW: PyO3 library target
[lib]
name = "syntect"
# Keep existing lib target

# NEW: PyO3 extension module (separate target)
[[bin]]
name = "syntect"
path = "src/pymod/main.rs"

# Or better: use pyo3's native module approach
```

**Recommended approach**: Use `maturin` or `pyo3`'s `cargo check --lib` approach with a **separate crate** or **feature-gated module**:

```toml
[lib]
name = "syntect"

# Feature-gated PyO3 module
[dependencies.pyo3]
optional = true
features = ["module", "py312"]  # or detect at build time
```

### Recommended: Separate `pyo3` crate in workspace

```
Cargo.toml (workspace root)
├── Cargo.toml (syntect library)
└── pyext/
    ├── Cargo.toml (pyo3 extension module)
    └── src/
        ├── lib.rs (PyO3 module entry)
        └── ... (same as pymod/ above)
```

This avoids polluting the main `Cargo.toml` with PyO3-specific config and lets `maturin` handle the build.

---

## API Surface Design

### High-Level (Convenience Functions)

```python
import syntect

# Quick highlight with defaults
result = syntect.highlight_string(
    code="fn main() { println!(\"hi\"); }",
    syntax="Rust",
    theme="base16-ocean.dark"
)
print(result.terminal_escaped)   # ANSI escape string
print(result.html)               # HTML with inline styles
print(result.tokens)             # List of (Style, text) tuples

# Or use the class-based API for caching
ss = syntect.SyntaxSet(load_defaults=True)
ts = syntect.ThemeSet(load_defaults=True)
theme = ts.get_theme("base16-ocean.dark")
hl = syntect.Highlighter(ss, theme)

for line in code.split("\n"):
    tokens = hl.highlight_line(line, ss)
    # tokens: list of (Style, text)
```

### Class-Based API

#### `SyntaxSet`
```python
class SyntaxSet:
    def __init__(self):
        """Create empty syntax set."""
    
    @staticmethod
    def load_defaults(newlines: bool = True) -> "SyntaxSet":
        """Load default syntax set from embedded dump."""
    
    def add_from_folder(self, path: str) -> None:
        """Load .sublime-syntax files from a directory."""
    
    def find_syntax_by_extension(self, ext: str) -> Optional[SyntaxReference]:
        """Find syntax by file extension, e.g. 'rs' → Rust."""
    
    def find_syntax_by_name(self, name: str) -> Optional[SyntaxReference]:
        """Find syntax by name, e.g. 'Rust'."""
    
    def find_syntax_by_scope(self, scope: str) -> Optional[SyntaxReference]:
        """Find syntax by scope, e.g. 'source.rust'."""
    
    def find_syntax_for_file(self, path: str) -> Optional[SyntaxReference]:
        """Auto-detect syntax from file path."""
    
    def find_syntax_plain_text(self) -> SyntaxReference:
        """Get plain text syntax (fallback)."""
    
    def syntaxes(self) -> List[SyntaxReference]:
        """Get all syntax references."""
    
    @staticmethod
    def from_dump(path: str) -> "SyntaxSet":
        """Load from .packdump file."""
    
    def to_dump(self, path: str) -> None:
        """Save to .packdump file."""
```

#### `SyntaxReference`
```python
class SyntaxReference:
    @property
    def name(self) -> str: ...
    @property
    def file_extensions(self) -> List[str]: ...
    @property
    def scope(self) -> str: ...
    @property
    def hidden(self) -> bool: ...
```

#### `ThemeSet`
```python
class ThemeSet:
    def __init__(self):
        """Create empty theme set."""
    
    @staticmethod
    def load_defaults() -> "ThemeSet":
        """Load default themes from embedded dump."""
    
    def add_from_folder(self, path: str) -> None:
        """Load .tmTheme files from a directory."""
    
    def get_theme(self, name: str) -> Optional[Theme]:
        """Get theme by name."""
    
    def theme_names(self) -> List[str]:
        """List all available theme names."""
    
    @staticmethod
    def from_dump(path: str) -> "ThemeSet":
        """Load from .themedump file."""
    
    def to_dump(self, path: str) -> None:
        """Save to .themedump file."""
```

#### `Theme`
```python
class Theme:
    @property
    def name(self) -> str: ...
    @property
    def author(self) -> str: ...
    @property
    def settings(self) -> ThemeSettings: ...
    @property
    def scopes(self) -> List[ThemeItem]: ...
```

#### `ThemeSettings`
```python
class ThemeSettings:
    @property
    def foreground(self) -> Optional[Color]: ...
    @property
    def background(self) -> Optional[Color]: ...
    # ... other settings ...
```

#### `ThemeItem`
```python
class ThemeItem:
    @property
    def scope(self) -> str: ...
    @property
    def style(self) -> StyleModifier: ...
```

#### `Style` (dataclass-like)
```python
@dataclass
class Style:
    foreground: Color
    background: Color
    font_style: FontStyle
```

#### `Color` (dataclass-like)
```python
@dataclass
class Color:
    r: int  # 0-255
    g: int
    b: int
    a: int  # 0-255 (alpha)
    
    @staticmethod
    def from_hex(hex_str: str) -> "Color":
        """Create from hex string like '#FF0000' or 'FF0000'."""
    
    def to_hex(self) -> str:
        """Export as hex string like '#FF0000'."""
```

#### `FontStyle` (enum-like)
```python
class FontStyle:
    BOLD = ...
    ITALIC = ...
    UNDERLINE = ...
    
    # Bitwise operations
    def __or__(self, other) -> FontStyle: ...
    def __and__(self, other) -> FontStyle: ...
```

#### `Highlighter`
```python
class Highlighter:
    def __init__(self, syntax: SyntaxReference, theme: Theme):
        """Create a highlighter for a syntax + theme combination."""
    
    def highlight_line(self, line: str, syntax_set: SyntaxSet) -> List[Tuple[Style, str]]:
        """Highlight a single line. Returns list of (Style, text) tuples."""
    
    def highlight_file(self, path: str, syntax_set: SyntaxSet) -> Iterator[List[Tuple[Style, str]]]:
        """Highlight all lines in a file."""
    
    def save_state(self) -> HighlightState:
        """Save current parse/highlight state for incremental highlighting."""
    
    @staticmethod
    def from_state(state: HighlightState, theme: Theme) -> "Highlighter":
        """Create from saved state."""
```

#### `HighlightState`
```python
class HighlightState:
    # Serializable state for incremental highlighting
    pass
```

#### `ParseState`
```python
class ParseState:
    def __init__(self, syntax: SyntaxReference):
        """Create parser state for a syntax."""
    
    def parse_line(self, line: str, syntax_set: SyntaxSet) -> ParseLineOutput:
        """Parse a line, returning scope stack operations."""
    
    def is_speculative(self) -> bool:
        """Check if parser is in speculative (branch) mode."""
```

#### `ParseLineOutput`
```python
class ParseLineOutput:
    @property
    def ops(self) -> List[Tuple[int, ScopeStackOp]]: ...
    @property
    def replayed(self) -> List[List[Tuple[int, ScopeStackOp]]]: ...
    @property
    def warnings(self) -> List[str]: ...
```

#### `ScopeStack`
```python
class ScopeStack:
    @staticmethod
    def from_string(s: str) -> "ScopeStack":
        """Parse scope string like 'source.rust keyword.operator'."""
    
    def apply(self, op: ScopeStackOp) -> None: ...
    
    def as_string(self) -> str: ...
    
    def len(self) -> int: ...
```

#### `ScopeStackOp`
```python
class ScopeStackOp:
    @staticmethod
    def push(scope: Scope) -> "ScopeStackOp": ...
    @staticmethod
    def pop(count: int) -> "ScopeStackOp": ...
```

#### `Scope`
```python
class Scope:
    @staticmethod
    def from_string(s: str) -> "Scope":
        """Parse scope string like 'source.rust'."""
    
    def to_string(self) -> str: ...
    def len(self) -> int: ...
    def is_prefix_of(self, other: "Scope") -> bool: ...
```

### Utility Functions (module-level)

```python
def highlight_string(
    code: str,
    syntax: Union[str, SyntaxReference],
    theme: Union[str, Theme],
    syntax_set: SyntaxSet,
    theme_set: ThemeSet
) -> HighlightResult:
    """Quick highlight with auto-loading of syntax/theme."""

def as_terminal_escaped(tokens: List[Tuple[Style, str]], include_bg: bool = True) -> str:
    """Convert tokens to 24-bit ANSI escape sequence string."""

def as_html(tokens: List[Tuple[Style, str]], include_bg: str = "if_different") -> str:
    """Convert tokens to HTML with inline styles."""

def as_latex(tokens: List[Tuple[Style, str]]) -> str:
    """Convert tokens to LaTeX \\textcolor output."""

def generate_css(theme: Theme, class_style: str = "spaced") -> str:
    """Generate CSS for a theme."""

def create_html_file(
    code: str,
    syntax: SyntaxReference,
    theme: Theme,
    syntax_set: SyntaxSet
) -> str:
    """Create full highlighted HTML <pre> block."""
```

---

## Implementation Phases

### Phase 0: Foundation (Setup)
1. Create `pyext/` sub-crate with its own `Cargo.toml`
2. Add PyO3 dependency and build configuration
3. Set up `pyproject.toml` for maturin
4. Configure feature flags for PyO3 build profile
5. Create basic module skeleton that compiles and imports

### Phase 1: Core Types (Data Classes)
1. `Color` — simple data class, from/to hex
2. `FontStyle` — enum with bitwise ops
3. `Style` — data class composed of Color + FontStyle
4. `StyleModifier` — optional Style changes
5. `Scope` — wrapper around internal Scope type
6. `SyntaxReference` — read-only wrapper

### Phase 2: Loading Infrastructure
1. `SyntaxSet` — load defaults, add from folder, find syntax
2. `SyntaxSet` dump save/load
3. `ThemeSet` — load defaults, add from folder, get theme
4. `ThemeSet` dump save/load
5. `Theme` — read-only wrapper
6. `ThemeSettings` — read-only wrapper

### Phase 3: Highlighting Engine
1. `Highlighter` — the core highlighting class
2. `HighlightState` — state management for incremental highlighting
3. `ParseState` — parser state wrapper
4. `ParseLineOutput` — parse result wrapper
5. `ScopeStack` / `ScopeStackOp` — scope stack management

### Phase 4: Output Utilities
1. Terminal escape output (`as_24_bit_terminal_escaped`)
2. HTML output (`styled_line_to_highlighted_html`, `highlighted_html_for_string`)
3. LaTeX output (`as_latex_escaped`)
4. CSS generation (`css_for_theme_with_class_style`)
5. `LinesWithEndings` iterator helper

### Phase 5: Convenience & Polish
1. High-level `highlight_string` function
2. `HighlightResult` dataclass (combines tokens, terminal, HTML)
3. Exception types
4. Documentation and type stubs (.pyi)
5. Tests (pytest)
6. Example Python scripts

---

## Key Implementation Notes

### 1. String Handling
- Python `str` → Rust `&str` via PyO3's `&PyString` or `&str` conversion
- Rust `String` → Python `str` via PyO3's `ToPy` trait
- Avoid unnecessary copies: use `&'py str` for borrowed Python strings

### 2. Error Propagation
```rust
#[pyfunction]
pub fn highlight_line(
    py: Python<'_>,
    self: &mut Highlighter,
    line: &str,
    syntax_set: &SyntaxSet,
) -> PyResult<Vec<(Style, String)>> {
    match self.highlight_line(line, syntax_set) {
        Ok(result) => Ok(result.into_py(py)),
        Err(e) => Err(PyError::from(e)),
    }
}
```

### 3. Feature Flag Strategy
The PyO3 build should use a **dedicated feature set** defined in `pyext/Cargo.toml`:
```toml
[features]
default = ["pyo3-features"]

[features.pyo3-features]
default = false
features = [
    "parsing",
    "yaml-load",
    "dump-load",
    "dump-create",
    "fancy-regex",
    "metadata",
    "plist-load",
    "html",
]

[features.pyo3-embedded-assets]
default = false
features = [
    "pyo3-features",
    "default-syntaxes",
    "default-themes",
]
```

### 4. Threading / GIL
- Acquire GIL before creating Python objects
- Release GIL for long-running operations (regex search, highlighting)
- Use `pyo3::python::with_gil` for GIL management

### 5. Memory Management
- `SyntaxSet` and `ThemeSet` are large → store in Python objects, don't copy
- Use `Py<Highlighter>` if storing highlighter in Python for later use
- `ParseState` and `HighlightState` are small → can be copied

---

## Testing Strategy

### Rust-side (unit tests)
- Test each PyO3 wrapper against the underlying Rust API
- Use `#[cfg(test)]` with PyO3 test utilities

### Python-side (pytest)
- Test `SyntaxSet` loading and syntax lookup
- Test `ThemeSet` loading and theme lookup
- Test highlighting produces correct output
- Test HTML/terminal/LaTeX output
- Test incremental highlighting (state save/restore)
- Test error cases (invalid syntax, missing theme, etc.)
- Test dump save/load round-trip

### Integration
- Compare PyO3 output against Rust example programs (syncat, synhtml)
- Benchmark highlighting speed vs. pure Python syntax highlighters

---

## Files to Create

```
pyext/
├── Cargo.toml              # NEW: PyO3 extension crate
├── pyproject.toml          # NEW: maturin configuration
├── src/
│   ├── lib.rs              # NEW: PyO3 module entry point
│   ├── syntax_set.rs       # NEW: SyntaxSet, SyntaxReference
│   ├── theme_set.rs        # NEW: ThemeSet, Theme, ThemeSettings, ThemeItem
│   ├── style.rs            # NEW: Style, Color, FontStyle, StyleModifier
│   ├── highlighter.rs      # NEW: Highlighter, HighlightState
│   ├── parse_state.rs      # NEW: ParseState, ParseLineOutput, ScopeStack, ScopeStackOp, Scope
│   ├── html.rs             # NEW: HTML output utilities
│   ├── util.rs             # NEW: Terminal, LaTeX, CSS utilities
│   ├── dumps.rs            # NEW: Dump utilities
│   └── converters.rs       # NEW: Shared conversion helpers
tests/
├── conftest.py             # NEW: pytest configuration
├── test_syntax_set.py      # NEW: SyntaxSet tests
├── test_theme_set.py       # NEW: ThemeSet tests
├── test_highlighter.py     # NEW: Highlighter tests
├── test_output.py          # NEW: Output format tests
└── test_convenience.py     # NEW: High-level API tests
examples/
├── highlight_file.py       # NEW: Highlight a file to terminal
├── highlight_html.py       # NEW: Highlight to HTML
├── incremental.py          # NEW: Incremental highlighting demo
└── css_generator.py        # NEW: CSS generation demo
```

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| fancy-regex is slower than oniguruma | Still fast enough for Python; oniguruma can be a feature flag later |
| Large binary size from embedded assets | Make embedded assets optional; users can load syntaxes/themes from disk |
| PyO3 + serde compatibility | Both use serde; should be compatible. Test round-trip serialization. |
| Thread safety of shared SyntaxSet | SyntaxSet is Send+Sync; document that Highlighter is not thread-safe |
| Complex type conversions | Create a dedicated `converters.rs` module for all Py↔Rust conversions |
| Feature flag complexity | Use a dedicated pyext crate with its own Cargo.toml to avoid polluting main crate |
