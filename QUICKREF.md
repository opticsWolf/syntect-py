# syntect-py Quick Reference

> Python bindings for syntect — high-quality syntax highlighting using Sublime Text grammars.
> syntect-py 5.3.0 · PyO3 0.29 · Python ≥ 3.9 · regex-fancy (pure Rust)
>
> Current parity coverage: P1–P4.5. The Assets API is available; expanded bat grammar data remains outstanding.

---

## Installation

```bash
pip install syntect
```

Or build from source:

```bash
# From the repository root
python -m pip install maturin
maturin build --release -m pyext/Cargo.toml
python -m pip install --force-reinstall pyext/target/wheels/*.whl
```

Release wheels are built by GitHub Actions for Linux x86_64/ARM64, macOS
x86_64/ARM64, and Windows x86_64. A source distribution is also uploaded to
PyPI when a `v*` tag is pushed.

---

## Minimal Example

```python
import syntect

ss = syntect.SyntaxSet.load_defaults(True)
ts = syntect.ThemeSet.load_defaults()
rust = ss.find_syntax_by_name("Rust")
theme = ts.get_theme("base16-ocean.dark")

hl = syntect.Highlighter(rust, theme)
code = "fn main() { println!(\"Hello\"); }"
tokens = hl.highlight_lines(code, ss, ts)

result = syntect.highlight_string(code, "Rust", "base16-ocean.dark", ss, ts)
print(result.html)
print(result.as_terminal_escaped(True))
```

---

## Color and Style Types

### Color

```python
c = syntect.Color.from_hex("#FF0000")   # r=255, g=0, b=0, a=255
c = syntect.Color(255, 0, 0, 255)
hex_str = c.to_hex()                     # "#FF0000" (uppercase)
c2 = syntect.Color.from_hex("FF0000")   # also works without #
c == syntect.Color(255, 0, 0, 255)       # True
repr(c)                                  # "Color(r=255, g=0, b=0, a=255)"
```

**Properties:** `r`, `g`, `b`, `a` (all `u8`)

**Methods:** `__eq__`, `__repr__`

### FontStyle

```python
fs = syntect.FontStyle(3)                  # BOLD (1) | UNDERLINE (2)
fs = syntect.FontStyle.from_string("bold italic underline")  # bits=7
fs_bold = syntect.FontStyle.BOLD           # bits=1
fs_italic = syntect.FontStyle.ITALIC       # bits=4
fs_underline = syntect.FontStyle.UNDERLINE # bits=2
combined = fs_bold | fs_italic             # bits=5
masked = fs & fs_bold                      # bits=1
inverted = ~fs                            # bits=~3
repr(fs)                                   # "FontStyle(BOLD | UNDERLINE)" or "(empty)"
```

**Properties:** `bits` (`u8`)

**Operators:** `__or__`, `__and__`, `__xor__`, `__invert__`

### Style

```python
style = syntect.Style.from_hex_styles("#FF0000", "#000000", 3)
style = syntect.Style(fg_color, bg_color, font_style)
fg = style.foreground                     # Color
bg = style.background                     # Color
fs = style.font_style                     # FontStyle
style == syntect.Style(...)               # True (compares fg, bg, fs)
repr(style)                               # "Style(fg=#FF0000, bg=#000000, style=3)"
```

**Properties:** `foreground`, `background`, `font_style`

**Static method:** `from_hex_styles(fg_hex, bg_hex, font_bits)`

**Constructor:** `Style(fg, bg, fs)`

### StyleModifier

```python
sm = syntect.StyleModifier(fg, bg, fs)   # All Optional[Color/FontStyle]
sm.foreground                             # Optional[Color]
sm.background                             # Optional[Color]
sm.font_style                             # Optional[FontStyle]
repr(sm)                                  # "StyleModifier(fg='#FF0000', bg=None, font=3)"
```

---

## Syntax Management

### SyntaxSet

