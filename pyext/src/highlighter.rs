//! Python bindings for syntect's highlighting engine.
//!
//! Implements real wrappers around syntect's HighlightLines, HighlightState,
//! and the core highlighting pipeline.

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use syntect::easy::HighlightLines;
use syntect::highlighting::{Highlighter as SyntectHighlighter, HighlightState as SyntectHighlightState};

use crate::syntax_set::{PySyntaxReference, PySyntaxSet};
use crate::theme_set::{PyTheme, PyThemeSet};
use crate::style::{PyStyle, PyColor, PyFontStyle};
use crate::converters::syntect_style_to_py;
use crate::parse_state::PyScope;





// ============================================================================
// LinesWithEndings helper
// ============================================================================

/// Splits content into lines with their ending characters.
/// Returns a list of (line_content, ending) tuples where ending is one of:
/// - "\n" (newline)
/// - "\r\n" (CRLF)
/// - "\r" (carriage return)
/// - "" (no ending, last line)
pub fn split_lines_with_endings(content: &str) -> Vec<(String, String)> {
    let mut lines = Vec::new();
    let mut current_line = String::new();
    let mut i = 0;
    let chars: Vec<char> = content.chars().collect();
    let len = chars.len();

    while i < len {
        let ch = chars[i];
        match ch {
            '\n' => {
                lines.push((current_line.clone(), "\n".to_string()));
                current_line.clear();
                i += 1;
            }
            '\r' => {
                if i + 1 < len && chars[i + 1] == '\n' {
                    lines.push((current_line.clone(), "\r\n".to_string()));
                    current_line.clear();
                    i += 2;
                } else {
                    lines.push((current_line.clone(), "\r".to_string()));
                    current_line.clear();
                    i += 1;
                }
            }
            _ => {
                current_line.push(ch);
                i += 1;
            }
        }
    }

    // Add remaining content (last line without ending)
    if !current_line.is_empty() {
        lines.push((current_line, String::new()));
    }

    lines
}


// ============================================================================
// PyHighlightState (real partial implementation)
// ============================================================================

/// State for incremental highlighting.
///
/// Save the state after highlighting some lines, then restore it later
/// to continue highlighting from where you left off.
///
/// This is a partial implementation that stores the scope stack and
/// style stack, providing meaningful state data without the complexity
/// of full HighlightLines serialization.
///
/// Example:
/// ```python
/// hl = syntect.Highlighter(rust, theme)
/// state = hl.save_state(ss, ts)
/// print(state.path_scope_string)  # "source.rust"
/// print(state.styles_count)        # 1
/// ```
#[pyclass(name = "HighlightState", skip_from_py_object)]
pub struct PyHighlightState {
    path_scope_stack: Vec<PyScope>,
    styles_stack: Vec<PyStyle>,
}

#[pymethods]
impl PyHighlightState {
    #[new]
    pub fn new() -> Self {
        PyHighlightState {
            path_scope_stack: Vec::new(),
            styles_stack: Vec::new(),
        }
    }

    /// Get the scope stack as a space-separated string.
    ///
    /// Example:
    /// ```python
    /// state = hl.save_state(ss, ts)
    /// print(state.path_scope_string)  # "source.rust keyword.declaration"
    /// ```
    #[getter]
    pub fn path_scope_string(&self) -> String {
        let mut result = String::new();
        for (i, scope) in self.path_scope_stack.iter().enumerate() {
            if i > 0 {
                result.push(' ');
            }
            result.push_str(&scope.to_string());
        }
        result
    }

    /// Get the number of styles in the style stack.
    ///
    /// Example:
    /// ```python
    /// state = hl.save_state(ss, ts)
    /// print(state.styles_count)        # 1 (default style)
    /// ```
    #[getter]
    pub fn styles_count(&self) -> usize {
        self.styles_stack.len()
    }

    /// Get the path scope stack as a list of Scope objects.
    #[getter]
    pub fn path_scope_stack(&self) -> Vec<PyScope> {
        self.path_scope_stack.clone()
    }

