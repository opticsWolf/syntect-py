# syntect-py Upgrade Plan — Feature Parity with mordant's syntect Integration

**Status:** Implementation in progress (P1–P4.5 implemented; expanded P5 grammar data remains)
**Scope:** Review `syntect-py` against the way `mordant` uses `syntect`, then update the phased plan for closing the gaps.
**Reviewed repos:**
- `syntect-py` — fork of `syntect` 5.3.0 with a PyO3 0.29 Python binding (`pyext/`)
- `mordant` — CommonMark/GFM Markdown parser (crate `rushdown`) with a PyO3 Python binding (`mordant-py/`) that integrates `syntect` 5.3.0 + `syntect-assets` 0.23.6

**Last reviewed:** 2026-08-06

### Implementation log

The first implementation pass has landed in `pyext/`:

- **P1 complete:** `SyntaxSet.find_syntax_by_token` and `find_syntax_by_first_line` are exported and stubbed.
- **P2 complete:** themes can be parsed from plist strings, inserted/replaced by name, and loaded-folder names are returned.
- **P3 complete:** `ScopeSelectors`, theme/settings/item constructors and setters, combined `FontStyle.from_string`, and selector-preserving CSS generation are available.
- **P4 core complete:** VS Code JSON/JSONC conversion, plist/VS Code detection, custom-theme registration, and module-level syntax/theme listing are available. The registry is process-wide and intentionally separate from caller-owned `ThemeSet` instances.
- **P6 core complete:** `HighlightLines.with_theme` and `ThemeSet.get_theme(..., fallback=...)` are available; the legacy `HighlightLines` constructor and `highlight_string` convenience path fall back to `InspiredGitHub`.
- **P4.5 complete:** the 55-theme mordant collection is vendored under `pyext/syntect/themes/`, included in wheels, and automatically registered at `import syntect` through the mixed Python/Rust package wrapper. `load_themes_from_folder` remains available for additional theme directories.
- **P5 API scaffold:** `Assets`/`HighlightingAssets` now expose `from_binary`, configurable fallback lookup, syntax/theme-set access, and the bundled `Monokai Extended` fallback theme. The published `syntect-assets` dump was tested but is not wire-compatible with this fork, so it is deliberately not used.
- **Still outstanding:** vendoring/converting bat's expanded grammar data for the full P5 asset parity target.

---

## 1. Where mordant uses syntect

mordant's core Rust crate (`mordant/src/`) does **not** use syntect. All syntect usage is inside the Python binding crate (`mordant-py/src/`) and the package-level Python layer (`mordant-py/mordant/__init__.py`):

| File | Role |
|------|------|
| `mordant-py/src/highlighter.rs` | `Highlighter`/`HighlighterMode`, `highlight_code`, `render_attribute_mode`, `render_class_mode`, `detect_syntax_from_content`, `load_builtin_themes`, `add_custom_theme`, `list_syntaxes`, `list_themes` |
| `mordant-py/src/vscode_theme.rs` | Parse VSCode JSON/JSONC themes and convert them into `syntect::highlighting::Theme` |
| `mordant-py/src/mermaid_theme.rs` | Read `Color`, `ThemeSettings`, `ThemeItem`, `Theme` fields to derive Mermaid color schemes |
| `mordant-py/src/themes.rs` | Placeholder for embedded-theme helpers; actual embedded themes are loaded by `mordant/__init__.py` |
| `mordant-py/mordant/__init__.py` | Loads bundled `.tmTheme`/`.json` themes from the package `themes/` directory at import time |
| `mordant-py/Cargo.toml` | `syntect = { version = "5.3.0", default-features = false, features = ["default-fancy"] }`, `syntect-assets = "0.23.6"`, `jsonc-parser` |

The highlighter uses **syntect-assets** (`HighlightingAssets::from_binary()`, `set_fallback_theme("Monokai Extended")`, `get_syntax_set()`) for bat's updated syntaxes, falling back to `SyntaxSet::load_defaults_newlines()` if assets fail. Themes are a mix of syntect's built-in defaults, custom themes shipped in the wheel, and user-provided themes from `.mordant/themes/`.

---

## 2. Coverage matrix: mordant's syntect usage vs syntect-py

Legend: ✅ covered · ⚠️ partial / different API · ❌ missing