```python
# Constructors
ss = syntect.SyntaxSet()                 # Empty syntax set
ss = syntect.SyntaxSet.load_defaults(True)
ss = syntect.SyntaxSet.load_defaults(False)
ss = syntect.SyntaxSet.load_from_folder("/path/to/syntaxes", False)
ss = syntect.SyntaxSet.from_dump("syntaxes.packdump")

# Discovery
ref = ss.find_syntax_by_name("Rust")
ref = ss.find_syntax_by_extension("rs")
ref = ss.find_syntax_by_token("rs")       # Language token/alias lookup
ref = ss.find_syntax_by_first_line("#!/usr/bin/env node")
ref = ss.find_syntax_by_scope("source.rust")
ref = ss.find_syntax_for_file("main.rs")   # Returns None|SyntaxReference
ref = ss.find_syntax_plain_text()          # Returns SyntaxReference

# Listing
refs = ss.syntaxes()                       # List[SyntaxReference]
unlinked = ss.find_unlinked_contexts()     # List[str]
meta = ss.metadata                         # Optional[Metadata]
warnings = ss.warnings()                   # List[str]

# Conversion
builder = ss.into_builder()                # SyntaxSetBuilder (clones ss)
ss.to_dump("syntaxes.packdump")            # Save to dump file

repr(ss)                                   # "SyntaxSet(syntaxes=N)"
```

### SyntaxReference

```python
ref = ss.find_syntax_by_name("Rust")
ref.name                                    # "Rust"
ref.scope                                   # "source.rust"
ref.file_extensions                         # ["rs"]
ref.hidden                                  # bool
ref.first_line_match                        # Optional[str] (regex pattern)
ref.version                                 # int (1 or 2)
ref.variables                               # List[Tuple[str, str]]
repr(ref)                                   # "SyntaxReference(name='Rust', scope='source.rust', version=1)"
```

### SyntaxSetBuilder

```python
builder = syntect.SyntaxSetBuilder()
builder.add_from_folder("/path/to/syntaxes", False)
builder.add_plain_text_syntax()
ss = builder.build()
warnings = builder.warnings()               # List[str]
repr(builder)                               # "SyntaxSetBuilder(syntaxes=N)"
```

---

## Theme Management

### ThemeSet

```python
# Constructors
ts = syntect.ThemeSet()                    # Empty theme set
ts = syntect.ThemeSet.load_defaults()
ts = syntect.ThemeSet.from_dump("themes.themedump")

# Loading
ts.add_from_folder("/path/to/themes")       # Returns loaded theme names
theme = syntect.ThemeSet.load_theme_from_reader(plist_content)
ts.add_theme("custom", theme)
ts.add_theme_from_reader("custom-2", plist_content)
ts = syntect.ThemeSet.builder()               # Static: returns empty ThemeSet

# Access
theme = ts.get_theme("base16-ocean.dark")   # Optional[Theme]
fallback = ts.get_theme("missing", "base16-ocean.dark")
names = ts.theme_names()                      # List[str]
ts.to_dump("themes.themedump")              # Save to dump file

repr(ts)                                    # "ThemeSet(themes=N)"
```

### Theme

```python
theme = ts.get_theme("base16-ocean.dark")
theme.key                                   # "base16-ocean.dark"
theme.name                                  # "Base16 Ocean Dark"
theme.author                                # str
theme.settings                              # ThemeSettings
theme.scopes                                # List[ThemeItem]
repr(theme)                                 # "Theme(name='...', author='...')"
```

### ThemeSettings (31 readable properties)

```python
settings = theme.settings
settings = syntect.ThemeSettings()             # Construct an empty settings object
settings.background = syntect.Color.from_hex("#1E1E1E")
settings.foreground = syntect.Color.from_hex("#E0E0E0")
# Colors (Optional[Color])
settings.foreground
settings.background
settings.selection_background
settings.gutter_foreground
settings.gutter_background
settings.gutter                              # Alias for gutter_background
settings.selection                          # Alias for selection_background
settings.caret
settings.line_highlight
settings.misspelling
settings.minimap_border
settings.accent
settings.highlight
settings.find_highlight
settings.find_highlight_foreground
settings.selection_foreground
settings.selection_border
settings.inactive_selection
settings.inactive_selection_foreground
settings.bracket_contents_foreground
settings.brackets_foreground
settings.brackets_background
settings.tags_foreground

# CSS (Optional[str])
settings.popup_css
settings.phantom_css

# UnderlineOptions (Optional[UnderlineOption])
settings.bracket_contents_options
settings.brackets_options
settings.tags_options

# Guide colors
settings.guide
settings.active_guide
settings.stack_guide
settings.shadow

repr(settings)                              # "ThemeSettings(fg=..., bg=..., caret=...)"
# Color/CSS fields can be assigned; underline option fields remain read-only.
```

### ScopeSelectors

