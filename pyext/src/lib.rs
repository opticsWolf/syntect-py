//! PyO3 Python bindings for syntect.
//!
//! Exposes syntax highlighting, theme management, and output formatting
//! to Python via the `syntect` module.

use pyo3::prelude::*;

mod converters;
mod convenience;
mod dumps;
mod errors;
mod highlighter;
mod html;
mod parse_state;
mod style;
mod syntax_set;
mod theme_set;
mod util;

/// High-quality syntax highlighting using Sublime Text grammars.
///
/// This module provides Python bindings for the syntect Rust library.
///
/// Example usage:
/// ```python
/// import syntect
///
/// ss = syntect.SyntaxSet.load_defaults()
/// ts = syntect.ThemeSet.load_defaults()
/// theme = ts.get_theme("base16-ocean.dark")
///
/// hl = syntect.Highlighter(ss, theme)
/// for line in ["fn main() {", "    println!(\"hello\");", "}"]:
///     tokens = hl.highlight_line(line, ss)
///     print(syntect.as_terminal_escaped(tokens))
/// ```
#[pymodule]
fn syntect(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = m.py();

    // Error types - register as module-level exception classes
    m.add("LoadingError", py.get_type::<errors::LoadingError>())?;
    m.add("ParsingError", py.get_type::<errors::ParsingError>())?;
    m.add("DumpError", py.get_type::<errors::DumpError>())?;

    // Core types
    m.add_class::<style::PyColor>()?;
    m.add_class::<style::PyFontStyle>()?;
    m.add_class::<style::PyStyle>()?;
    m.add_class::<style::PyStyleModifier>()?;

    // Syntax management
    m.add_class::<syntax_set::PySyntaxSet>()?;
    m.add_class::<syntax_set::PySyntaxReference>()?;
    m.add_class::<syntax_set::PySyntaxSetBuilder>()?;

    // Theme management
    m.add_class::<theme_set::PyThemeSet>()?;
    m.add_class::<theme_set::PyTheme>()?;
    m.add_class::<theme_set::PyThemeSettings>()?;
    m.add_class::<theme_set::PyThemeItem>()?;

    // Highlighting engine
    m.add_class::<highlighter::PyHighlighter>()?;
    m.add_class::<highlighter::PyHighlightState>()?;
    m.add_class::<convenience::PyHighlightResult>()?;

    // Parsing
    m.add_class::<parse_state::PyParseState>()?;
    m.add_class::<parse_state::PyParseLineOutput>()?;
    m.add_class::<parse_state::PyScopeStack>()?;
    m.add_class::<parse_state::PyScopeStackOp>()?;
    m.add_class::<parse_state::PyScope>()?;

    // Output utilities
    m.add_class::<html::PyClassStyle>()?;
    m.add_class::<html::PyIncludeBg>()?;
    m.add_function(wrap_pyfunction!(util::as_terminal_escaped, m)?)?;
    m.add_function(wrap_pyfunction!(util::as_html, m)?)?;
    m.add_function(wrap_pyfunction!(util::as_latex_escaped, m)?)?;
    m.add_function(wrap_pyfunction!(html::css_for_theme, m)?)?;
    m.add_function(wrap_pyfunction!(html::generate_css, m)?)?;
    m.add_function(wrap_pyfunction!(html::highlighted_html_for_string_py, m)?)?;
    m.add_function(wrap_pyfunction!(html::create_html_file, m)?)?;
    m.add_function(wrap_pyfunction!(html::highlighted_html_at_line_and_column_number, m)?)?;

    // Dump utilities
    m.add_function(wrap_pyfunction!(dumps::dump_syntax_set, m)?)?;
    m.add_function(wrap_pyfunction!(dumps::load_syntax_set, m)?)?;
    m.add_function(wrap_pyfunction!(dumps::dump_theme_set, m)?)?;
    m.add_function(wrap_pyfunction!(dumps::load_theme_set, m)?)?;

    // High-level convenience
    m.add_function(wrap_pyfunction!(highlighter::highlight_string, m)?)?;

    Ok(())
}