| # | syntect API / feature used by mordant | Where in mordant | syntect-py status |
|---|----------------------------------------|------------------|-------------------|
| 1 | `SyntaxSet::load_defaults_newlines()` | `highlighter.rs` fallback | ✅ `SyntaxSet.load_defaults(newlines=True)` |
| 2 | `SyntaxSet::find_syntax_by_token(&lang)` | `highlighter.rs` lookup cascade | ❌ not exposed (exists in fork `src/parsing/syntax_set.rs:225`) |
| 3 | `SyntaxSet::find_syntax_by_extension(&ext)` | `highlighter.rs` | ✅ |
| 4 | `SyntaxSet::find_syntax_plain_text()` | `highlighter.rs` | ✅ |
| 5 | `SyntaxSet::find_syntax_by_first_line(&line)` | `highlighter.rs` shebang/Emacs/XML detection | ❌ not exposed (exists in fork `src/parsing/syntax_set.rs:242`) |
| 6 | `SyntaxSet::syntaxes()` | `highlighter.rs` `list_syntaxes` | ✅ |
| 7 | `easy::HighlightLines::new(syntax, theme)` | `highlighter.rs` | ⚠️ `HighlightLines` ctor takes `(syntax_ref, syntax_set, theme_set, theme_name)` and re-resolves by name instead of accepting a `Theme` object |
| 8 | `easy::HighlightLines::highlight_line(line, ss)` | `highlighter.rs` | ✅ |
| 9 | `ThemeSet::load_defaults()` | `highlighter.rs` | ✅ |
| 10 | `ThemeSet::load_from_reader(&mut Cursor)` (single `.tmTheme` from string) | `highlighter.rs`, `vscode_theme.rs`, `add_custom_theme` | ❌ only folder-based `ThemeSet.add_from_folder` exists |
| 11 | `ts.themes.get(name).unwrap_or(default)` fallback | `highlighter.rs` (`"InspiredGitHub"`) | ⚠️ `ThemeSet.get_theme(key)` returns `None`; no fallback argument |
| 12 | `theme.settings.background` | `highlighter.rs` | ✅ |
| 13 | `html::ClassedHTMLGenerator::new_with_class_style(..., ClassStyle::Spaced)` | `highlighter.rs` | ✅ `ClassedHTMLGenerator(syntax_ref, syntax_set, class_style)` |
| 14 | `parse_html_for_line_which_includes_newline` + `finalize()` | `highlighter.rs` | ✅ |
| 15 | `html::ClassStyle::Spaced` | `highlighter.rs` | ✅ |
| 16 | `html::IncludeBackground::No` | `highlighter.rs` | ✅ `IncludeBg.no()` |
| 17 | `html::styled_line_to_highlighted_html` | `highlighter.rs` | ✅ |
| 18 | `util::LinesWithEndings` | `highlighter.rs` | ✅ (`lines_with_endings` returns `(line, ending)` tuples) |
| 19 | `syntect_assets::HighlightingAssets::{from_binary, set_fallback_theme, get_syntax_set}` | `highlighter.rs` | ❌ no `Assets`/`HighlightingAssets` class |
| 20 | `highlighting::Color` fields/hex | `vscode_theme.rs`, `mermaid_theme.rs` | ✅ `Color(r,g,b,a)`, `from_hex`, `to_hex` |
| 21 | `highlighting::FontStyle` from `"bold italic underline"` strings | `vscode_theme.rs` | ⚠️ only `FontStyle(bits)`; no `from_string` parser |
| 22 | `highlighting::ScopeSelectors::from_str` | `vscode_theme.rs`, `mermaid_theme.rs` | ❌ internal helper only (`pyext/src/html.rs:scope_string_to_selectors`); no public class |
| 23 | `StyleModifier { foreground, background, font_style }` construction | `vscode_theme.rs` | ✅ `StyleModifier.__new__` exists |
| 24 | `ThemeItem { scope, style }` construction | `vscode_theme.rs` | ❌ `PyThemeItem` is read-only |
| 25 | `Theme { name, author, scopes, settings }` construction | `vscode_theme.rs` | ❌ `PyTheme` is read-only |
| 26 | `ThemeSettings::default()` + field mutation | `vscode_theme.rs` | ❌ `PyThemeSettings` is read-only |
| 27 | `ts.themes.insert(name, theme)` | `highlighter.rs` `add_custom_theme` | ❌ no `ThemeSet.add_theme(name, theme)` |
| 28 | Reading `Theme`/`ThemeItem`/`Color` for Mermaid derivation | `mermaid_theme.rs` | ✅ |
| 29 | `ThemeItem.scope` as a real `ScopeSelectors` object | `vscode_theme.rs`, `mermaid_theme.rs`, `html.rs` | ⚠️ `ThemeItem.scope` is a plain string; multi-scope/comma-separated selectors are not preserved and CSS generation is broken for them |
| 30 | `FontStyle` bit handling in CSS/attribute rendering | `highlighter.rs` `render_attribute_mode` | ⚠️ `css_for_theme` uses an `if/else` chain that only emits one of bold/italic/underline per item |
| 31 | VSCode JSON/JSONC theme detection & conversion | `vscode_theme.rs`, `add_custom_theme`, `mordant/__init__.py` | ❌ no JSONC/VSCode theme converter in `syntect-py` |
| 32 | Directory scanning for user/package themes (`.tmTheme` + `.json`) | `highlighter.rs`, `mordant/__init__.py` | ❌ no `load_builtin_themes` or equivalent |
| 33 | Module-level `list_themes()`, `list_syntaxes()`, `add_custom_theme()` | `highlighter.rs`, `mordant/__init__.py` | ⚠️ only class-level `SyntaxSet.syntaxes()` and `ThemeSet.theme_names()` exist |

**Summary:** of 33 usages, ~14 are fully covered, 6 are partial, and **13 are missing** (including the new CSS/scope-selector and rendering items). The missing items cluster into 6 feature groups (see §3).

---

## 3. Gap analysis (what to add)

### G1 — Syntax lookup primitives: `find_syntax_by_token` and `find_syntax_by_first_line`

mordant's language-detection path depends on these two:

- `highlight_code`: `ps.find_syntax_by_token(&lang).or_else(|| ps.find_syntax_by_extension(&lang)).unwrap_or_else(plain_text)`
- `detect_syntax_from_content`: `ps.find_syntax_by_first_line(first_line)` for `#!/usr/bin/env …` shebangs, `-*- Mode: C -*-` Emacs modelines, and `<?xml …?>` declarations.

Both methods already exist in the Rust fork (`src/parsing/syntax_set.rs:225` and `:242`) but have **no `#[pyfunction]`/`#[pymethods]` export** and are absent from `syntect.pyi`. A Python user cannot reproduce mordant's lookup cascade.

### G2 — Theme loading from content: `ThemeSet.load_from_reader`

mordant registers themes from **file contents**, not paths:

- `load_builtin_themes()` scans `~/.mordant/themes/` and `%APPDATA%/mordant/themes/` for `*.tmTheme`, then calls `ThemeSet::load_from_reader(&mut Cursor::new(content))`.
- `add_custom_theme(name, content)` does the same for a string.

syntect-py only supports folder-based loading (`ThemeSet.add_from_folder`). There is no way to load a `.tmTheme` plist from a Python string or register a constructed theme under an arbitrary name.

### G3 — Theme authoring API (prerequisite for VSCode JSON themes)

mordant's `vscode_theme.rs` builds syntect themes **struct-by-struct**:

```text
ThemeSettings::default()
  → mutate color fields
  → ScopeSelectors::from_str("*" | scope)
  → StyleModifier { … }
  → ThemeItem { scope, style }
  → Theme { name, author, scopes, settings }
  → ts.themes.insert(name, theme)
```

syntect-py exposes `StyleModifier` construction, but everything else (`ScopeSelectors`, `ThemeSettings`, `ThemeItem`, `Theme`, and mutating `ThemeSet`) is read-only. The full VSCode-JSON conversion pipeline can only be ported after these construction APIs exist.

Additionally, `ThemeItem.scope` is currently stored as a plain whitespace-joined string, and the CSS generator in `html.rs` re-parses it with a naive helper that splits on whitespace and treats each token as a separate selector. This breaks the multi-scope/comma-separated selectors that real VSCode themes use (e.g. `"variable, constant"` or `"entity.name.function, support.function"`).

### G4 — Assets module (bat's syntaxes & themes, `syntect-assets` equivalent)

The single biggest feature gap. mordant uses `syntect-assets` to embed bat's current grammar set and theme collection, with a configurable fallback theme (`set_fallback_theme("Monokai Extended")`).

syntect-py embeds only the stock syntect 5.3.0 default dumps (`default-syntaxes` / `default-themes` features) — older grammars, ~190 syntaxes. There is:

- no `HighlightingAssets`-equivalent Python class (`from_binary()`, `set_fallback_theme()`, `get_syntax_set()`),
- no way to obtain bat's updated grammar set,
- no fallback-theme concept.

### G5 — `HighlightLines` constructor parity + theme fallback

