# syntect-py Architecture

> Python bindings for syntect — high-quality syntax highlighting using Sublime Text grammars.
> PyO3 0.29 · Python ≥ 3.9 · regex-fancy (pure Rust, no Oniguruma)

---

## 1. Overview

`syntect-py` exposes the syntect Rust syntax highlighting library to Python through a thin PyO3 wrapper layer. The design separates concerns into modules that mirror syntect's own module structure, with Python-idiomatic naming and API patterns.

### Design Principles

1. **Mirror syntect's module structure** — Each syntect module has a corresponding `pyext/src/*.rs` file.
2. **Owned data where lifetimes are hard** — `PyClassedHTMLGenerator` and `PyHighlightLines` clone upstream types to own their data, avoiding borrow-lifetime issues across the FFI boundary.
3. **Properties, not methods, for simple accessors** — `MatchPower.value`, `ClearAmount.kind`, `ContextId.syntax_index` are `#[getter]` properties, not callable methods.
4. **Conditional compilation for features** — Metadata types use `#[cfg(feature = "metadata")]` to compile only when the feature is enabled.
5. **No module-level `#![allow(unused)]`** — All `#[allow(dead_code)]` and `#[allow(unused_assignments)]` are scoped to individual items.
6. **Shared conversion helpers** — `converters.rs` centralizes Py↔Rust type conversions to avoid duplication.
7. **String-based constructors for enums** — `ClassStyle("spaced")` and `IncludeBg("no")` accept string constructors in addition to static factory methods.

---

## 2. Module Map

| PyO3 Module | Syntect Equivalent | Responsibility |
|---|---|---|
| `style.rs` | `syntect::highlighting::Color`, `FontStyle`, `Style`, `StyleModifier` | Core color/style types |
| `syntax_set.rs` | `syntect::parsing::SyntaxSet`, `SyntaxReference` | Syntax loading, management, and discovery |
| `theme_set.rs` | `syntect::highlighting::ThemeSet`, `Theme`, `ThemeSettings`, `ThemeItem`, `UnderlineOption` | Theme management and settings |
| `metadata.rs` | `syntect::parsing::Metadata`, `MetadataSet`, `MetadataItem` | `.tmPreferences` metadata (cfg: metadata) |
| `highlighter.rs` | `syntect::easy::HighlightLines`, `HighlightState` | Stateful and stateless highlighting |
| `highlighting.rs` | `syntect::highlighting::ScoredStyle` | Advanced highlighting internals |
| `parse_state.rs` | `syntect::parsing::ParseState`, `ParseLineOutput`, `Scope`, `ScopeStack`, `ScopeStackOp`, `MatchPower`, `ClearAmount`, `ContextId` | Parsing state management |
| `html.rs` | `syntect::html::ClassedHTMLGenerator`, `ClassStyle`, `IncludeBg` | HTML output utilities |
| `util.rs` | `syntect::util::LinesWithEndings` | Utility functions and line iteration |
| `convenience.rs` | `syntect::easy::HighlightResult` | High-level convenience API |
| `dumps.rs` | `syntect::dumps` | Dump/load serialization |
| `converters.rs` | — | Shared Py↔Rust conversion helpers |
| `errors.rs` | — | Custom exception type definitions |

---

## 3. Module Dependencies

```
lib.rs
├── style.rs          (no deps)
├── syntax_set.rs     → errors.rs
├── theme_set.rs      → errors.rs, style.rs
├── metadata.rs       (no deps)
├── highlighter.rs    → syntax_set.rs, theme_set.rs, style.rs, converters.rs, parse_state.rs
├── highlighting.rs   (no deps)
├── parse_state.rs    → syntax_set.rs
├── html.rs           → syntax_set.rs, theme_set.rs, style.rs
├── util.rs           → style.rs
├── convenience.rs    → style.rs, util.rs
├── dumps.rs          → errors.rs, syntax_set.rs, theme_set.rs
├── converters.rs     → style.rs
├── errors.rs         (no deps)
└── (all modules registered in lib.rs)
```

---