```python
selectors = syntect.ScopeSelectors.from_string("variable, constant")
selectors.to_string()                       # "variable, constant"
repr(selectors)                             # "ScopeSelectors('variable, constant')"
```

Selectors preserve comma/pipe unions, selector paths, and exclusions. They are
used directly by CSS generation rather than reconstructed from whitespace.

### ThemeItem

```python
item = theme.scopes[0]
item.scope                                  # Display string, e.g. "source.rust"
item.scope_selectors                        # ScopeSelectors object
item.foreground                             # Optional[Color]
item.background                             # Optional[Color]
item.font_style                             # u8 (bitmask)
item.style_modifier                         # StyleModifier
item.style                                  # StyleModifier
repr(item)                                  # "ThemeItem(scope='...', font=3)"

# Construct a theme item
item = syntect.ThemeItem(
    syntect.ScopeSelectors.from_string("comment"),
    syntect.StyleModifier(
        foreground=syntect.Color.from_hex("#6A7A3E"),
        font_style=syntect.FontStyle.from_string("italic"),
    ),
)
```

### Theme construction

```python
settings = syntect.ThemeSettings()
settings.background = syntect.Color.from_hex("#1E1E1E")
item = syntect.ThemeItem(
    syntect.ScopeSelectors.from_string("keyword, storage"),
    syntect.StyleModifier(foreground=syntect.Color.from_hex("#FF6B6B")),
)
theme = syntect.Theme(
    name="My Theme", author="me", settings=settings, scopes=[item]
)
ts = syntect.ThemeSet()
ts.add_theme("my-theme", theme)
```

### UnderlineOption

```python
uo = syntect.UnderlineOption.underline()
uo = syntect.UnderlineOption.stippled_underline()
uo = syntect.UnderlineOption.squiggly_underline()
uo = syntect.UnderlineOption.none_()         # Returns None
repr(uo)                                     # "UnderlineOption(underline)"
```

---

## VS Code themes and bundled themes

```python
# Auto-detect and parse VS Code JSON or JSONC
content = open("theme.json", encoding="utf-8").read()
assert syntect.is_vscode_theme(content)
theme = syntect.parse_vscode_theme(content)

# Register in the process-wide convenience registry
syntect.add_custom_theme("my-vscode-theme", content)
print(syntect.list_themes())
print(syntect.list_syntaxes())

# Load all .tmTheme and .json files from a directory
loaded = syntect.load_themes_from_folder("/path/to/themes")
```

The wheel includes 55 mordant themes under `syntect/themes/`, including
`Dracula`, `Nord`, `Monokai Extended`, `OneDark`, and `Solarized (dark)`. They
are registered automatically during import. The process-wide registry is
separate from caller-created `ThemeSet` objects.

## Assets compatibility API

```python
assets = syntect.Assets.from_binary()
assets.set_fallback_theme("Monokai Extended")
ss = assets.get_syntax_set()
ts = assets.get_theme_set()
theme = assets.get_theme("unknown-theme")  # Uses configured fallback
names = assets.theme_names()

# Alias and convenience constructor
assets2 = syntect.HighlightingAssets.from_binary()
assets3 = syntect.load_assets()
```

The API is compatible with the planned `syntect-assets` integration. The
current implementation uses fork-compatible defaults and the bundled
`Monokai Extended` fallback; the expanded bat grammar dataset is not yet
included.

---

## Metadata (tmPreferences)

```python
meta = ss.metadata                         # Optional[Metadata]
if meta:
    print(len(meta))                       # Number of metadata sets
    for mset in meta.sets:
        print(mset.selector_string)        # e.g., "source.python"
        item = mset.items
        print(item.line_comment)           # "//"
        print(item.indent_parens)          # True/False
        print(item.shell_variables)        # List[Tuple[str, str]]
        print(item.block_comment)          # Optional[Tuple[str, str]]
        # Additional fields:
        print(item.increase_indent_pattern)
        print(item.decrease_indent_pattern)
        print(item.bracket_indent_next_line_pattern)
        print(item.disable_indent_next_line_pattern)
        print(item.unindented_line_pattern)
```

---

## Highlighting

### Highlighter (stateless convenience API)