mordant calls `HighlightLines::new(syntax, theme)` with a **theme object**. syntect-py's `HighlightLines.__new__` requires `(syntax_ref, syntax_set, theme_set, theme_name)` and re-resolves by name, so a ported mordant-style caller must keep a parallel name string or use `PyHighlighter` instead.

mordant also silently falls back to `"InspiredGitHub"` when a theme name is unknown; syntect-py currently raises `PyValueError`.

### G6 — VSCode JSON/JSONC theme conversion and directory loading

mordant exposes `add_custom_theme(name, content)` which auto-detects plist XML vs VSCode JSON (including JSONC with comments) and registers the resulting theme. mordant's `__init__.py` then loads all `.tmTheme` and `.json` files from the package `themes/` directory at import time.

syntect-py has none of this: no JSONC parser, no VSCode theme converter, no directory scanner, and no module-level `add_custom_theme`/`list_themes`/`list_syntaxes` convenience functions.

### G7 — Bundled theme collection

mordant ships **~55 themes** (a mix of `.tmTheme` and `.json` files) in `mordant/mordant-py/mordant/themes/` and registers them at import time via `mordant/__init__.py::_load_embedded_themes()`. syntect-py has no bundled theme folder, so users start with only the syntect built-in themes. The same theme list as mordant cannot be achieved without copying/embedding this collection.

---

## 4. Phased implementation plan

**Ordering rationale:** expose the existing Rust functions first (cheap wins), then add construction APIs, then theme loading/conversion, then the assets module (largest chunk), then parity polish. Each phase should end with a green build + passing `pytest` + updated `syntect.pyi` stubs.

### Phase P1 — Expose syntax lookup primitives (G1)

**Files:** `pyext/src/syntax_set.rs`, `pyext/syntect.pyi`, `pyext/tests/test_syntect.py`

- Add to `#[pymethods] impl PySyntaxSet`:
  - `pub fn find_syntax_by_token(&self, token: &str) -> Option<PySyntaxReference>` → `self.inner.find_syntax_by_token(token).map(syntax_ref_to_py)`
  - `pub fn find_syntax_by_first_line(&self, line: &str) -> Option<PySyntaxReference>` → `self.inner.find_syntax_by_first_line(line).map(syntax_ref_to_py)`
- Update `syntect.pyi` with `SyntaxSet.find_syntax_by_token` and `SyntaxSet.find_syntax_by_first_line`.
- Tests: token lookup (`"py"` → Python, `"rs"` → Rust), first-line lookup (`"#!/usr/bin/env node"`, `"-*- Mode: C -*-"`), and `None` for misses; mirror the fork tests at `src/parsing/syntax_set.rs:1397-1410`.

**Exit criteria:** mordant's lookup cascade `find_syntax_by_token → find_syntax_by_extension → find_syntax_plain_text` is reproducible in Python.

### Phase P2 — Theme loading from string content and mutation (G2)

**Files:** `pyext/src/theme_set.rs`, `pyext/syntect.pyi`, `pyext/tests/test_syntect.py`

