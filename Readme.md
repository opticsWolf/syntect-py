# syntect-py

> High-quality syntax highlighting for Python using Sublime Text grammars, powered by the [syntect](https://github.com/trishume/syntect) Rust crate.
> PyO3 0.29 · Python ≥ 3.9 · Pure Rust regex (no C dependencies)

[![Tests](https://img.shields.io/badge/tests-337_passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)]()
[![PyO3](https://img.shields.io/badge/pyo3-0.29-orange)]()

---

## Features

- **192+ syntaxes** — Rust, Python, JavaScript, TypeScript, Go, C, C++, Java, HTML, CSS, YAML, TOML, Markdown, and more (all from Sublime Text packages)
- **10+ themes** — base16-ocean.dark, Solarized Light, InspiredGithub, and more
- **Multiple output formats** — inline HTML, class-based HTML, ANSI terminal escapes (24-bit color), LaTeX
- **Stateful highlighting** — incremental re-highlighting with save/restore for editor integration
- **Real parse state** — context-sensitive parsing across lines with scope stack introspection
- **Metadata access** — `.tmPreferences` metadata (indent rules, comment patterns, shell variables)
- **Serialization** — dump/load syntax sets and themes as binary `.packdump`/`.themedump` files
- **Zero C dependencies** — uses `regex-fancy` (pure Rust), no Oniguruma
- **Full type stubs** — comprehensive `.pyi` stubs for IDE autocomplete and type checking
- **337 tests** — covering all 29 implementation phases (Phases 11–29) plus 70 golden output tests

---

## Installation

```bash
pip install syntect
```

### From source

```bash
cd pyext
maturin build
pip install --force-reinstall target/wheels/*.whl
```

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
hl_lines = syntect.HighlightLines(rust, ts, "base16-ocean.dark")
for line in code.split("\n"):
    tokens = hl_lines.highlight_line(line, ss)  # 2 args: (line, ss)
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

---

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
if theme is None:  # Returns None, does not raise
    print("Theme not found")
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
| `get_theme()` returns `None` for missing | Does not raise exception |
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
├── .github/workflows/ci.yml  # CI/CD pipeline
├── pyext/
│   ├── Cargo.toml        # PyO3 + syntect dependencies
│   ├── pyproject.toml    # maturin build configuration
│   ├── syntect.pyi       # Type stubs (complete)
│   ├── src/
│   │   ├── lib.rs        # Module entry point
│   │   ├── style.rs      # Color, FontStyle, Style, StyleModifier
│   │   ├── syntax_set.rs # SyntaxSet, SyntaxReference, SyntaxSetBuilder
│   │   ├── theme_set.rs  # ThemeSet, Theme, ThemeSettings, ThemeItem
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
│   └── tests/            # 337 tests (15 test files + golden outputs)
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

Run any example:

```bash
cd pyext
python examples/basic_highlight.py
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
cd pyext
python -m pytest tests/ -v
```

337 tests passing (267 original + 70 golden output tests). Includes stub conformance, LaTeX escaping, HTML/terminal output, CSS generation, and performance benchmarks.

---

## Built On

`syntect-py` is a Python binding layer over the [syntect](https://github.com/trishume/syntect) Rust crate, which provides:

- 192+ syntax definitions from [Sublime Text Packages](https://github.com/sublimehq/Packages)
- 10+ themes from the [base16](https://github.com/chrisk/base16) collection
- Pure Rust `fancy-regex` engine (no C dependencies)
- 24-bit color ANSI terminal output, HTML, and LaTeX support

---

*All 337 tests passing · Zero compiler warnings · PyO3 0.29 · Python ≥ 3.9 · All phases complete · CI configured*