## 4. Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Python Layer                                │
│                                                                      │
│  import syntect                                                      │
│  ss = syntect.SyntaxSet.load_defaults(True)                        │
│  ts = syntect.ThemeSet.load_defaults()                              │
│  theme = ts.get_theme("base16-ocean.dark")                          │
│  hl = syntect.Highlighter(rust, theme)                              │
│  tokens = hl.highlight_line("fn main() {}", ss, ts)                 │
│  html = result.as_html("if_different", default_bg)                  │
└─────────────────────────────────────────────────────────────────────┘
                              │ PyO3 FFI
┌─────────────────────────────────────────────────────────────────────┐
│                     pyext/src/*.rs (PyO3)                          │
│                                                                      │
│  PyHighlighter ──► syntect::easy::HighlightLines                    │
│  PyParseState  ──► syntect::parsing::ParseState                     │
│  PySyntaxSet   ──► syntect::parsing::SyntaxSet                      │
│  PyTheme       ──► syntect::highlighting::Theme                     │
│  PyHighlightState ──► syntect::highlighting::HighlightState         │
│  PyClassedHTMLGenerator ──► syntect::html::ClassedHTMLGenerator     │
│  PyScopeStack  ──► syntect::parsing::ScopeStack                     │
│  PyScope       ──► syntect::parsing::Scope                          │
│  PyScopeStackOp ──► syntect::parsing::ScopeStackOp                  │
│                                                                      │
│  (Owned clones where lifetimes cross FFI boundary)                  │
│  (Shared conversion helpers in converters.rs)                       │
└─────────────────────────────────────────────────────────────────────┘
                              │ Rust API
┌─────────────────────────────────────────────────────────────────────┐
│                   syntect (Rust crate)                              │
│                                                                      │
│  Sublime Text grammars (.sublime-syntax, .tmTheme, .tmPreferences)  │
│  regex-fancy (pure Rust regex engine)                               │
│  Output: HTML, ANSI terminal escapes, LaTeX                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Key Design Decisions

### 5.1 Disable `regex-onig` Default Features

The `default-features = false` flag on the syntect dependency excludes `regex-onig` (Oniguruma), whose C `re_registers` structs are not `Send`/`Sync`. This causes PyO3 compilation errors for `#[pyclass]` fields. The `regex-fancy` feature (pure Rust) is used instead.

```toml
syntect = { path = "..", default-features = false, features = [
    "parsing", "yaml-load", "plist-load",
    "dump-load", "dump-create",
    "regex-fancy", "metadata", "html",
    "default-syntaxes", "default-themes",
] }
pyo3 = { version = "0.29", features = ["macros", "abi3-py39"] }
```

### 5.2 Partial `HighlightState`

Direct access to `syntect::highlighting::HighlightState`'s internal fields is private. The wrapper stores:
- `path_scope_stack: Vec<Scope>` — from the public `ScopeStack` API
- `styles_stack: Vec<Style>` — default style from `Highlighter::get_default()`

The `save_state()` method creates a temporary `HighlightLines` instance to extract the scope stack and default style.

### 5.3 `ParseState` Requires `SyntaxSet`

The `PyParseState` constructor takes a `syntax_set` parameter because syntect's `ParseState::new()` requires a reference to the owning `SyntaxSet` to resolve `SyntaxReference` objects. The `parse_line()` method takes `&mut self` to maintain parsing context across lines.

### 5.4 `PyClassedHTMLGenerator` Lifetime Handling

`syntect::html::ClassedHTMLGenerator` holds references to `SyntaxSet` and `SyntaxReference`. The wrapper owns clones of both directly:

```rust
pub struct PyClassedHTMLGenerator {
    syntax_set: syntect::parsing::SyntaxSet,    // owned clone
    syntax_ref: syntect::parsing::SyntaxReference, // owned clone
    parse_state: syntect::parsing::ParseState,
    scope_stack: syntect::parsing::ScopeStack,
    open_spans: isize,
    html: String,
    style: SyntectClassStyle,
}
```

### 5.5 `PyHighlightLines` Statefulness

Unlike `PyHighlighter` which creates a fresh highlighter per call, `PyHighlightLines` maintains the upstream `HighlightLines` stateful behavior. Its `highlight_line()` takes only `(line, syntax_set)` — 2 arguments — because the theme is baked in at construction.

The constructor takes `(syntax_ref, theme_set, theme_name)` — 3 arguments — to resolve the theme from the theme set.

### 5.6 `PyHighlighter.from_state()` Limitation

`from_state()` accepts a `HighlightState` and `Theme`, but does not currently restore the scope stack from the state. It creates a new blank `Highlighter` with the theme configuration. Full incremental highlighting requires deeper integration with the upstream `HighlightLines` API.

### 5.7 `ScopeRepository` Skipped

The upstream `ScopeRepository` type was deprecated in syntect v5.3.0 and is intentionally excluded from bindings.

### 5.8 Arc-Based Lazy Cloning (#17)

`PySyntaxReference`, `PyThemeItem`, and `PyTheme` string/vector fields use `Arc` for O(1) shared ownership:

```rust
pub struct PySyntaxReference {
    name: Arc<String>,                          // clone() is pointer copy
    file_extensions: Arc<Vec<String>>,           // clone() is pointer copy
    scope: Arc<String>,
    first_line_match: Option<Arc<String>>,
    version: i32,
    variables: Arc<Vec<(String, String)>>,
}

pub struct PyTheme {
    key: Arc<String>,
    name: Arc<String>,
    author: Arc<String>,
    // ...
}

pub struct PyThemeItem {
    scope: Arc<String>,
    style_modifier: Arc<String>,
    // ...
}
```

All `find_syntax_by_*` and `syntaxes()` methods use a shared `syntax_ref_to_py()` helper. CSS generation improved from 0.049ms to 0.046ms/100lines. `highlight_string` improved from 128.9ms/100lines to 126.5ms/100lines.

### 5.9 `HighlightResult` vs `Highlighter.highlight_line()`

`HighlightResult` is returned by `highlight_string()` — a high-level convenience function that highlights all lines at once. It provides `tokens`, `html`, and `terminal_escaped` properties plus `as_html()`, `as_terminal_escaped()`, and `as_latex_escaped()` methods.

`Highlighter.highlight_line()` returns `List[Tuple[Style, str]]` directly — a single line's tokens — for use in incremental highlighting loops.

---

## 6. Error Handling

All public functions use consistent error types:

| Python Exception | Origin | Use Case |
|---|---|---|
| `syntect.LoadingError` | `errors.rs` | File loading failures (`.sublime-syntax`, `.tmTheme`) |
| `syntect.ParsingError` | `errors.rs` | Syntax definition parse failures |
| `syntect.DumpError` | `errors.rs` | Dump file read/write failures |
| `syntect.ParseSyntaxError` | `errors.rs` | Custom parse error type |
| `ValueError` | `pyo3.exceptions.PyValueError` | User input validation (invalid syntax/theme names, hex colors, scope parsing) |
| `OSError` | `pyo3.exceptions.PyOSError` | OS-level I/O errors (missing directories, file not found, dump open failures) |
| `RuntimeError` | `pyo3.exceptions.PyRuntimeError` | Internal syntect errors (highlighting failures) |
| `IndexError` | `pyo3.exceptions.PyIndexError` | Out-of-range index access (e.g., `ParseLineOutput.get_op_type(999)`) |

---

## 7. Build System

```
pyext/
├── Cargo.toml          # PyO3 + syntect dependencies (default-features = false)
├── pyproject.toml      # maturin build configuration
├── syntect.pyi         # Type stubs (auto-generated + hand-maintained)
├── src/
│   ├── lib.rs          # Module entry point, class/function registration
│   ├── style.rs        # Color, FontStyle, Style, StyleModifier
│   ├── syntax_set.rs   # SyntaxSet, SyntaxReference, SyntaxSetBuilder
│   ├── theme_set.rs    # ThemeSet, Theme, ThemeSettings, ThemeItem, UnderlineOption
│   ├── metadata.rs     # Metadata, MetadataSet, MetadataItem
│   ├── highlighter.rs  # Highlighter, HighlightState, HighlightLines, split_lines_with_endings
│   ├── highlighting.rs # ScoredStyle, ScopeRangeIterator
│   ├── parse_state.rs  # ParseState, ParseLineOutput, Scope, ScopeStack, ScopeStackOp,
│   │                     # MatchPower, ClearAmount, ContextId
│   ├── html.rs         # ClassedHTMLGenerator, ClassStyle, IncludeBg, CSS/HTML functions
│   ├── util.rs         # LinesWithEndings, split_at, modify_range, lines_with_endings,
│   │                     # as_terminal_escaped, as_html, as_latex_escaped
│   ├── convenience.rs  # HighlightResult, highlight_string
│   ├── dumps.rs        # dump_syntax_set, load_syntax_set, dump_theme_set, load_theme_set
│   ├── converters.rs   # syntect_style_to_py, syntect_color_to_py, syntect_font_style_to_py,
│   │                     # py_color_to_syntect, py_font_style_to_syntect, py_style_to_syntect
│   └── errors.rs       # LoadingError, ParsingError, DumpError, ParseSyntaxError,
│                         # loading_error_to_string, dump_error_to_string
├── examples/           # 9 example scripts
├── tests/              # 337 tests across 15 test files (incl. 70 golden outputs)
└── mypy.ini            # mypy type checking configuration
```

---

## 8. Type Mapping (Complete)

### Core Types

| Rust Type | Python Class | Constructor | Key Methods/Properties |
|---|---|---|---|
| `syntect::highlighting::Color` | `syntect.Color` | `Color(r, g, b, a)` | `from_hex()`, `to_hex()`, `r`, `g`, `b`, `a`, `__eq__`, `__repr__` |
| `syntect::highlighting::FontStyle` | `syntect.FontStyle` | `FontStyle(bits)` | `BOLD`, `ITALIC`, `UNDERLINE` (class attrs), `bits`, `__or__`, `__and__`, `__xor__`, `__invert__`, `__repr__` |
| `syntect::highlighting::Style` | `syntect.Style` | `Style(fg, bg, fs)` | `from_hex_styles()`, `foreground`, `background`, `font_style`, `__eq__`, `__repr__` |
| `syntect::highlighting::StyleModifier` | `syntect.StyleModifier` | `StyleModifier(fg, bg, fs)` | `foreground`, `background`, `font_style`, `__repr__` |

### Syntax Types

| Rust Type | Python Class | Constructor | Key Methods/Properties |
|---|---|---|---|
| `syntect::parsing::SyntaxSet` | `syntect.SyntaxSet` | `SyntaxSet.new()` | `load_defaults()`, `load_from_folder()`, `from_dump()`, `builder()`, `into_builder()`, `warnings()`, `find_syntax_by_extension()`, `find_syntax_by_name()`, `find_syntax_by_scope()`, `find_syntax_for_file()`, `find_syntax_plain_text()`, `syntaxes()`, `to_dump()`, `find_unlinked_contexts()`, `metadata`, `__repr__` |
| `syntect::parsing::SyntaxReference` | `syntect.SyntaxReference` | (opaque) | `name`, `scope`, `file_extensions`, `hidden`, `first_line_match`, `version`, `variables`, `__repr__` |
| `syntect::parsing::SyntaxSetBuilder` | `syntect.SyntaxSetBuilder` | `SyntaxSetBuilder()` | `add_from_folder()`, `add_plain_text_syntax()`, `build()`, `warnings()`, `__repr__` |

### Theme Types

| Rust Type | Python Class | Constructor | Key Methods/Properties |
|---|---|---|---|
| `syntect::highlighting::ThemeSet` | `syntect.ThemeSet` | `ThemeSet.new()` | `load_defaults()`, `from_dump()`, `builder()`, `add_from_folder()`, `get_theme()`, `theme_names()`, `to_dump()`, `__repr__` |
| `syntect::highlighting::Theme` | `syntect.Theme` | (opaque) | `key`, `name`, `author`, `settings`, `scopes`, `__repr__` |
| `syntect::highlighting::ThemeSettings` | `syntect.ThemeSettings` | (opaque) | 29 properties: `foreground`, `background`, `selection_background`, `gutter_foreground`, `gutter_background`, `caret`, `line_highlight`, `misspelling`, `minimap_border`, `accent`, `popup_css`, `phantom_css`, `bracket_contents_foreground`, `bracket_contents_options`, `brackets_foreground`, `brackets_background`, `brackets_options`, `tags_foreground`, `tags_options`, `highlight`, `find_highlight`, `find_highlight_foreground`, `selection_foreground`, `selection_border`, `inactive_selection`, `inactive_selection_foreground`, `guide`, `active_guide`, `stack_guide`, `shadow`, `__repr__` |
| `syntect::highlighting::ThemeItem` | `syntect.ThemeItem` | (opaque) | `scope`, `foreground`, `background`, `font_style`, `style_modifier`, `style` (→ `StyleModifier`), `__repr__` |
| `syntect::highlighting::UnderlineOption` | `syntect.UnderlineOption` | (opaque) | `none_()`, `underline()`, `stippled_underline()`, `squiggly_underline()`, `__repr__` |

### Metadata Types

| Rust Type | Python Class | Constructor | Key Methods/Properties |
|---|---|---|---|
| `syntect::parsing::Metadata` | `syntect.Metadata` | (opaque) | `sets`, `__len__`, `__repr__` |
| `syntect::parsing::MetadataSet` | `syntect.MetadataSet` | (opaque) | `selector_string`, `items`, `__repr__` |
| `syntect::parsing::MetadataItem` | `syntect.MetadataItem` | (opaque) | `increase_indent_pattern`, `decrease_indent_pattern`, `bracket_indent_next_line_pattern`, `disable_indent_next_line_pattern`, `unindented_line_pattern`, `indent_parens`, `shell_variables`, `line_comment`, `block_comment`, `__repr__` |

### Highlighting Types

| Rust Type | Python Class | Constructor | Key Methods/Properties |
|---|---|---|---|
| `syntect::easy::HighlightLines` | `syntect.Highlighter` | `Highlighter(syntax_ref, theme)` | `highlight_line(line, ss, ts)`, `highlight_lines(code, ss, ts)`, `highlight_file(path, ss, ts)`, `save_state(ss, ts)`, `from_state(state, theme)`, `__repr__` |
| `syntect::highlighting::HighlightState` | `syntect.HighlightState` | `HighlightState()` | `path_scope_stack`, `styles_stack`, `path_scope_string`, `styles_count`, `__repr__` |
| `syntect::easy::HighlightLines` | `syntect.HighlightLines` | `HighlightLines(syntax_ref, theme_set, theme_name)` | `highlight_line(line, ss)`, `highlight_lines(code, ss, ts)`, `__repr__` |
| `syntect::easy::HighlightResult` | `syntect.HighlightResult` | (opaque) | `tokens`, `html`, `terminal_escaped`, `as_html()`, `as_terminal_escaped()`, `as_latex_escaped()`, `__repr__` |
| `syntect::highlighting::ScoredStyle` | `syntect.ScoredStyle` | `ScoredStyle(fg_r,fg_g,fg_b,fg_a,fg_score, bg_r,bg_g,bg_b,bg_a,bg_score, fs, fs_score)` | All color components + scores as properties, `__repr__` |

### Parsing Types

| Rust Type | Python Class | Constructor | Key Methods/Properties |
|---|---|---|---|
| `syntect::parsing::ParseState` | `syntect.ParseState` | `ParseState(syntax_name, syntax_set)` | `parse_line(line, ss)` (mutates state), `is_speculative()`, `syntax_name`, `__repr__` |
| `syntect::parsing::ParseLineOutput` | `syntect.ParseLineOutput` | (opaque) | `ops`, `replayed`, `warnings`, `get_scope_stack_op(index)`, `get_op_type(index)`, `__repr__` |
| `syntect::parsing::Scope` | `syntect.Scope` | `Scope(value)` / `Scope.from_string()` | `to_string()`, `len()`, `is_empty()`, `is_prefix_of()`, `__eq__`, `__repr__` |
| `syntect::parsing::ScopeStack` | `syntect.ScopeStack` | `ScopeStack()` / `ScopeStack.from_string()` | `push()`, `pop()`, `apply()`, `as_string()`, `len()`, `is_empty()`, `__repr__` |
| `syntect::parsing::ScopeStackOp` | `syntect.ScopeStackOp` | (opaque) | `push()`, `pop(n)`, `clear_all()`, `clear_top(n)`, `restore()`, `noop()`, `__repr__` |
| `syntect::parsing::MatchPower` | `syntect.MatchPower` | `MatchPower(value)` | `value`, `__float__()`, `__repr__` |
| `syntect::parsing::ClearAmount` | `syntect.ClearAmount` | (opaque) | `all_()`, `top_n(n)`, `kind`, `value`, `__repr__` |
| `syntect::parsing::ContextId` | `syntect.ContextId` | `ContextId(syntax_index, context_index)` | `syntax_index`, `context_index`, `__eq__`, `__repr__` |

### HTML/Output Types

| Rust Type | Python Class | Constructor | Key Methods/Properties |
|---|---|---|---|
| `syntect::html::ClassedHTMLGenerator` | `syntect.ClassedHTMLGenerator` | `ClassedHTMLGenerator(syntax_ref, syntax_set, class_style)` | `parse_html_for_line(line)`, `parse_html_for_line_which_includes_newline(line)`, `finalize()`, `__repr__` |
| `syntect::html::ClassStyle` | `syntect.ClassStyle` | `ClassStyle("spaced"|"spaced_prefixed"|"class_attribute")` | `spaced()`, `spaced_prefixed(prefix)`, `class_attribute()`, `__repr__` |
| `syntect::html::IncludeBackground` | `syntect.IncludeBg` | `IncludeBg("no"|"yes"|anything)` | `no()`, `yes()`, `if_different()`, `__repr__` |
| `syntect::util::LinesWithEndings` | `syntect.LinesWithEndings` | `LinesWithEndings(content)` | `__iter__`, `__next__`, (class, not just a function) |
| `syntect::highlighting::ScopeRangeIterator` | `syntect.ScopeRangeIterator` | `ScopeRangeIterator(ops, line)` | `__iter__`, `__next__`, yields `(start, end, scope)` |

### Module-Level Functions

| Function | Module | Signature | Returns |
|---|---|---|---|
| `as_terminal_escaped` | `util` | `(tokens, include_bg)` | `str` |
| `as_html` | `util` | `(tokens, include_bg, default_bg)` | `str` |
| `as_latex_escaped` | `util` | `(tokens)` | `str` |
| `split_at` | `util` | `(tokens, position)` | `(left, right)` |
| `modify_range` | `util` | `(tokens, range_start, range_end, new_style)` | `List[Tuple[Style, str]]` |
| `lines_with_endings` | `util` | `(content)` | `LinesWithEndings` |
| `css_for_theme` | `html` | `(theme, class_style)` | `str` |
| `css_for_theme_class` | `html` | `(theme, class_style_obj)` | `str` |
| `generate_css` | `html` | `(theme, class_style)` | `str` |
| `highlighted_html_for_string_py` | `html` | `(code, syntax_ref, theme, ss, ts, include_bg, start_line)` | `str` |
| `create_html_file` | `html` | `(code, syntax_ref, theme, ss, ts)` | `str` |
| `highlighted_html_at_line_and_column_number` | `html` | `(code, syntax_ref, theme, ss, ts, start_line)` | `str` |
| `tokens_to_classed_spans` | `html` | `(tokens, class_style)` | `str` |
| `line_tokens_to_classed_spans_py` | `html` | `(line, ops, class_style)` | `(html, delta)` |
| `styled_line_to_highlighted_html` | `html` | `(tokens, include_bg)` | `str` |
| `dump_syntax_set` | `dumps` | `(ss, path)` | `None` |
| `load_syntax_set` | `dumps` | `(path)` | `SyntaxSet` |
| `dump_theme_set` | `dumps` | `(ts, path)` | `None` |
| `load_theme_set` | `dumps` | `(path)` | `ThemeSet` |
| `highlight_string` | `highlighter` | `(code, syntax_name, theme_name, ss, ts)` | `HighlightResult` |

---

## 9. Scope Bit Flags

| Bit | Meaning | `syntect.FontStyle` constant |
|---|---|---|
| 1 | Bold | `FontStyle.BOLD` |
| 2 | Underline | `FontStyle.UNDERLINE` |
| 4 | Italic | `FontStyle.ITALIC` |

Combine with `|`: `FontStyle.BOLD | FontStyle.ITALIC` → bits = 5

---

## 10. Class Style Modes

| Mode | `kind` | CSS Class Pattern |
|---|---|---|
| `spaced` | 0 | `<span class="token keyword">` |
| `spaced_prefixed` | 1 | `<span class="syn-keyword">` (or custom prefix) |
| `class_attribute` | 2 | `<span class_attribute="keyword">` |

---

## 11. Include Background Modes

| Mode | `kind` | Behavior |
|---|---|---|
| `no` | 0 | Never include background color |
| `yes` | 1 | Always include background color |
| `if_different` | 2 | Only include if different from `default_bg` |

---

*Generated: 2026-06-30 · 337 tests passing · Zero compiler warnings · All phases complete · CI configured · Arc-based lazy cloning · 70 golden output tests*
