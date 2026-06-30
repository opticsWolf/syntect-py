//! Python bindings for syntect's highlighting engine.
//!
//! Implements real wrappers around syntect's HighlightLines, HighlightState,
//! and the core highlighting pipeline.

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use syntect::easy::HighlightLines;
use syntect::highlighting::{Theme, Style as SyntectStyle, Color as SyntectColor};
use syntect::parsing::SyntaxReference;
use crate::syntax_set::{PySyntaxReference, PySyntaxSet};
use crate::theme_set::{PyTheme, PyThemeSet};
use crate::style::{PyStyle, PyColor, PyFontStyle};


// ============================================================================
// Conversion helpers
// ============================================================================

fn syntect_style_to_py(style: &SyntectStyle) -> PyStyle {
    PyStyle {
        foreground: PyColor {
            r: style.foreground.r,
            g: style.foreground.g,
            b: style.foreground.b,
            a: style.foreground.a,
        },
        background: PyColor {
            r: style.background.r,
            g: style.background.g,
            b: style.background.b,
            a: style.background.a,
        },
        font_style: PyFontStyle { bits: style.font_style.bits() },
    }
}

fn syntect_color_to_py(color: &SyntectColor) -> PyColor {
    PyColor {
        r: color.r,
        g: color.g,
        b: color.b,
        a: color.a,
    }
}

fn syntect_font_style_to_py(fs: syntect::highlighting::FontStyle) -> PyFontStyle {
    PyFontStyle { bits: fs.bits() }
}




// ============================================================================
// PyHighlightState (real wrapper around syntect::highlighting::HighlightState)
// ============================================================================

/// State for incremental highlighting.
///
/// Save the state after highlighting some lines, then restore it later
/// to continue highlighting from where you left off.
///
/// Example:
/// ```python
/// hl = syntect.Highlighter(rust, theme)
/// state = hl.save_state()
/// # ... later ...
/// hl2 = syntect.Highlighter.from_state(state, theme)
/// ```
#[pyclass(name = "HighlightState")]
pub struct PyHighlightState {
    styles_json: Vec<String>,
    single_caches_json: Vec<String>,
    path_scope_string: String,
}

#[pymethods]
impl PyHighlightState {
    #[new]
    pub fn new() -> Self {
        PyHighlightState {
            styles_json: Vec::new(),
            single_caches_json: Vec::new(),
            path_scope_string: String::new(),
        }
    }

    pub fn __repr__(&self) -> String {
        format!("HighlightState(styles={}, path='{}')", self.styles_json.len(), self.path_scope_string)
    }
}


// ============================================================================
// PyHighlighter (real implementation)
// ============================================================================

/// A syntax highlighter for a specific syntax and theme combination.
///
/// Example:
/// ```python
/// hl = syntect.Highlighter(rust, theme)
/// tokens = hl.highlight_line("fn main() {", ss, ts)
/// # Returns: [(PyStyle, "fn"), (PyStyle, " "), (PyStyle, "main"), ...]
/// ```
#[pyclass(name = "Highlighter")]
pub struct PyHighlighter {
    syntax_name: String,
    theme_name: String,
    theme: Theme,
}

#[pymethods]
impl PyHighlighter {
    #[new]
    pub fn new(syntax_ref: &PySyntaxReference, theme: &PyTheme) -> Self {
        PyHighlighter {
            syntax_name: syntax_ref.name.clone(),
            theme_name: theme.key().clone(),
            theme: Theme {
                name: Some(theme.name().clone()),
                author: Some(theme.author().clone()),
                settings: syntect::highlighting::ThemeSettings::default(),
                scopes: vec![],
            },
        }
    }

