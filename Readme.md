# syntect-py

> High-quality syntax highlighting for Python using Sublime Text grammars, powered by the [syntect](https://github.com/trishume/syntect) Rust crate.
> syntect-py 5.3.0 · PyO3 0.29 · Python ≥ 3.9 · Pure Rust regex (no C dependencies)

[![Tests](https://img.shields.io/badge/tests-346_passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)]()
[![PyO3](https://img.shields.io/badge/pyo3-0.29-orange)]()

---

## Features

- **190+ built-in syntaxes** — Rust, Python, JavaScript, TypeScript, Go, C, C++, Java, HTML, CSS, YAML, TOML, Markdown, and more
- **55 bundled mordant themes** — Dracula, Nord, Monokai Extended, OneDark, Solarized, and more, loaded automatically
- **Syntax lookup primitives** — token/alias lookup and first-line detection for shebangs, modelines, and XML
- **Theme authoring** — construct themes with `ThemeSettings`, `ThemeItem`, `ScopeSelectors`, and `StyleModifier`
- **VS Code theme support** — parse JSON/JSONC themes and register custom plist/VS Code themes
- **Assets compatibility API** — `Assets`/`HighlightingAssets` fallback API for future expanded grammar data
- **Multiple output formats** — inline HTML, class-based HTML, ANSI terminal escapes (24-bit color), LaTeX
- **Stateful highlighting** — incremental re-highlighting with save/restore for editor integration
- **Real parse state** — context-sensitive parsing across lines with scope stack introspection
- **Metadata access** — `.tmPreferences` metadata (indent rules, comment patterns, shell variables)
- **Serialization** — dump/load syntax sets and themes as binary `.packdump`/`.themedump` files
- **Zero C dependencies** — uses `regex-fancy` (pure Rust), no Oniguruma
- **Full type stubs** — comprehensive `.pyi` stubs for IDE autocomplete and type checking
- **346 tests** — covering syntax/theme parity, JSONC themes, CSS selectors, bundled themes, assets fallback, stub conformance, and golden outputs

---

## Installation

```bash
pip install syntect
```

### From source

```bash
# From the repository root
python -m pip install maturin
maturin build --release --out pyext/dist -m pyext/Cargo.toml
python -m pip install --force-reinstall pyext/dist/*.whl
```

Prebuilt wheels are published for Linux x86_64/ARM64, macOS x86_64/ARM64,
and Windows x86_64. Source distributions are also published to PyPI from
`v*` Git tags.

---

## Quick Start

```python
import syntect

# Load syntax definitions and themes (once at startup)
ss = syntect.SyntaxSet.load_defaults(True)
ts = syntect.ThemeSet.load_defaults()

# Get a syntax and theme
rust = ss.find_syntax_by_name("Rust")
theme = ts.get_theme("base16-ocean.dark")

# Create a highlighter
hl = syntect.Highlighter(rust, theme)

# Highlight a single line
tokens = hl.highlight_line("fn main() {}", ss, ts)
for style, text in tokens:
    print(f"{style.foreground.to_hex()} {text}")

# Or use the high-level convenience function
result = syntect.highlight_string(
    code='fn main() { println!("Hello"); }',
    syntax="Rust",
    theme="base16-ocean.dark",
    syntax_set=ss,
    theme_set=ts
)

print(result.html)          # HTML output
print(result.as_terminal_escaped(True))  # ANSI terminal output
print(result.as_latex_escaped())          # LaTeX output
```

---

## Incremental Highlighting

For editors that need to re-highlight after changes:

```python
hl = syntect.Highlighter(rust, theme)
state = hl.save_state(ss, ts)  # Save highlighting state

# ... some time later ...
hl2 = syntect.Highlighter.from_state(state, theme)  # Resume from state

# Or use the stateful HighlightLines API (upstream behavior)
hl_lines = syntect.HighlightLines(rust, ss, ts, "base16-ocean.dark")
for line in code.split("\n"):
    tokens = hl_lines.highlight_line(line, ss)  # 2 args: (line, ss)

# Or construct directly from a Theme object:
hl_direct = syntect.HighlightLines.with_theme(rust, ss, theme)
```

---

## HTML Output

### Inline HTML (single tokens)

```python
tokens = hl.highlight_line("fn main() {}", ss, ts)
html = syntect.as_html(tokens, "if_different", None)
# <span style="color:#B48EAD;">fn</span><span style="color:#C0C5CE;"> </span>...
```

### Class-based HTML (compact, CSS-externally styled)

```python
class_style = syntect.ClassStyle.spaced_prefixed("syn-")
html = syntect.tokens_to_classed_spans(tokens, class_style)
# <span class="syn-keyword">fn</span><span class="syn-punctuation"> </span>...
```

### Streaming HTML generator

```python
gen = syntect.ClassedHTMLGenerator(rust, ss, class_style)
for line in code.split("\n"):
    gen.parse_html_for_line_which_includes_newline(line)
html = gen.finalize()  # Closes any open spans
```

### Full HTML with line numbers

```python
html = syntect.highlighted_html_at_line_and_column_number(
    code, rust, theme, ss, ts, start_line=1
)
# <pre><span data-line="1">...</span>\n<span data-line="2">...</span></pre>
```

### CSS generation

```python
css = syntect.css_for_theme(theme, "spaced")
# .keyword { color: #B48EAD; }
# .function { color: #8FA1B3; }

cs = syntect.ClassStyle.spaced_prefixed("syn-")
css = syntect.css_for_theme_class(theme, cs)
```

CSS generation preserves comma-separated selectors and emits combined font
styles such as bold + italic + underline.

---

## Theme Authoring and VS Code Themes

```python
settings = syntect.ThemeSettings()
settings.background = syntect.Color.from_hex("#1E1E1E")

item = syntect.ThemeItem(
    syntect.ScopeSelectors.from_string("variable, constant"),
    syntect.StyleModifier(
        foreground=syntect.Color.from_hex("#FFD700"),
        font_style=syntect.FontStyle.from_string("bold italic underline"),
    ),
)
theme = syntect.Theme(
    name="Custom Theme", author="me", settings=settings, scopes=[item]
)

ts = syntect.ThemeSet()
ts.add_theme("custom", theme)

# VS Code JSON/JSONC or plist XML
content = open("theme.json", encoding="utf-8").read()
syntect.add_custom_theme("vscode-theme", content)
print(syntect.list_themes())
```

The process-wide `add_custom_theme()` registry is separate from caller-owned
`ThemeSet` instances. Use `ThemeSet.add_theme()` for an isolated set.

## Assets Compatibility API

```python
assets = syntect.Assets.from_binary()
assets.set_fallback_theme("Monokai Extended")
asset_syntaxes = assets.get_syntax_set()
asset_themes = assets.get_theme_set()
theme = assets.get_theme("unknown-theme")  # configured fallback
```

The API is ready for expanded bat grammar data. The current implementation
uses fork-compatible default syntax/theme data because the published
`syntect-assets` binary dump is not compatible with this fork's serialization.

## Terminal Output (24-bit color)

```python
tokens = hl.highlight_line("fn main() {}", ss, ts)
escaped = syntect.as_terminal_escaped(tokens, include_bg=True)
print(escaped, end="")  # \x1b[38;2;180;142;173mfn\x1b[38;2;192;197;206m ...
```

Alpha transparency is handled automatically — foreground colors are blended with the background.

---

## LaTeX Output

```python
tokens = hl.highlight_line("fn main() {}", ss, ts)
latex = syntect.as_latex_escaped(tokens)
# \textcolor[RGB]{180,142,173}{fn}\textcolor[RGB]{192;197;206}{ }...
```

Spaces and newlines are elided when the style doesn't change.

---

## Metadata Access (`.tmPreferences`)

```python
ss = syntect.SyntaxSet.load_defaults(True)
meta = ss.metadata
if meta:
    for mset in meta.sets:
        print(mset.selector_string)       # "source.python"
        item = mset.items
        print(item.line_comment)          # "//"
        print(item.indent_parens)         # True/False
        print(item.shell_variables)       # List[Tuple[str, str]]
        print(item.increase_indent_pattern)
```

---

## Parsing Introspection

```python
ps = syntect.ParseState("Rust", ss)
output = ps.parse_line("fn main() {", ss)

for pos, op in output.ops:
    print(f"  {pos}: {op}")
    # 0: Push(source.rust)
    # 1: Push(keyword.declaration)

is_speculative = ps.is_speculative()  # True during backtracking
print(ps.syntax_name)                 # "Rust"
```

---

## Dump / Serialization

```python
# Save to binary dump (fast loading)
syntect.dump_syntax_set(ss, "syntaxes.packdump")
syntect.dump_theme_set(ts, "themes.themedump")

# Load from dump
ss = syntect.load_syntax_set("syntaxes.packdump")
ts = syntect.load_theme_set("themes.themedump")
```

---

## Utility Functions

```python
# Split tokens at a character position
left, right = syntect.split_at(tokens, 5)

# Modify style in a character range
modified = syntect.modify_range(tokens, 0, 5, new_style)

# Iterate lines with their endings
for line, ending in syntect.lines_with_endings("hello\nworld\r\n"):
    print(repr(line), repr(ending))
    # 'hello' '\n'  'world' '\r\n'
```

---

## Error Handling

```python
import syntect

try:
    ss = syntect.SyntaxSet.load_from_folder("/missing", True)
except (syntect.LoadingError, OSError) as e:
    print(f"Load error: {e}")

theme = ts.get_theme("nonexistent")
if theme is None:  # Returns None when no fallback is supplied
    print("Theme not found")

fallback = ts.get_theme("nonexistent", "base16-ocean.dark")
```

**Exception types:** `LoadingError`, `ParsingError`, `DumpError`, `ParseSyntaxError`, `ValueError`, `OSError`, `RuntimeError`, `IndexError`

---

## API Gotchas

| Issue | Solution |
|---|---|
| `Highlighter.highlight_line()` takes 3 args `(line, ss, ts)` | `HighlightLines.highlight_line()` takes 2 args `(line, ss)` |
| `as_html()` requires `default_bg` parameter | Pass `None` for no default |
| `rust.variables` is `List[Tuple[str, str]]` | Not a `Dict[str, str]` |
| `MatchPower.value` is a property | Not a method: use `mp.value`, not `mp.value()` |
| `save_state()` requires `ss, ts` arguments | Not no-arg: `hl.save_state(ss, ts)` |
| `get_theme()` returns `None` for missing | Pass `fallback="theme-name"` for fallback lookup |
| `HighlightLines` unknown theme | Falls back to `InspiredGitHub` when available |
| `add_custom_theme()` registry | Process-wide; use `ThemeSet.add_theme()` for an isolated set |
| `Color.to_hex()` returns uppercase | `#FF0000`, not `#ff0000` |
| `is_prefix_of()` semantics | `parent.is_prefix_of(child)` — parent checks if child starts with it |

---

## Project Structure

```
syntect-py/
├── ARCHITECTURE.md       # Architecture documentation
├── QUICKREF.md           # Quick reference guide
├── CHANGELOG.md          # Version history
├── DESIGN.md             # Design decisions
├── Readme.md             # This file
├── .github/workflows/CI.yml      # Multiplatform CI
├── .github/workflows/Release.yml # Wheel/sdist build and PyPI publish
├── pyext/
│   ├── Cargo.toml        # PyO3 + syntect dependencies
│   ├── pyproject.toml    # maturin build configuration and theme inclusion
│   ├── README.md         # Python package metadata readme
│   ├── syntect.pyi       # Type stubs (complete)
│   ├── syntect/
│   │   ├── __init__.py   # Mixed-package wrapper
│   │   ├── __init__.pyi
│   │   └── themes/       # 55 bundled mordant themes
│   ├── src/
│   │   ├── lib.rs        # Module entry point
│   │   ├── style.rs      # Color, FontStyle, Style, StyleModifier
│   │   ├── syntax_set.rs # SyntaxSet, SyntaxReference, SyntaxSetBuilder
│   │   ├── theme_set.rs  # ThemeSet, Theme, ThemeSettings, ThemeItem, ScopeSelectors
│   │   ├── vscode_theme.rs# VS Code JSON/JSONC conversion and registry
│   │   ├── assets.rs      # Assets/HighlightingAssets compatibility API
│   │   ├── metadata.rs   # Metadata, MetadataSet, MetadataItem
│   │   ├── highlighter.rs# Highlighter, HighlightState, HighlightLines
│   │   ├── highlighting.rs# ScoredStyle, ScopeRangeIterator
│   │   ├── parse_state.rs# ParseState, Scope, ScopeStack, etc.
│   │   ├── html.rs       # ClassedHTMLGenerator, CSS/HTML functions
│   │   ├── util.rs       # LinesWithEndings, split_at, modify_range
│   │   ├── convenience.rs# HighlightResult
│   │   ├── dumps.rs      # dump/load syntax/theme sets
│   │   ├── converters.rs # Py↔Rust conversion helpers
│   │   └── errors.rs     # Exception types
│   ├── examples/         # 9 example scripts
│   ├── benches/          # Benchmark scripts (highlighting, loading, parsing)
│   └── tests/            # Python, parity, stub, and golden-output tests
```

---

## Examples

| Example | Description |
|---|---|
| `basic_highlight.py` | Single-line highlighting with all output formats |
| `incremental.py` | Stateful highlighting with save/restore |
| `highlight_file.py` | Multi-line file highlighting with CRLF support |
| `advanced_highlight.py` | Classed HTML, scope stack, split/modify |
| `highlight_html.py` | Full HTML file generation with CSS |
| `css_generator.py` | CSS generation for themes |
| `benchmark.py` | Performance benchmarking |
| `metadata_example.py` | Metadata access from `.tmPreferences` |
| `error_handling.py` | Error handling patterns |

Run any example from the repository root after installing the wheel:

```bash
python pyext/examples/basic_highlight.py
```

---

## Documentation

| Document | Contents |
|---|---|
| `ARCHITECTURE.md` | Architecture, module map, type mapping, design decisions |
| `QUICKREF.md` | Complete API reference with examples and gotchas |
| `syntect.pyi` | Type stubs for IDE autocomplete |
| `docs/IMPROVEMENT_PLAN.md` | Remediation & improvement plan with phased execution |

---

## Tests

```bash
python -m pytest pyext/tests/ -v
```

346 tests passing. The suite includes stub conformance, JSONC theme conversion,
CSS selector preservation, bundled-theme loading, assets fallback, LaTeX
escaping, HTML/terminal output, and golden outputs.

---

## Built On

`syntect-py` is a Python binding layer over the [syntect](https://github.com/trishume/syntect) Rust crate, which provides:

- 190+ built-in syntax definitions from [Sublime Text Packages](https://github.com/sublimehq/Packages)
- 55 bundled mordant themes plus syntect's built-in themes
- JSON/JSONC VS Code theme conversion and custom theme registration
- Pure Rust `fancy-regex` engine (no C dependencies)
- 24-bit color ANSI terminal output, HTML, and LaTeX support

---

*346 tests passing · syntect-py 5.3.0 · PyO3 0.29 · Python ≥ 3.9 · P1–P4.5 parity implemented · PyPI CI/release configured · expanded bat grammar data remains outstanding*