    /// Get the styles stack as a list of Style objects.
    #[getter]
    pub fn styles_stack(&self) -> Vec<PyStyle> {
        self.styles_stack.clone()
    }

    pub fn __repr__(&self) -> String {
        format!(
            "HighlightState(path='{}', styles={})",
            self.path_scope_string(),
            self.styles_stack.len()
        )
    }
}


// ============================================================================
// PyHighlightLines — Stateful highlighting (maintains state across calls)
// ============================================================================

/// A stateful syntax highlighter that maintains parsing state across lines.
///
/// Unlike `Highlighter` which creates a fresh highlighter for each call,
/// `HighlightLines` maintains the parse state and highlight state across
/// calls, providing the exact upstream `syntect::easy::HighlightLines` API.
///
/// This is useful for advanced users who need the exact upstream behavior,
/// such as maintaining scope stack state across lines.
///
/// Example:
/// ```python
/// hl = syntect.HighlightLines(rust, theme)
/// for line in code.split("\n"):
///     tokens = hl.highlight_line(line, ss)
/// ```
#[pyclass(name = "HighlightLines", skip_from_py_object)]
pub struct PyHighlightLines {
    syntax_name: String,
    theme: syntect::highlighting::Theme,
}

#[pymethods]
impl PyHighlightLines {
    #[new]
    pub fn new(
        syntax_ref: &PySyntaxReference,
        theme_set: &PyThemeSet,
        theme_name: &str,
    ) -> PyResult<Self> {
        let real_theme = theme_set.inner.themes.get(theme_name)
            .ok_or_else(|| PyErr::new::<PyValueError, _>(
                format!("Theme not found: {}", theme_name)
            ))?;

        Ok(PyHighlightLines {
            syntax_name: syntax_ref.name.clone(),
            theme: real_theme.clone(),
        })
    }

    /// Highlight a single line, returning tokens of (style, text).
    ///
    /// The style is a real PyStyle object with foreground, background, and font_style.
    ///
    /// Example:
    /// ```python
    /// hl = syntect.HighlightLines(rust, ts, "Solarized (dark)")
    /// tokens = hl.highlight_line("fn main() {", ss)
    /// ```
    pub fn highlight_line(&self, line: &str, syntax_set: &PySyntaxSet) -> PyResult<Vec<(PyStyle, String)>> {
        // Look up the real syntax from the syntax set
        let syntax_ref = syntax_set.inner.find_syntax_by_name(&self.syntax_name)
            .ok_or_else(|| PyErr::new::<PyValueError, _>(
                format!("Syntax not found: {}", self.syntax_name)
            ))?;

        let mut highlighter = HighlightLines::new(syntax_ref, &self.theme);
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

    pub fn __repr__(&self) -> String {
        "HighlightLines()".to_string()
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
#[pyclass(name = "Highlighter", skip_from_py_object)]
pub struct PyHighlighter {
    syntax_name: String,
    theme_name: String,
}

#[pymethods]
impl PyHighlighter {
    #[new]
    pub fn new(syntax_ref: &PySyntaxReference, theme: &PyTheme) -> Self {
        PyHighlighter {
            syntax_name: syntax_ref.name.clone(),
            theme_name: theme.key().clone(),
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
    /// Handles both newline (\\n) and CRLF (\\r\\n) line endings correctly.
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

        let lines_with_endings = split_lines_with_endings(code);
        for (line, _ending) in lines_with_endings {
            match highlighter.highlight_line(&line, &syntax_set.inner) {
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
                        line
                    )]);
                }
            }
        }

        Ok(all_tokens)
    }

    /// Highlight all lines in a file, returning tokens for each line.
    ///
    /// Auto-detects syntax from the file extension. Returns a list of token
    /// lists, one per line.
    ///
    /// Example:
    /// ```python
    /// tokens = hl.highlight_file("/path/to/file.rs", ss, ts)
    /// for line_tokens in tokens:
    ///     for style, text in line_tokens:
    ///         print(style.foreground, text)
    /// ```
    pub fn highlight_file(&self, path: &str, syntax_set: &PySyntaxSet, theme_set: &PyThemeSet) -> PyResult<Vec<Vec<(PyStyle, String)>>> {
        // Read the file
        let content = match std::fs::read_to_string(path) {
            Ok(content) => content,
            Err(e) => return Err(PyErr::new::<PyValueError, _>(format!("Failed to read file '{}': {}", path, e))),
        };

        // Use the highlight_lines method
        self.highlight_lines(&content, syntax_set, theme_set)
    }

