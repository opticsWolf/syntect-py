# Changelog

All notable changes will be documented in this file.

## [5.3.0] - 2026-06-30

### Added
- Complete Python bindings for syntect v5.3.0
- All public API types from upstream syntect crate
- Stateful `ParseState` with real incremental parsing
- Stateful `HighlightLines` with parse state across lines
- `HighlightState` for save/restore incremental highlighting
- `Metadata`, `MetadataSet`, `MetadataItem` for tmPreferences support
- `ScoredStyle` and `ScopeRangeIterator` for advanced debugging
- `ClassedHTMLGenerator` for class-based HTML output
- `tokens_to_classed_spans`, `line_tokens_to_classed_spans_py`, `styled_line_to_highlighted_html`
- `split_at`, `modify_range`, `lines_with_endings` utility functions
- `dump_syntax_set`, `load_syntax_set`, `dump_theme_set`, `load_theme_set` serialization
- `css_for_theme`, `css_for_theme_class`, `generate_css` CSS generation
- `highlighted_html_for_string_py`, `create_html_file`, `highlighted_html_at_line_and_column_number`
- `ParseSyntaxError` exception type
- `MatchPower`, `ClearAmount`, `ContextId` advanced types
- Complete type stubs (`syntect.pyi`)
- 9 example scripts
- 258 comprehensive tests
- `ARCHITECTURE.md` (21.8KB)
- `QUICKREF.md` (24.6KB)
- `README.md` (comprehensive Python documentation)

### Changed
- Disabled default features for syntect dependency (uses `regex-fancy` only)
- All highlighting functions handle empty strings efficiently
- `split_at` and `modify_range` use character positions (not byte positions) for Unicode support
- Error messages include available syntaxes/themes when lookup fails
- `HighlightLines` constructor signature: `HighlightLines(rust, ss, ts, theme_name)`
- `lines_with_endings` returns `(line, ending)` tuples (ending is just newline chars)

### Fixed
- `as_html` `IfDifferent` background logic (added `default_bg` parameter)
- `\r\n` handling in `highlight_lines` and `highlight_string`
- `ClassStyle.spaced_prefixed` now respects prefix parameter
- Fragile scope parsing in `css_for_theme`
- `PyLinesWithEndings.__next__` ending now correctly returns only newline chars
- Unicode-aware character splitting in `split_at` and `modify_range`

### Performance
- `split_lines_with_endings` optimized (no `Vec<char>` allocation)
- `HighlightLines` stores owned `SyntaxReference` clone
- `as_html`, `as_terminal_escaped`, `as_latex_escaped` deduplicated into shared implementations
- Empty string early returns in all highlighting functions

### Security
- Uses `regex-fancy` (pure Rust) instead of `regex-onig` (Oniguruma C library)
- No unsafe code paths exposed to Python

---

*This changelog follows [Keep a Changelog](https://keepachangelog.com/) format.*