```python
hl = syntect.Highlighter(rust, theme)      # Takes SyntaxReference + Theme

# Highlight a single line
tokens = hl.highlight_line("fn main() {}", ss, ts)
# Returns: List[Tuple[Style, str]]

# Highlight all lines
all_tokens = hl.highlight_lines(code, ss, ts)
# Returns: List[List[Tuple[Style, str]]]

# Highlight a file (auto-detects syntax from extension)
file_tokens = hl.highlight_file("/path/to/file.rs", ss, ts)
# Returns: List[List[Tuple[Style, str]]]

# Save/restore state for incremental highlighting
state = hl.save_state(ss, ts)              # Returns HighlightState
hl2 = syntect.Highlighter.from_state(state, theme)  # Returns Highlighter

repr(hl)                                    # "Highlighter(syntax='Rust', theme='...')"
```

### HighlightLines (stateful API — upstream behavior)

```python
hl = syntect.HighlightLines(rust, ss, ts, "base16-ocean.dark")
# Constructor: (syntax_ref, syntax_set, theme_set, theme_name) — 4 args
# Unknown theme names fall back to InspiredGitHub when available.

# Direct Theme construction, without registering it in a ThemeSet:
hl_direct = syntect.HighlightLines.with_theme(rust, ss, theme)

tokens = hl.highlight_line("fn main() {}", ss)
# Returns: List[Tuple[Style, str]] — 2 args (line, syntax_set)
# Theme is baked in at construction
# State persists across calls — unterminated blocks carry forward

repr(hl)                                    # "HighlightLines()"
```

### HighlightState

```python
state = hl.save_state(ss, ts)
state.path_scope_stack                      # List[Scope]
state.styles_stack                          # List[Style]
state.path_scope_string                     # "source.rust" (space-separated)
state.styles_count                          # 1 (int)
repr(state)                                 # "HighlightState(path='...', styles=1)"

# Constructor (creates empty state)
empty = syntect.HighlightState()
```

### highlight_string (high-level convenience)

```python
result = syntect.highlight_string(
    code="fn main() {}",
    syntax="Rust",
    theme="base16-ocean.dark",
    syntax_set=ss,
    theme_set=ts
)
# Returns: HighlightResult

result.tokens                              # List[Tuple[Style, str]]
result.html                                # str (HTML snippet)
result.terminal_escaped                    # str (ANSI escapes)

# Output methods
html = result.as_html("if_different", None)
terminal = result.as_terminal_escaped(True)
latex = result.as_latex_escaped()

repr(result)                               # "HighlightResult(tokens=N, html_len=M, terminal_len=K)"
```

---

## Parsing

### ParseState (real stateful parser)

```python
ps = syntect.ParseState("Rust", ss)        # Constructor requires syntax_set
output = ps.parse_line("fn main() {}", ss) # Mutates state across calls
is_spec = ps.is_speculative()               # bool
name = ps.syntax_name                       # "Rust" (property)
repr(ps)                                    # "ParseState(syntax='Rust', speculative=False)"
```

### ParseLineOutput

```python
output = ps.parse_line("fn main() {}", ss)
output.ops                                 # List[Tuple[int, str]] — (position, "Push(...)"|"Pop(n)"|"Clear"|"Restore"|"Noop")
output.replayed                            # List[List[Tuple[int, str]]]
output.warnings                            # List[str]

op_type = output.get_op_type(0)            # "Push"|"Pop"|"Clear"|"Restore"|"Noop"
scope_op = output.get_scope_stack_op(0)    # ScopeStackOp object
repr(output)                               # "ParseLineOutput(ops=N, replayed=M, warnings=K)"
```

### Scope

```python
s = syntect.Scope("source.rust")           # Constructor
s = syntect.Scope.from_string("source.rust")  # Static method
s.to_string()                              # "source.rust"
s.len()                                    # 2 (number of scope atoms)
s.is_empty()                               # False
s.is_prefix_of(other)                      # True if s is a prefix of other
s == other_scope                           # True/False
repr(s)                                    # "Scope('source.rust')"
```

### ScopeStack

```python
stack = syntect.ScopeStack()               # Empty constructor
stack = syntect.ScopeStack.from_string("source rust")  # Static method
stack.push(syntect.Scope("meta"))
stack.pop()
stack.apply(syntect.ScopeStackOp.push(syntect.Scope("keyword")))
stack.as_string()                          # "source rust meta"
stack.len()                                # 3
stack.is_empty()                           # False
repr(stack)                                # "ScopeStack([source rust meta])"
```

### ScopeStackOp