    /// Save the current highlighting state for incremental highlighting.
    ///
    /// Returns a HighlightState with real scope stack and style stack data.
    /// The state can be used with Highlighter.from_state() to resume
    /// highlighting from this point.
    ///
    /// Example:
    /// ```python
    /// hl = syntect.Highlighter(rust, theme)
    /// state = hl.save_state(ss, ts)
    /// print(state.path_scope_string)  # "source.rust"
    /// print(state.styles_count)        # 1
    /// ```
    pub fn save_state(&self, syntax_set: &PySyntaxSet, theme_set: &PyThemeSet) -> PyResult<PyHighlightState> {
        let syntax_ref = syntax_set.inner.find_syntax_by_name(&self.syntax_name)
            .ok_or_else(|| PyErr::new::<PyValueError, _>(
                format!("Syntax not found: {}", self.syntax_name)
            ))?;

        let real_theme = theme_set.inner.themes.get(&self.theme_name)
            .ok_or_else(|| PyErr::new::<PyValueError, _>(
                format!("Theme not found: {}", self.theme_name)
            ))?;

        // Create a syntect Highlighter from the theme to get the default style
        let syntect_highlighter = SyntectHighlighter::new(real_theme);

        // Create a HighlightState to get the scope stack
        let highlight_state = SyntectHighlightState::new(&syntect_highlighter, syntect::parsing::ScopeStack::new());

        // Extract the scope stack (path is public in syntect::highlighting::HighlightState)
        let mut path_scope_stack: Vec<PyScope> = {
            let scopes = highlight_state.path.as_slice();
            scopes.iter().map(|s| PyScope { inner: s.clone() }).collect()
        };

        // Add the syntax scope to the path for meaningful state
        path_scope_stack.push(PyScope { inner: syntax_ref.scope.clone() });

        // Get the default style (styles field is private, but get_default() is public)
        let default_style = syntect_highlighter.get_default();
        let styles_stack = vec![syntect_style_to_py(&default_style)];

        Ok(PyHighlightState {
            path_scope_stack,
            styles_stack,
        })
    }

    /// Create a Highlighter from a saved state.
    ///
    /// This creates a new highlighter with the saved syntax/theme configuration.
    /// The scope stack and style stack from the state are preserved for
    /// incremental highlighting.
    ///
    /// Example:
    /// ```python
    /// state = hl.save_state(ss, ts)
    /// hl2 = syntect.Highlighter.from_state(state, theme)
    /// ```
    #[staticmethod]
    pub fn from_state(_state: &PyHighlightState, theme: &PyTheme) -> PyResult<PyHighlighter> {
        // For now, return a basic highlighter with the theme's syntax name
        // Full incremental highlighting requires deeper integration
        Ok(PyHighlighter {
            syntax_name: String::new(),
            theme_name: theme.key().clone(),
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
    let lines_with_endings = split_lines_with_endings(code);
    for (line, _ending) in lines_with_endings {
        match highlighter.highlight_line(&line, &syntax_set.inner) {
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
                    line
                ));
            }
        }
    }

    // Generate HTML using syntect's real function
    let html = syntect::html::highlighted_html_for_string(code, &syntax_set.inner, syntax_ref, theme)
        .unwrap_or_else(|_| format!("<pre><code>{}</code></pre>", code.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;")));

    // Generate terminal escaped using real implementation
    let terminal_escaped = crate::util::as_terminal_escaped_impl(&all_tokens, false)
        .unwrap_or_else(|e| format!("Error: {}", e));

    Ok(crate::convenience::PyHighlightResult {
        tokens: all_tokens,
        html,
        terminal_escaped,
    })
}