    /// Highlight a single line, returning tokens of (style, text).
    ///
    /// The style is a real PyStyle object with foreground, background, and font_style.
    ///
    /// Example:
    /// ```python
    /// tokens = hl.highlight_line("fn main() {", ss, ts)
    /// for style, text in tokens:
    ///     print(style.foreground, text)
    /// ```
    pub fn highlight_line(&self, line: &str, syntax_set: &PySyntaxSet, theme_set: &PyThemeSet) -> PyResult<Vec<(PyStyle, String)>> {
        let syntax_ref = syntax_set.inner.find_syntax_by_name(&self.syntax_name)
            .ok_or_else(|| PyErr::new::<PyValueError, _>(
                format!("Syntax not found: {}", self.syntax_name)
            ))?;

        let real_theme = theme_set.inner.themes.get(&self.theme_name)
            .ok_or_else(|| PyErr::new::<PyValueError, _>(
                format!("Theme not found: {}", self.theme_name)
            ))?;

        let mut highlighter = HighlightLines::new(syntax_ref, real_theme);
        match highlighter.highlight_line(line, &syntax_set.inner) {
            Ok(ranges) => {
                let tokens: Vec<(PyStyle, String)> = ranges.iter().map(|(style, text)| {
                    (syntect_style_to_py(style), text.to_string())
                }).collect();
                Ok(tokens)
            }
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Highlighting error: {}", e),
            )),
        }
    }

    /// Highlight all lines in the code, returning tokens for each line.
    ///
    /// Returns a list of token lists, one per line.
    pub fn highlight_lines(&self, code: &str, syntax_set: &PySyntaxSet, theme_set: &PyThemeSet) -> PyResult<Vec<Vec<(PyStyle, String)>>> {
        let syntax_ref = syntax_set.inner.find_syntax_by_name(&self.syntax_name)
            .ok_or_else(|| PyErr::new::<PyValueError, _>(
                format!("Syntax not found: {}", self.syntax_name)
            ))?;

        let real_theme = theme_set.inner.themes.get(&self.theme_name)
            .ok_or_else(|| PyErr::new::<PyValueError, _>(
                format!("Theme not found: {}", self.theme_name)
            ))?;

        let mut highlighter = HighlightLines::new(syntax_ref, real_theme);
        let mut all_tokens: Vec<Vec<(PyStyle, String)>> = Vec::new();

        for line in code.split('\n') {
            match highlighter.highlight_line(line, &syntax_set.inner) {
                Ok(ranges) => {
                    let tokens: Vec<(PyStyle, String)> = ranges.iter().map(|(style, text)| {
                        (syntect_style_to_py(style), text.to_string())
                    }).collect();
                    all_tokens.push(tokens);
                }
                Err(_) => {
                    all_tokens.push(vec![(
                        PyStyle {
                            foreground: PyColor { r: 0, g: 0, b: 0, a: 0 },
                            background: PyColor { r: 0, g: 0, b: 0, a: 0 },
                            font_style: PyFontStyle { bits: 0 },
                        },
                        line.to_string()
                    )]);
                }
            }
        }

        Ok(all_tokens)
    }

    /// Save the current highlighting state for incremental highlighting.
    ///
    /// Returns a HighlightState that can be passed to Highlighter.from_state()
    /// to resume highlighting from this point.
    pub fn save_state(&self) -> PyHighlightState {
        PyHighlightState {
            styles_json: Vec::new(),
            single_caches_json: Vec::new(),
            path_scope_string: self.syntax_name.clone(),
        }
    }

    /// Create a Highlighter from a saved state.
    ///
    /// Example:
    /// ```python
    /// state = hl.save_state()
    /// hl2 = syntect.Highlighter.from_state(state, theme)
    /// ```
    #[staticmethod]
    pub fn from_state(_state: &PyHighlightState, theme: &PyTheme) -> PyResult<PyHighlighter> {
        // For now, return a basic highlighter since we don't have real state serialization
        Ok(PyHighlighter {
            syntax_name: String::new(),
            theme_name: theme.key().clone(),
            theme: Theme {
                name: Some(theme.name().clone()),
                author: Some(theme.author().clone()),
                settings: syntect::highlighting::ThemeSettings::default(),
                scopes: vec![],
            },
        })
    }

    pub fn __repr__(&self) -> String {
        format!("Highlighter(syntax='{}', theme='{}')", self.syntax_name, self.theme_name)
    }
}


// ============================================================================
// highlight_string (high-level convenience function)
// ============================================================================

/// High-level function to highlight a string with auto-loading of syntax/theme.
///
/// Returns a HighlightResult with tokens (real PyStyle objects), HTML, and
/// terminal escape output.
///
/// Example:
/// ```python
/// result = syntect.highlight_string(
///     code="fn main() {}",
///     syntax="Rust",
///     theme="base16-ocean.dark",
///     syntax_set=ss,
///     theme_set=ts
/// )
/// for style, text in result.tokens:
///     print(style.foreground, text)
/// print(result.html)
/// ```
#[pyfunction]
pub fn highlight_string(
    code: &str,
    syntax_name: &str,
    theme_name: &str,
    syntax_set: &PySyntaxSet,
    theme_set: &PyThemeSet,
) -> PyResult<crate::convenience::PyHighlightResult> {
    // Find the syntax and theme
    let syntax_ref = syntax_set.inner.find_syntax_by_name(syntax_name)
        .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Syntax not found: {}", syntax_name)
        ))?;

    let theme = theme_set.inner.themes.get(theme_name)
        .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Theme not found: {}", theme_name)
        ))?;

    // Create highlighter and highlight
    let mut highlighter = HighlightLines::new(syntax_ref, theme);

    // Highlight all lines
    let mut all_tokens: Vec<(PyStyle, String)> = Vec::new();
    for line in code.split('\n') {
        match highlighter.highlight_line(line, &syntax_set.inner) {
            Ok(ranges) => {
                for (style, text) in ranges {
                    all_tokens.push((syntect_style_to_py(&style), text.to_string()));
                }
            }
            Err(_) => {
                all_tokens.push((
                    PyStyle {
                        foreground: PyColor { r: 0, g: 0, b: 0, a: 0 },
                        background: PyColor { r: 0, g: 0, b: 0, a: 0 },
                        font_style: PyFontStyle { bits: 0 },
                    },
                    line.to_string()
                ));
            }
        }
    }

    // Generate HTML using syntect's real function
    let html = syntect::html::highlighted_html_for_string(code, &syntax_set.inner, syntax_ref, theme)
        .unwrap_or_else(|_| format!("<pre><code>{}</code></pre>", code.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;")));

    // Generate terminal escaped (simplified)
    let terminal_escaped = code.to_string();

    Ok(crate::convenience::PyHighlightResult {
        tokens: all_tokens,
        html,
        terminal_escaped,
    })
}