```python
op = syntect.ScopeStackOp.push(syntect.Scope("source"))
op = syntect.ScopeStackOp.pop(1)
op = syntect.ScopeStackOp.clear_all()
op = syntect.ScopeStackOp.clear_top(2)
op = syntect.ScopeStackOp.restore()
op = syntect.ScopeStackOp.noop()
repr(op)                                   # "ScopeStackOp(Push)"|"ScopeStackOp(Pop, count=1)"|...
```

### MatchPower

```python
mp = syntect.MatchPower(0.5)               # Constructor
val = mp.value                              # 0.5 (property)
float(mp)                                   # 0.5 (__float__)
repr(mp)                                    # "MatchPower(0.5000)"
```

### ClearAmount

```python
ca = syntect.ClearAmount.all_()
ca = syntect.ClearAmount.top_n(3)
ca.kind                                     # "all"|"top_n" (property)
ca.value                                    # 0 (for all) or n (for top_n) (property)
repr(ca)                                    # "ClearAmount(all)"|"ClearAmount(top_n=3)"
```

### ContextId

```python
cid = syntect.ContextId(0, 42)             # Constructor
cid.syntax_index                            # 0 (property)
cid.context_index                           # 42 (property)
cid == other_cid                            # True/False
repr(cid)                                   # "ContextId(syntax=0, context=42)"
```

---

## Output Utilities

### Terminal Escapes

```python
# Module-level function
escaped = syntect.as_terminal_escaped(tokens, include_bg=True)
# include_bg: bool — whether to include background color

# On HighlightResult
result = syntect.highlight_string(code, "Rust", "base16-ocean.dark", ss, ts)
escaped = result.as_terminal_escaped(True)

# Alpha transparency is handled: foreground is blended with background
```

### HTML

```python
# Module-level function
html = syntect.as_html(tokens, "if_different", default_bg=None)
# include_bg: "no"|"false"|"0"|"yes"|"true"|"1"|anything_else
# default_bg: Optional[Color] — theme's default background

# On HighlightResult
html = result.as_html("if_different", None)
```

### LaTeX

```python
latex = syntect.as_latex_escaped(tokens)
# Returns \textcolor[RGB]{r,g,b}{text} with LaTeX escaping
# Spaces and newlines are elided when style doesn't change
```

### CSS

```python
# String-based class style
css = syntect.css_for_theme(theme, "spaced")
css = syntect.css_for_theme(theme, "spaced_prefixed")
css = syntect.css_for_theme(theme, "class_attribute")

# ClassStyle object (supports custom prefix)
cs = syntect.ClassStyle.spaced_prefixed("syn-")
css = syntect.css_for_theme_class(theme, cs)

# Alias
css = syntect.generate_css(theme, "spaced")
```

### Classed HTML

```python
# Convert tokens to class-based HTML
html = syntect.tokens_to_classed_spans(tokens, class_style)

# Convert a line with ops to classed spans
html, delta = syntect.line_tokens_to_classed_spans_py(line, ops, class_style)

# Convert styled tokens to inline HTML
html = syntect.styled_line_to_highlighted_html(tokens, "no")

# Full HTML for string
html = syntect.highlighted_html_for_string_py(code, rust, theme, ss, ts, "if_different", 1)

# HTML with line numbers
html = syntect.highlighted_html_at_line_and_column_number(code, rust, theme, ss, ts, 1)

# Alias
html = syntect.create_html_file(code, rust, theme, ss, ts)
```

### ClassedHTMLGenerator

```python
gen = syntect.ClassedHTMLGenerator(
    syntax_ref, syntax_set,
    syntect.ClassStyle.spaced_prefixed("syn-")
)
gen.parse_html_for_line("fn main() {")
gen.parse_html_for_line_which_includes_newline("    println!();\n")
html = gen.finalize()                    # Closes any open spans
repr(gen)                                # "ClassedHTMLGenerator()"
```

### ClassStyle

```python
cs = syntect.ClassStyle("spaced")            # String constructor
cs = syntect.ClassStyle("class_attribute")
cs = syntect.ClassStyle.spaced()
cs = syntect.ClassStyle.spaced_prefixed("syn-")
cs = syntect.ClassStyle.class_attribute()
repr(cs)                                     # "ClassStyle('spaced')"|"ClassStyle('spaced_prefixed')"|"ClassStyle('class_attribute')"
```

### IncludeBg