- Add `ThemeSet.load_theme_from_reader(content: str) -> Theme` staticmethod (wraps `ThemeSet::load_from_reader(&mut Cursor::new(content))` with error → `PyValueError`).
- Add `ThemeSet.add_theme(name: str, theme: Theme)` method (mutating `self.inner.themes`).
- Add `ThemeSet.add_theme_from_reader(name: str, content: str)` convenience (load + insert in one call).
- Update `ThemeSet.add_from_folder` to return the list of newly loaded theme names instead of an empty `Vec` (matches mordant's `load_builtin_themes` behavior).
- Update stub + tests (round-trip a small `.tmTheme` plist string; register and retrieve; list names).

**Exit criteria:** mordant's `load_builtin_themes()` / `add_custom_theme()` plist path can be re-implemented in Python one-to-one.

### Phase P3 — Theme authoring API + scope-selector fix (G3)

**Files:** `pyext/src/style.rs`, `pyext/src/theme_set.rs`, `pyext/src/html.rs`, `pyext/src/lib.rs`, `pyext/syntect.pyi`, tests

- **`ScopeSelectors` pyclass** (new): expose the real syntect `ScopeSelectors` type:
  - `ScopeSelectors.from_string(s: str) -> ScopeSelectors` (wraps `ScopeSelectors::from_str`, raises `PyValueError` on invalid selectors).
  - `to_string()` and `__repr__`.
  - No `Box::leak`; store the Rust object directly.
- **`PyThemeSettings`**: add `#[new] pub fn new() -> Self` (empty `ThemeSettings::default()`) and `#[setter]`s for all fields mordant maps: `foreground`, `background`, `caret`, `line_highlight`, `find_highlight`, `find_highlight_foreground`, `accent`, `gutter`, `gutter_foreground`, `selection`, `inactive_selection`, `inactive_selection_foreground`, `highlight`, `guide`, `active_guide`, `stack_guide`, `tags_foreground`, `brackets_foreground`, `shadow`. Keep the existing getters.
- **`PyThemeItem`**: add `#[new] pub fn new(scope: &ScopeSelectors, style: &StyleModifier) -> Self`; keep the existing `style`/`style_modifier` getters. Change or add a `scope_selectors` property returning the real `ScopeSelectors` object; keep the string `scope` getter for backward compatibility if possible.
- **`PyTheme`**: add `#[new] pub fn new(name: Option<String>, author: Option<String>, settings: &PyThemeSettings, scopes: Vec<PyThemeItem>) -> Self`.
- **`PyFontStyle`**: add `#[staticmethod] from_string(s: &str) -> Option<FontStyle>` parsing space/comma-separated `"bold"`, `"italic"`, `"underline"` (syntect 5.x bits: `BOLD=1`, `UNDERLINE=2`, `ITALIC=4`).
- **CSS rendering fix**: update `css_for_theme` / `css_for_theme_class` to use the real `ScopeSelectors` object from `ThemeItem.scope_selectors` instead of the naive whitespace parser. Also handle combined font styles (bold + italic + underline) instead of an exclusive `if/else` chain.
- Update `.pyi` + tests: build a theme entirely from Python primitives, register via `add_theme`, retrieve, verify `get_theme` reflects settings/scopes, and verify CSS generation for multi-scope selectors.

**Exit criteria:** `vscode_theme.rs`'s `vscode_theme_to_syntect` can be ported verbatim to Python, and CSS generation no longer breaks on comma-separated scope selectors.

### Phase P4 — VSCode JSON/JSONC theme conversion and directory loading (G6)

**Files:** `pyext/src/vscode_theme.rs` (recommended), `pyext/src/lib.rs`, `pyext/syntect.pyi`, `pyext/tests/test_syntect.py`, and optionally a Python package-level helper

- Add a Rust-side VSCode JSON/JSONC converter in `pyext/src/vscode_theme.rs` (mirrors mordant's `vscode_theme.rs`). Add `jsonc-parser` as a dependency in `pyext/Cargo.toml`.
- Expose to Python:
  - `syntect.is_vscode_theme(content: str) -> bool`
  - `syntect.is_plist_theme(content: str) -> bool`
  - `syntect.parse_vscode_theme(content: str) -> Theme`
  - `syntect.add_custom_theme(name: str, content: str) -> None` (auto-detects format and registers into a global/process-level `ThemeSet`, or into a caller-provided `ThemeSet`)
  - `syntect.list_themes() -> List[str]` (module-level, from the global set)
  - `syntect.list_syntaxes() -> List[str]` (module-level, from the global `SyntaxSet`)
- Provide a Python helper to scan a directory (package `themes/` or user `~/.syntect/themes/`) for `.tmTheme` + `.json` files and register them. This is the equivalent of mordant's `mordant/__init__.py::_load_embedded_themes()`.
- Tests: convert the fixtures from `mordant/mordant-py/tests/test_vscode_theme.py` (single-scope, multi-scope, named colors, JSONC comments) and verify the themes highlight correctly; verify `add_custom_theme` overwrites and is retrievable.

**Exit criteria:** a VSCode JSON theme file (with comments and named colors) can be loaded and used for highlighting with identical results to mordant's Rust path.

### Phase P4.5 — Bundle mordant's theme folder (G7)

**Files:** copy `D:/User/Documents/Python/mordant/mordant-py/mordant/themes/` → `syntect-py/pyext/syntect/themes/` (or `syntect-py/pyext/themes/`); update `pyext/pyproject.toml`; add Python loader; `pyext/syntect.pyi`; tests

- Copy the entire `mordant/mordant-py/mordant/themes/` directory (55 files: `.tmTheme` and `.json`). The collection includes themes such as `1337`, `Dracula`, `Nord`, `Monokai Extended`, `OneDark`, `Solarized (dark)`, `zenburn`, etc.
- Package the folder as wheel data. Two options:
  - **Option A (mixed Rust/Python package):** create a proper Python package `syntect/` with `syntect/__init__.py` that imports the Rust extension (e.g. `from syntect._syntect import *`) and then loads the bundled themes. The themes live in `syntect/themes/`. This matches mordant's layout and is the recommended approach.
  - **Option B (include data files):** keep the single `syntect` extension module and use `[tool.maturin] include = [...]` to ship the themes, then locate them with `importlib.resources` at runtime.
- Add a Python loader (called from `syntect/__init__.py` or a dedicated helper) that scans the bundled themes directory and registers each `.tmTheme` and `.json` file via the new `syntect.add_custom_theme(name, content)` function.
- Update `pyext/syntect.pyi` to reflect any new package-level functions (e.g. `load_bundled_themes`, `add_custom_theme`).
- Add license/provenance notes for the vendored themes (see mordant's `ThirdPartyNotices.md`).

**Tests:** verify that `syntect.list_themes()` includes names like `Dracula`, `Nord`, `Monokai Extended`, `1337`, `OneDark`; total theme count is ≥ built-in count + 55; each bundled theme can be retrieved via `ThemeSet.get_theme` and used for highlighting.

**Exit criteria:** a fresh `import syntect` registers all 55 bundled themes, and they are indistinguishable from mordant's theme list.

### Phase P5 — Assets module (G4) — largest phase

**Files:** `Cargo.toml` (root), `pyext/Cargo.toml`, new `src/assets/` or `pyext/src/assets.rs`, `pyext/syntect.pyi`, tests, build scripts

**Options:**

- **A. Add `syntect-assets` crate dependency.** Fastest to write, but the crate depends on the *published* `syntect` crate, so it must be patched (`[patch.crates-io]`) to use the local fork. If the patch is not applied correctly, it brings in a second full `syntect` copy and may pull `regex-onig`/`bzip2` baggage.
- **B. Vendor the data and write a small assets module (recommended).** The real value is the data (bat's `assets/` folder: `.sublime-syntax` tree + `.tmTheme`s, MIT-licensed). Vendor the data into the fork (e.g. `assets/` + build-time packing into `.packdump`/`.themedump`, or `include_bytes!`), then implement a minimal `HighlightingAssets` equivalent:
  - `Assets.from_binary() -> Assets` (embedded bat syntaxes+themes)
  - `assets.set_fallback_theme(name: str)` (default `"Monokai Extended"`)
  - `assets.get_syntax_set() -> SyntaxSet` (load `.sublime-syntax` tree with `SyntaxSetBuilder`; fall back to `SyntaxSet::load_defaults_newlines()` on failure — exactly mordant's error path)
  - `assets.get_theme(name: str) -> Optional[Theme]` and/or `assets.get_theme_set() -> ThemeSet`
  - expose as `syntect.Assets` / `syntect.HighlightingAssets`.

**Implementation steps (Option B):**

1. Add bat's `assets/syntaxes/` and `assets/themes/` to the fork (or fetch them as a git submodule).
2. At build time, pack them into `.packdump` and `.themedump` files (or keep them loose and load with `SyntaxSetBuilder`/`ThemeSet::load_from_reader`).
3. Add a Python-exposed `Assets` class wrapping the loaded data.
4. Add a module-level `syntect.load_assets()` returning a cached `(SyntaxSet, ThemeSet)` pair, mirroring mordant's global `SYNTAX_SET`/`THEME_SET`.
5. Wire fallback-theme semantics into highlighter/theme lookups so an unknown theme name resolves to the configured fallback instead of raising.

**Tests:** `Assets.from_binary()` loads; syntax count ≥ bat's grammar count; fallback theme is honored; unknown theme name resolves to fallback; `list_syntaxes()` reports the bat grammar set.

**Exit criteria:** mordant's `ASSETS`/`SYNTAX_SET`/`THEME_SET` static setup is reproducible in Python, and the module-level `list_syntaxes()`/`list_themes()` return the bat + custom set.

### Phase P6 — `HighlightLines` parity + theme fallback (G5)

**Files:** `pyext/src/highlighter.rs`, `pyext/src/theme_set.rs`, `pyext/syntect.pyi`, tests

- Add a `HighlightLines.with_theme(syntax_ref, syntax_set, theme: Theme)` classmethod that constructs `syntect::easy::HighlightLines::new(syntax, &theme.inner)` directly. Keep the existing `(syntax_ref, syntax_set, theme_set, theme_name)` constructor for backward compatibility.
- Add fallback handling to `ThemeSet.get_theme(key, fallback: Optional[str] = None) -> Optional[Theme]`. When `fallback` is provided and the key is missing, return the fallback theme.
- Add fallback handling to the highlighter constructors: when `theme_name` is not found, resolve to the configured fallback (e.g. `"InspiredGitHub"`) instead of raising `PyValueError`.
- Tests: construct `HighlightLines` from a `Theme` object; verify unknown theme name returns the fallback; verify the fallback param works on `ThemeSet.get_theme`.

**Exit criteria:** mordant's `HighlightLines::new(syntax, theme)` call and its silent fallback behavior are reproducible in Python.

---

## 5. Testing strategy

- Extend `pyext/tests/test_syntect.py` per phase (P1–P6 and P4.5 exit criteria above).
- Add a dedicated parity test module `pyext/tests/test_mordant_parity.py` that reproduces mordant's highlighter behavior in Python:
  1. mordant lookup cascade (`token → extension → plain text`) on a corpus of language ids.
  2. content detection via first line (shebang, Emacs modeline, `<?xml`).
  3. attribute-mode HTML output shape (`<pre style="background-color:…"><code class="language-…">` + per-line `styled_line_to_highlighted_html`).
  4. classed-mode HTML via `ClassedHTMLGenerator` + `ClassStyle.spaced`.
  5. VSCode JSON theme conversion equivalence on shared fixtures from mordant.
  6. CSS generation for multi-scope/comma-separated selectors (regression guard for the current whitespace-split bug).
- Keep `syntect.pyi` in sync after every phase. A CI step comparing stub symbols to registered `#[pyfunction]`/`#[pymethods]` is a good follow-up (prior art in `docs/IMPROVEMENT_PLAN.md`).

---

## 6. Out of scope / notes

- **Language-detection heuristics** (`detect_syntax_from_content`'s long if-chain for PHP/JSON/YAML/diff/etc.) are mordant's own code, not syntect API. After P1 they are fully implementable in Python with the exposed primitives; the plan only requires the primitives, not a port of the heuristics. (Optional stretch: add a Python-side `syntect.detect_syntax(ss, code)` util.)
- **Mermaid theme derivation** (`mermaid_theme.rs`) needs only read access to `Color`, `Theme`, and `ThemeItem` — already covered. No work required beyond a parity test.
- **`HighlightState` real serialization** — not used by mordant; leave as-is.
- **Thread-safety / caching** — mordant uses `LazyLock` + `RwLock` for global assets/theme-set. syntect-py can offer `syntect.load_assets()`/`syntect.load_defaults()` result caching in Python (P5) but a global cache is optional.
- **Licensing:** vendoring bat's syntax/theme data (Option B in P5) is MIT; keep provenance notes (see mordant's `ThirdPartyNotices.md`).
- **syntect-assets crate version drift:** if Option A is chosen, pin `syntect-assets` 0.23.6 (the version mordant uses) and confirm its embedded bat data matches the dump format the fork can load. Patch `syntect-assets` to `syntect = { path = "..." }` to avoid duplicate crate copies.

---

# Appendix — Concrete reference code from mordant

This appendix collects the exact mordant code paths that the upgrade plan is derived from. They can be used as templates when implementing the corresponding features in `syntect-py`.

---

## A. Syntax lookup cascade (`mordant-py/src/highlighter.rs`)

mordant resolves a language identifier with the same cascade that syntect-py should expose:

```rust
// From mordant-py/src/highlighter.rs
let _syntax = ps
    .find_syntax_by_token(&lang)
    .or_else(|| ps.find_syntax_by_extension(&lang))
    .unwrap_or_else(|| ps.find_syntax_plain_text());
```

Content-based first-line detection (shebangs, Emacs modelines, XML declarations):

```rust
// From mordant-py/src/highlighter.rs :: detect_syntax_from_content
let first_line = code.lines().next().unwrap_or("");
if let Some(syntax) = ps.find_syntax_by_first_line(first_line) {
    let name = syntax.name.to_lowercase().replace(' ', "-");
    // ... normalizations for bash/svelte/etc ...
    return name;
}

// 2. Try token/name matching on the first line
let trimmed = first_line.trim();
if let Some(syntax) = ps.find_syntax_by_token(trimmed) {
    return syntax.name.to_lowercase().replace(' ', "-");
}

// 3. Try extension matching (if the first line happens to be a filename)
if let Some(dot_pos) = trimmed.rfind('.') {
    let ext = &trimmed[dot_pos + 1..];
    if let Some(syntax) = ps.find_syntax_by_extension(ext) {
        return syntax.name.to_lowercase().replace(' ', "-");
    }
}
```

**Target in syntect-py:** add `SyntaxSet.find_syntax_by_token` and `SyntaxSet.find_syntax_by_first_line` in `pyext/src/syntax_set.rs`.

---

## B. Theme loading from string content (`mordant-py/src/highlighter.rs`)

mordant loads `.tmTheme` files by reading them into a string and using `ThemeSet::load_from_reader`:

```rust
// From mordant-py/src/highlighter.rs :: load_builtin_themes
if file_str.ends_with(".tmTheme") {
    let theme_name = file_str.trim_end_matches(".tmTheme");

    if let Ok(content) = std::fs::read_to_string(&file_path) {
        if let Ok(theme) = ThemeSet::load_from_reader(&mut Cursor::new(content)) {
            let mut ts = THEME_SET.write().unwrap();
            ts.themes.insert(theme_name.to_string(), theme);
            loaded.push(theme_name.to_string());
        }
    }
}
```

The global theme set is mutated directly (`ts.themes.insert(...)`). The same pattern is used for `add_custom_theme`:

```rust
// From mordant-py/src/highlighter.rs :: add_custom_theme (plist branch)
let mut reader = Cursor::new(content.as_bytes());
let theme = ThemeSet::load_from_reader(&mut reader);

match theme {
    Ok(t) => {
        ts.themes.insert(name.to_string(), t);
        Ok(())
    }
    Err(e) => Err(...),
}
```

**Target in syntect-py:** add `ThemeSet.load_theme_from_reader`, `ThemeSet.add_theme`, and `ThemeSet.add_theme_from_reader` in `pyext/src/theme_set.rs`.

---

## C. VSCode JSON/JSONC theme conversion (`mordant-py/src/vscode_theme.rs`)

### C.1 Data structures

```rust
// From mordant-py/src/vscode_theme.rs
#[derive(Debug, Deserialize)]
pub struct VscodeTokenColor {
    pub scope: Option<VscodeScope>,
    pub settings: VscodeTokenSettings,
}

#[derive(Debug, Deserialize)]
#[serde(untagged)]
pub enum VscodeScope {
    Single(String),
    Multiple(Vec<String>),
}

impl VscodeScope {
    pub fn to_scope_selectors(&self) -> Result<ScopeSelectors, String> {
        match self {
            VscodeScope::Single(s) => ScopeSelectors::from_str(s).map_err(|e| e.to_string()),
            VscodeScope::Multiple(v) => ScopeSelectors::from_str(&v.join(",")).map_err(|e| e.to_string()),
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct VscodeTokenSettings {
    pub foreground: Option<String>,
    pub background: Option<String>,
    #[serde(rename = "fontStyle")]
    pub font_style: Option<String>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct VscodeTheme {
    pub name: Option<String>,
    pub author: Option<String>,
    #[serde(rename = "type")]
    pub theme_type: Option<String>,
    #[serde(default)]
    pub colors: HashMap<String, Option<String>>,
    #[serde(rename = "tokenColors")]
    pub token_colors: Vec<VscodeTokenColor>,
}
```

### C.2 Color resolution

```rust
// From mordant-py/src/vscode_theme.rs
pub fn resolve_color(color_str: &str) -> Option<Color> {
    let trimmed = color_str.trim();

    // Try hex color first
    if let Ok(color) = hex_to_color(trimmed) {
        return Some(color);
    }

    // Try named color lookup
    if let Some(color) = resolve_named_color(trimmed) {
        return Some(color);
    }

    None
}

fn hex_to_color(s: &str) -> Result<Color, ()> {
    let s = s.trim();

    // #RRGGBB
    if s.starts_with('#') && s.len() == 7 {
        let r = u8::from_str_radix(&s[1..3], 16).map_err(|_| ())?;
        let g = u8::from_str_radix(&s[3..5], 16).map_err(|_| ())?;
        let b = u8::from_str_radix(&s[5..7], 16).map_err(|_| ())?;
        return Ok(Color { r, g, b, a: 255 });
    }

    // rgb(r, g, b)
    if s.starts_with("rgb(") && s.ends_with(')') {
        let inner = &s[4..s.len() - 1];
        let parts: Vec<&str> = inner.split(',').map(|p| p.trim()).collect();
        if parts.len() == 3 {
            let r = parts[0].parse::<u8>().map_err(|_| ())?;
            let g = parts[1].parse::<u8>().map_err(|_| ())?;
            let b = parts[2].parse::<u8>().map_err(|_| ())?;
            return Ok(Color { r, g, b, a: 255 });
        }
    }

    Err(())
}
```

### C.3 Font-style parsing

```rust
// From mordant-py/src/vscode_theme.rs
fn parse_font_style(s: &str) -> Option<FontStyle> {
    let s = s.trim().to_lowercase();
    let mut flags: u32 = 0;

    for part in s.split(',') {
        let part = part.trim();
        match part {
            "bold" => flags |= 1 << 0,                       // BOLD = 1
            "underline" | "underlined" => flags |= 1 << 1,  // UNDERLINE = 2
            "italic" => flags |= 1 << 2,                    // ITALIC = 4
            _ => {}
        }
    }

    if flags == 0 {
        None
    } else {
        FontStyle::from_bits((flags & 0xFF) as u8)
    }
}
```

### C.4 Theme conversion

```rust
// From mordant-py/src/vscode_theme.rs :: vscode_theme_to_syntect
pub fn vscode_theme_to_syntect(vscode: &VscodeTheme) -> Result<Theme, String> {
    let mut settings = ThemeSettings::default();

    for (key, value) in &vscode.colors {
        if value.is_none() { continue; }
        let color_val = value.as_ref().unwrap();
        let color = resolve_color(color_val);

        match key.as_str() {
            "editor.background" => settings.background = color,
            "editor.foreground" => {
                settings.foreground = color;
                settings.caret = color;
            }
            "editor.lineHighlightBackground" => settings.line_highlight = color,
            "editor.selectionBackground" => settings.selection = color,
            "editorGutter.background" => settings.gutter = color,
            "editorLineNumber.foreground" => settings.gutter_foreground = color,
            "editor.findMatchBackground" => {
                settings.highlight = color;
                settings.find_highlight = color;
            }
            "widget.shadow" | "scrollbar.shadow" => settings.shadow = color,
            // ... many more mappings ...
            _ => {}
        }
    }

    let mut scopes: Vec<ThemeItem> = Vec::new();
    for token_color in &vscode.token_colors {
        let scope = if let Some(s) = &token_color.scope {
            s.to_scope_selectors()?
        } else {
            ScopeSelectors::from_str("*").map_err(|e| e.to_string())?
        };

        let style = StyleModifier {
            foreground: token_color.settings.foreground.as_ref().and_then(|s| resolve_color(s)),
            background: token_color.settings.background.as_ref().and_then(|s| resolve_color(s)),
            font_style: token_color.settings.font_style.as_ref().map(|s| parse_font_style(s)).unwrap_or(None),
        };

        scopes.push(ThemeItem { scope, style });
    }

    Ok(Theme {
        name: vscode.name.clone(),
        author: vscode.author.clone(),
        scopes,
        settings,
    })
}
```

### C.5 Format detection

```rust
// From mordant-py/src/vscode_theme.rs
pub fn is_vscode_json_theme(content: &str) -> bool {
    let trimmed = content.trim();
    trimmed.starts_with('{') && trimmed.contains("\"tokenColors\"")
}

pub fn is_plist_xml_theme(content: &str) -> bool {
    let trimmed = content.trim();
    trimmed.starts_with("<?xml") || trimmed.starts_with("<plist")
}

pub fn parse_vscode_theme_jsonc(jsonc_str: &str) -> Result<VscodeTheme, String> {
    let serde_value = jsonc_parser::parse_to_serde_value(
        jsonc_str,
        &jsonc_parser::ParseOptions::default()
    ).map_err(|e| format!("JSONC parse error: {}", e))?;

    serde_json::from_value(serde_value)
        .map_err(|e| format!("Theme parse error: {}", e))
}
```

**Target in syntect-py:** add `pyext/src/vscode_theme.rs` mirroring this module and expose `is_vscode_theme`, `is_plist_theme`, `parse_vscode_theme`, and `add_custom_theme`.

---

## D. Reading `Theme`/`ThemeItem`/`Color` for Mermaid derivation (`mordant-py/src/mermaid_theme.rs`)

This shows the read-side API that must continue to work once theme construction is exposed:

```rust
// From mordant-py/src/mermaid_theme.rs :: derive_mermaid_theme
let s = &syn.settings;
let bg_color = s.background.unwrap_or(Color { r: 0xff, g: 0xff, b: 0xff, a: 0xff });
let fg_color = s.foreground.unwrap_or(Color { r: 0x00, g: 0x00, b: 0x00, a: 0xff });

let mut entries: Vec<(String, Color)> = syn
    .scopes
    .iter()
    .filter_map(|item: &ThemeItem| {
        item.style.foreground.map(|c| {
            let name = item
                .scope
                .selectors
                .iter()
                .filter_map(|sel| sel.extract_single_scope())
                .map(|sc| sc.to_string())
                .collect::<Vec<_>>()
                .join(" ");
            (name, c)
        })
    })
    .collect();
```

**Target in syntect-py:** keep existing `Theme`, `ThemeItem`, `Color`, and `ThemeSettings` getters working; add `ScopeSelectors` as a first-class object.

---

## E. syntect-assets usage (`mordant-py/src/highlighter.rs`)

mordant initializes bat's syntaxes and a fallback theme like this:

```rust
// From mordant-py/src/highlighter.rs
use syntect_assets::assets::HighlightingAssets;

static ASSETS: LazyLock<std::sync::Arc<std::sync::Mutex<HighlightingAssets>>> =
    LazyLock::new(|| {
        let mut assets = HighlightingAssets::from_binary();
        assets.set_fallback_theme("Monokai Extended");
        std::sync::Arc::new(std::sync::Mutex::new(assets))
    });

static SYNTAX_SET: LazyLock<std::sync::Arc<SyntaxSet>> = LazyLock::new(|| {
    let assets = ASSETS.lock().unwrap();
    let ss = match assets.get_syntax_set() {
        Ok(s) => s.clone(),
        Err(_) => SyntaxSet::load_defaults_newlines(),
    };
    std::sync::Arc::new(ss)
});
```

Theme fallback lookup:

```rust
// From mordant-py/src/highlighter.rs :: highlight_code
let theme = ts.themes
    .get(theme_name)
    .unwrap_or_else(|| &ts.themes["InspiredGitHub"]);
```

**Target in syntect-py:** add an `Assets`/`HighlightingAssets` class in `pyext/src/assets.rs` (or vendor the data directly) and wire fallback-theme behavior into `ThemeSet.get_theme` / highlighters.

---

## F. Python-side embedded theme loading (`mordant-py/mordant/__init__.py`)

mordant loads bundled themes from the wheel at import time:

```python
# From mordant-py/mordant/__init__.py
def _load_embedded_themes():
    package_dir = os.path.dirname(os.path.abspath(__file__))
    themes_dir = os.path.join(package_dir, "themes")

    if not os.path.isdir(themes_dir):
        return

    for f in sorted(os.listdir(themes_dir)):
        file_path = os.path.join(themes_dir, f)
        try:
            with open(file_path, "r") as fp:
                content = fp.read()

            if f.endswith(".tmTheme"):
                theme_name = f.replace(".tmTheme", "")
            elif f.endswith(".json"):
                theme_name = f.replace(".json", "")
            else:
                continue

            add_custom_theme(theme_name, content)
        except Exception as e:
            print(f"Warning: Could not load theme {f}: {e}")

_load_embedded_themes()
```

**Target in syntect-py:** provide an equivalent Python helper (e.g. in a `syntext/themes.py` or the package `__init__.py`) that scans a directory and registers every `.tmTheme`/`.json` file via the new Rust-backed `add_custom_theme`.

---

## G. Reference test fixtures (`mordant-py/tests/test_vscode_theme.py`)

These are the exact inputs mordant tests against. They should be reused in syntect-py parity tests:

```python
# From mordant-py/tests/test_vscode_theme.py
VS_CODE_THEME_JSON = '''{
    "name": "Test VSCode Theme",
    "type": "dark",
    "tokenColors": [
        { "scope": "comment", "settings": { "foreground": "#6A7A3E", "fontStyle": "italic" } },
        { "scope": "keyword", "settings": { "foreground": "#FF6B6B" } },
        { "scope": "string",  "settings": { "foreground": "#4EC6FB" } },
        { "scope": "variable", "settings": { "foreground": "#E0E0E0" } }
    ],
    "colors": {
        "editor.background": "#1E1E1E",
        "editor.foreground": "#E0E0E0"
    }
}'''

MULTI_SCOPE_THEME = '''{
    "name": "Multi-Scope Test",
    "tokenColors": [
        { "scope": "variable, constant", "settings": { "foreground": "#FFD700" } },
        { "scope": "entity.name.function, support.function",
          "settings": { "foreground": "#61DAFF", "fontStyle": "bold" } }
    ]
}'''

JSONC_THEME = '''{
    // This is a comment
    "name": "JSONC Test Theme",
    /* Block comment */
    "tokenColors": [
        { "scope": "comment", "settings": { "foreground": "#888888" } }
    ]
}'''
```

**Target in syntect-py:** add these fixtures to `pyext/tests/test_syntect.py` or `pyext/tests/test_mordant_parity.py` and assert the same conversion/highlighting behavior.

---

## H. Target API examples for syntect-py

These snippets show the API surface the plan aims to create.

### H.1 Python usage after P1–P6 (and P4.5)

```python
import syntect

# P1: language detection cascade
ss = syntect.SyntaxSet.load_defaults(True)
lang = "py"
syntax = ss.find_syntax_by_token(lang) \
       or ss.find_syntax_by_extension(lang) \
       or ss.find_syntax_plain_text()

# P1: first-line detection
sh = ss.find_syntax_by_first_line("#!/usr/bin/env bash")

# P2: load a .tmTheme from a string
ts = syntect.ThemeSet.load_defaults()
with open("Dracula.tmTheme", "r") as f:
    ts.add_theme_from_reader("Dracula", f.read())

# P3: build a theme from primitives
settings = syntect.ThemeSettings()
settings.background = syntect.Color.from_hex("#1E1E1E")
settings.foreground = syntect.Color.from_hex("#E0E0E0")

scopes = [
    syntect.ThemeItem(
        scope=syntect.ScopeSelectors.from_string("comment"),
        style=syntect.StyleModifier(
            foreground=syntect.Color.from_hex("#6A7A3E"),
            font_style=syntect.FontStyle.from_string("italic"),
        ),
    ),
]

theme = syntect.Theme(name="My Theme", author="me", settings=settings, scopes=scopes)
ts.add_theme("my-theme", theme)

# P4: VSCode JSON/JSONC theme (auto-detected)
syntect.add_custom_theme("vscode-theme", open("theme.json").read())

# P5: bat/syntect-assets
assets = syntect.Assets.from_binary()
assets.set_fallback_theme("Monokai Extended")
ss = assets.get_syntax_set()
ts = assets.get_theme_set()

# P6: HighlightLines with a Theme object directly
syntax = ss.find_syntax_by_name("Rust")
hl = syntect.HighlightLines.with_theme(syntax, ss, ts.get_theme("base16-ocean.dark"))
for line in code.splitlines():
    tokens = hl.highlight_line(line, ss)
```

### H.2 Rust/pyO3 target signatures

```rust
// pyext/src/syntax_set.rs
#[pymethods]
impl PySyntaxSet {
    fn find_syntax_by_token(&self, token: &str) -> Option<PySyntaxReference> { ... }
    fn find_syntax_by_first_line(&self, line: &str) -> Option<PySyntaxReference> { ... }
}

// pyext/src/theme_set.rs
#[pymethods]
impl PyThemeSet {
    #[staticmethod]
    fn load_theme_from_reader(content: &str) -> PyResult<PyTheme> { ... }

    fn add_theme(&mut self, name: &str, theme: &PyTheme) -> PyResult<()> { ... }
    fn add_theme_from_reader(&mut self, name: &str, content: &str) -> PyResult<()> { ... }

    fn get_theme(&self, key: &str, fallback: Option<&str>) -> Option<PyTheme> { ... }
}

// pyext/src/style.rs
#[pymethods]
impl PyFontStyle {
    #[staticmethod]
    fn from_string(s: &str) -> Option<PyFontStyle> { ... }
}

// pyext/src/theme_set.rs (new class)
#[pyclass(name = "ScopeSelectors")]
pub struct PyScopeSelectors { ... }

#[pymethods]
impl PyScopeSelectors {
    #[staticmethod]
    fn from_string(s: &str) -> PyResult<Self> { ... }
    fn to_string(&self) -> String { ... }
}

// pyext/src/highlighter.rs
#[pymethods]
impl PyHighlightLines {
    #[classmethod]
    fn with_theme(
        cls: &Bound<'_, PyType>,
        syntax_ref: &PySyntaxReference,
        syntax_set: &PySyntaxSet,
        theme: &PyTheme,
    ) -> PyResult<Self> { ... }
}

// pyext/src/vscode_theme.rs
#[pyfunction]
fn is_vscode_theme(content: &str) -> bool { ... }

#[pyfunction]
fn is_plist_theme(content: &str) -> bool { ... }

#[pyfunction]
fn parse_vscode_theme(content: &str) -> PyResult<PyTheme> { ... }

#[pyfunction]
fn add_custom_theme(name: &str, content: &str) -> PyResult<()> { ... }

// pyext/src/assets.rs
#[pyclass(name = "Assets")]
pub struct PyAssets { ... }

#[pymethods]
impl PyAssets {
    #[staticmethod]
    fn from_binary() -> Self { ... }
    fn set_fallback_theme(&mut self, name: &str) { ... }
    fn get_syntax_set(&self) -> PySyntaxSet { ... }
    fn get_theme_set(&self) -> PyThemeSet { ... }
}
```

---

## I. Quick mapping: mordant code → syntect-py target module

| mordant file / code | syntect-py target file | syntect-py target API |
|---|---|---|
| `highlighter.rs` `find_syntax_by_token` / `find_syntax_by_first_line` | `pyext/src/syntax_set.rs` | `SyntaxSet.find_syntax_by_token`, `SyntaxSet.find_syntax_by_first_line` |
| `highlighter.rs` `ThemeSet::load_from_reader` / `ts.themes.insert` | `pyext/src/theme_set.rs` | `ThemeSet.load_theme_from_reader`, `ThemeSet.add_theme` |
| `vscode_theme.rs` `ScopeSelectors::from_str` | `pyext/src/theme_set.rs` | `ScopeSelectors.from_string` |
| `vscode_theme.rs` `ThemeSettings` mutation | `pyext/src/theme_set.rs` | `ThemeSettings.__new__` + setters |
| `vscode_theme.rs` `ThemeItem`/`Theme` construction | `pyext/src/theme_set.rs` | `ThemeItem.__new__`, `Theme.__new__` |
| `vscode_theme.rs` `parse_font_style` | `pyext/src/style.rs` | `FontStyle.from_string` |
| `vscode_theme.rs` full converter + `add_custom_theme` | `pyext/src/vscode_theme.rs` | `parse_vscode_theme`, `is_vscode_theme`, `is_plist_theme`, `add_custom_theme` |
| `highlighter.rs` `HighlightingAssets` usage | `pyext/src/assets.rs` | `Assets.from_binary`, `set_fallback_theme`, `get_syntax_set`, `get_theme_set` |
| `highlighter.rs` theme fallback (`unwrap_or_else`) | `pyext/src/theme_set.rs` + `pyext/src/highlighter.rs` | `ThemeSet.get_theme(key, fallback)`, highlighter fallback handling |
| `highlighter.rs` `HighlightLines::new(syntax, theme)` | `pyext/src/highlighter.rs` | `HighlightLines.with_theme` |
| `mordant/__init__.py` `_load_embedded_themes` | Python package helper | Directory scanner calling `add_custom_theme` |
| `tests/test_vscode_theme.py` fixtures | `pyext/tests/test_syntect.py` / `test_mordant_parity.py` | Parity tests for VSCode/JSONC/multi-scope themes |

---

## J. mordant theme folder to copy (P4.5)

Copy the entire directory:

```text
D:/User/Documents/Python/mordant/mordant-py/mordant/themes/
  → syntect-py/pyext/syntect/themes/
```

The directory contains 55 theme files (`.tmTheme` + `.json`):

```
1337.tmTheme
Andromeda-color-theme.json
aura-theme.tmTheme
ayu-dark.json
ayu-light.json
ayu-mirage.json
azureus.json
bordo.json
cobalt2.json
Coldark-Cold.tmTheme
Coldark-Dark.tmTheme
DarkNeon.tmTheme
Dracula.tmTheme
GitHub.tmTheme
gruvbox-dark.tmTheme
gruvbox-light.tmTheme
hibernus.json
horizon.json
LaserWave-color-theme.json
lilac.json
lux.json
minimus.json
Monokai Extended Bright.tmTheme
Monokai Extended Light.tmTheme
Monokai Extended Origin.tmTheme
Monokai Extended.tmTheme
moonlight.json
Night Owl-color-theme.json
Night Owl-Light-color-theme.json
noctis.json
Nord.tmTheme
obscuro.json
OneDark.json
OneDark-Pro.json
OneHalfDark.tmTheme
OneHalfLight.tmTheme
palenight.json
Panda.json
sereno.json
shades-of-purple-color-theme.json
Solarized (dark).tmTheme
Solarized (light).tmTheme
Sublime Snazzy.tmTheme
synthwave-color-theme.json
tokyo-night-color-theme.json
tokyo-night-light-color-theme.json
tokyo-night-storm-color-theme.json
TwoDark.tmTheme
uva.json
viola.json
Visual Studio Dark+.tmTheme
WinterIsComing-dark-blue-color-theme.json
WinterIsComing-dark-color-theme.json
WinterIsComing-light-color-theme.json
zenburn.tmTheme
```

These are the exact files that mordant's `mordant/__init__.py` loads at import time via `_load_embedded_themes()`. After copying them to `syntect-py`, a loader should iterate the directory and call `add_custom_theme(name_without_extension, file_content)` for each file, exactly as shown in Appendix F.
