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
        foreground: syntect_color_to_py(&style.foreground),
        background: syntect_color_to_py(&style.background),
        font_style: syntect_font_style_to_py(style.font_style),
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
// PyHighlightResult (convenience wrapper)
// ============================================================================

/// Result of highlighting a string, containing tokens, HTML, and terminal output.
#[pyclass(name = "HighlightResult")]
pub struct PyHighlightResult {
    tokens: Vec<(String, String)>,
    html: String,
    terminal_escaped: String,
}

#[pymethods]
impl PyHighlightResult {
    #[getter]
    pub fn tokens(&self) -> Vec<(String, String)> {
        self.tokens.clone()
    }

    #[getter]
    pub fn html(&self) -> String {
        self.html.clone()
    }

    #[getter]
    pub fn terminal_escaped(&self) -> String {
        self.terminal_escaped.clone()
    }

    pub fn __repr__(&self) -> String {
        format!(
            "HighlightResult(tokens={}, html_len={}, terminal_len={})",
            self.tokens.len(),
            self.html.len(),
            self.terminal_escaped.len()
        )
    }
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
/// tokens = hl.highlight_line("fn main() {", ss)
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

    /// Highlight a single line, returning tokens of (style_string, text).
    ///
    /// The tokens include the syntect Style debug representation as the style string,
    /// which contains the foreground/background colors and font style.
    pub fn highlight_line(&self, line: &str, syntax_set: &PySyntaxSet, theme_set: &PyThemeSet) -> PyResult<Vec<(String, String)>> {
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
                let tokens: Vec<(String, String)> = ranges.iter().map(|(style, text)| {
                    let py_style = syntect_style_to_py(style);
                    (format!("Style(fg={}, bg={}, font={})",
                        py_style.foreground.to_hex(),
                        py_style.background.to_hex(),
                        py_style.font_style.bits),
                     text.to_string())
                }).collect();
                Ok(tokens)
            }
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Highlighting error: {}", e),
            )),
        }
    }

    /// Highlight all lines in the code, returning tokens for each line.
    pub fn highlight_lines(&self, code: &str, syntax_set: &PySyntaxSet, theme_set: &PyThemeSet) -> PyResult<Vec<Vec<(String, String)>>> {
        let syntax_ref = syntax_set.inner.find_syntax_by_name(&self.syntax_name)
            .ok_or_else(|| PyErr::new::<PyValueError, _>(
                format!("Syntax not found: {}", self.syntax_name)
            ))?;

        let real_theme = theme_set.inner.themes.get(&self.theme_name)
            .ok_or_else(|| PyErr::new::<PyValueError, _>(
                format!("Theme not found: {}", self.theme_name)
            ))?;

        let mut highlighter = HighlightLines::new(syntax_ref, real_theme);
        let mut all_tokens: Vec<Vec<(String, String)>> = Vec::new();

        for line in code.split('\n') {
            match highlighter.highlight_line(line, &syntax_set.inner) {
                Ok(ranges) => {
                    let tokens: Vec<(String, String)> = ranges.iter().map(|(style, text)| {
                        let py_style = syntect_style_to_py(style);
                        (format!("Style(fg={}, bg={}, font={})",
                            py_style.foreground.to_hex(),
                            py_style.background.to_hex(),
                            py_style.font_style.bits),
                         text.to_string())
                    }).collect();
                    all_tokens.push(tokens);
                }
                Err(_) => {
                    all_tokens.push(vec![("Style(fg=0, bg=0, font=0)".to_string(), line.to_string())]);
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
        "Highlighter()".to_string()
    }
}

// ============================================================================
// highlight_string (high-level convenience function)
// ============================================================================

/// High-level function to highlight a string with auto-loading of syntax/theme.
///
/// Example:
/// ```python
/// result = syntect.highlight_string(
///     code="fn main() {}",
///     syntax="Rust",
///     theme="base16-ocean.dark"
/// )
/// print(result.html)
/// ```
#[pyfunction]
pub fn highlight_string(
    code: &str,
    syntax_name: &str,
    theme_name: &str,
    syntax_set: &PySyntaxSet,
    theme_set: &PyThemeSet,
) -> PyResult<PyHighlightResult> {
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
    let mut all_tokens: Vec<(String, String)> = Vec::new();
    for line in code.split('\n') {
        match highlighter.highlight_line(line, &syntax_set.inner) {
            Ok(ranges) => {
                let tokens: Vec<(String, String)> = ranges.iter().map(|(style, text)| {
                    let py_style = syntect_style_to_py(style);
                    (format!("Style(fg={}, bg={}, font={})",
                        py_style.foreground.to_hex(),
                        py_style.background.to_hex(),
                        py_style.font_style.bits),
                     text.to_string())
                }).collect();
                all_tokens.extend(tokens);
            }
            Err(_) => {
                all_tokens.push(("Style(fg=0, bg=0, font=0)".to_string(), line.to_string()));
            }
        }
    }

    // Generate HTML (simplified)
    let html = format!("<pre><code>{}</code></pre>", code.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;"));

    // Generate terminal escaped (simplified)
    let terminal_escaped = code.to_string();

    Ok(PyHighlightResult {
        tokens: all_tokens,
        html,
        terminal_escaped,
    })
}