```python
ib = syntect.IncludeBg("no")                 # String constructor
ib = syntect.IncludeBg("yes")
ib = syntect.IncludeBg("if_different")
ib = syntect.IncludeBg.no()
ib = syntect.IncludeBg.yes()
ib = syntect.IncludeBg.if_different()
repr(ib)                                     # "IncludeBg('no')"|"IncludeBg('yes')"|"IncludeBg('if_different')"
```

---

## Utility Functions

### split_at

```python
left, right = syntect.split_at(tokens, position)
# Splits token list at character position.
# If split falls in middle of a token's text, that token is split.
```

### modify_range

```python
modified = syntect.modify_range(tokens, range_start, range_end, new_style)
# Overrides style for tokens in [range_start, range_end) character range.
# Splits tokens as needed to fit the range.
```

### lines_with_endings

```python
# Create iterator
iterator = syntect.lines_with_endings(content)

# Iterate
for line, ending in syntect.lines_with_endings(content):
    print(repr(line), repr(ending))
# Output: ('hello', '\n') ('world', '\r\n') ('last', '')

# LinesWithEndings is a class with __iter__ and __next__
```

---

## Dump / Serialization

```python
# Syntax set
syntect.dump_syntax_set(ss, "syntaxes.packdump")
ss = syntect.load_syntax_set("syntaxes.packdump")

# Theme set
syntect.dump_theme_set(ts, "themes.themedump")
ts = syntect.load_theme_set("themes.themedump")

# Also available as methods
ss.to_dump("syntaxes.packdump")
ss = syntect.SyntaxSet.from_dump("syntaxes.packdump")
ts.to_dump("themes.themedump")
ts = syntect.ThemeSet.from_dump("themes.themedump")
```

---

## Error Handling

```python
import syntect

# 1. LoadingError — file loading failures
try:
    ss = syntect.SyntaxSet.load_from_folder("/missing", True)
except (syntect.LoadingError, OSError) as e:
    print(f"Load error: {e}")

# 2. ParsingError — syntax parse failures
try:
    builder = syntect.SyntaxSetBuilder()
    ss = builder.build()
except syntect.ParsingError as e:
    print(f"Parse error: {e}")

# 3. DumpError — dump file failures
try:
    ss = syntect.load_syntax_set("/missing.packdump")
except (syntect.DumpError, OSError) as e:
    print(f"Dump error: {e}")

# 4. ParseSyntaxError — custom parse error
try:
    raise syntect.ParseSyntaxError("bad parse")
except syntect.ParseSyntaxError as e:
    print(f"ParseSyntaxError: {e}")

# 5. ValueError — user input validation
try:
    syntect.Color.from_hex("ZZZZZZ")
except ValueError as e:
    print(f"Invalid hex: {e}")

# 6. get_theme returns None for missing theme (no exception)
theme = ts.get_theme("nonexistent")
if theme is None:
    print("Theme not found")
```

---

## API Gotchas

| Issue | Solution |
|---|---|
| `Highlighter.highlight_line()` takes 3 args `(line, ss, ts)` | `HighlightLines.highlight_line()` takes 2 args `(line, ss)` |
| `as_html()` requires `default_bg` parameter | Pass `None` for no default |
| `rust.variables` is `List[Tuple[str, str]]` | Not a `Dict[str, str]` |
| `MatchPower.value` is a property | Not a method: use `mp.value`, not `mp.value()` |
| `ClearAmount.kind` / `ClearAmount.value` are properties | Not methods |
| `ContextId.syntax_index` / `context_index` are properties | Not methods |
| `save_state()` requires `ss, ts` arguments | Not no-arg: `hl.save_state(ss, ts)` |
| `is_prefix_of()` semantics | `parent.is_prefix_of(child)` — parent checks if child starts with it |
| `Color.to_hex()` returns uppercase | `#FF0000`, not `#ff0000` |
| `get_theme()` returns `None` for missing | Pass `fallback="theme-name"` for ThemeSet fallback lookup |
| `HighlightLines` unknown theme | Falls back to `InspiredGitHub` when available |
| `add_custom_theme()` registry | Process-wide registry; use `ThemeSet.add_theme()` for an isolated set |
| `ClassedHTMLGenerator` constructor order | `(syntax_ref, syntax_set, class_style)` — order matters |
| `tokens_to_classed_spans()` returns HTML string | Not a list of tuples |
| `lines_with_endings()` returns iterator | Iterate with `for line, ending in syntect.lines_with_endings(content)` |
| `HighlightResult.terminal_escaped` is a property | Access as `result.terminal_escaped`, not a method |
| `HighlightState` is a partial implementation | Stores `path_scope_stack` + `styles_stack`, not full upstream state |
| `from_state()` ignores saved scope stack | Creates new blank `Highlighter` with theme config |
| `SyntaxSet.new()` creates empty set | Use `load_defaults()` or `load_from_folder()` for real syntaxes |
| `ThemeSet.new()` creates empty set | Use `load_defaults()` or `from_dump()` for real themes |
| `ScopeStackOp.clear_all()` vs `clear_top(n)` | `clear_all()` clears everything; `clear_top(n)` clears top N |
| `ParseState.parse_line()` mutates state | State persists across calls — call in order for context-sensitive parsing |
| `lines_with_endings` is a class, not just a function | `syntect.LinesWithEndings(content)` creates an iterable |
| `ScopeRangeIterator` yields `(start, end, scope)` | `start`/`end` are character positions in the line |
| `ScoredStyle` has separate color components | `foreground_r`, `foreground_g`, `foreground_b`, `foreground_a` + `foreground_score` |
| `HighlightLines` constructor takes `theme_set` + `theme_name` | Not a `Theme` object — resolves internally |
| `css_for_theme` uses string class style | `css_for_theme_class` uses `ClassStyle` object with prefix support |
| `as_terminal_escaped(include_bg=True)` blends alpha | Foreground is alpha-blended with background before output |
| `as_html("if_different")` needs `default_bg` | Without `default_bg`, all backgrounds are included |
| `SyntaxSetBuilder.warnings()` vs `SyntaxSet.warnings()` | Builder warnings are from loading; SyntaxSet warnings are from linking |
| `ThemeItem.scope` is a display string | Use `ThemeItem.scope_selectors` for the parsed selector object |
| `ThemeItem.style` and `.style_modifier` | Both return `StyleModifier` objects |
| `Metadata` may be `None` | `load_defaults()` doesn't load `.tmPreferences` by default |
| `PyClassStyle("spaced_prefixed")` has no prefix | Use `spaced_prefixed("custom-")` for custom prefix |
| `IncludeBg("false")` maps to kind=0 | `IncludeBg("false")` is same as `IncludeBg("no")` |

---

## Module Index

| Module | Classes | Functions |
|---|---|---|
| Core | `Color`, `FontStyle`, `Style`, `StyleModifier` | — |
| Syntax | `SyntaxSet`, `SyntaxReference`, `SyntaxSetBuilder` | — |
| Theme | `ThemeSet`, `Theme`, `ThemeSettings`, `ThemeItem`, `ScopeSelectors`, `UnderlineOption` | `is_vscode_theme`, `is_plist_theme`, `parse_vscode_theme`, `add_custom_theme`, `load_themes_from_folder`, `list_themes`, `list_syntaxes` |
| Assets | `Assets`, `HighlightingAssets` | `load_assets` |
| Metadata | `Metadata`, `MetadataSet`, `MetadataItem` | — |
| Highlighting | `Highlighter`, `HighlightState`, `HighlightLines`, `HighlightResult`, `ScoredStyle` | `highlight_string` |
| Parsing | `ParseState`, `ParseLineOutput`, `Scope`, `ScopeStack`, `ScopeStackOp`, `MatchPower`, `ClearAmount`, `ContextId` | — |
| HTML/Output | `ClassedHTMLGenerator`, `ClassStyle`, `IncludeBg`, `ScopeRangeIterator` | `as_html`, `as_terminal_escaped`, `as_latex_escaped`, `css_for_theme`, `css_for_theme_class`, `generate_css`, `highlighted_html_for_string_py`, `create_html_file`, `highlighted_html_at_line_and_column_number`, `tokens_to_classed_spans`, `line_tokens_to_classed_spans_py`, `styled_line_to_highlighted_html` |
| Utilities | `LinesWithEndings` | `split_at`, `modify_range`, `lines_with_endings` |
| Dumps | — | `dump_syntax_set`, `load_syntax_set`, `dump_theme_set`, `load_theme_set` |
| Errors | `LoadingError`, `ParsingError`, `DumpError`, `ParseSyntaxError` | — |

---

*Updated: 2026-08-06 · syntect-py 5.3.0 · P1–P4.5 parity APIs implemented · 346 tests passing · PyPI wheel/sdist workflows configured · expanded bat grammar data remains outstanding.*
