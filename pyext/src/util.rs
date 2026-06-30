//! Python bindings for syntect's output utilities (terminal, LaTeX).

use pyo3::prelude::*;

// ============================================================================
// as_terminal_escaped (stub)
// ============================================================================

/// Convert highlighted tokens to a 24-bit terminal escape string.
///
/// Example:
/// ```python
/// escaped = syntect.as_terminal_escaped(tokens, include_bg=True)
/// ```
#[pyfunction]
pub fn as_terminal_escaped(tokens: Vec<(String, String)>, _include_bg: bool) -> String {
    // Stub: in Phase 3, this will call the real syntect util function
    let mut result = String::new();
    for (_, text) in tokens {
        result.push_str(&text);
    }
    result
}

// ============================================================================
// as_html (stub)
// ============================================================================

/// Convert highlighted tokens to HTML with inline styles.
///
/// Example:
/// ```python
/// html = syntect.as_html(tokens, include_bg="if_different")
/// ```
#[pyfunction]
pub fn as_html(tokens: Vec<(String, String)>, _include_bg: &str) -> String {
    // Stub: in Phase 3, this will call the real syntect util function
    let mut result = String::new();
    for (style, text) in tokens {
        result.push_str(&format!("<span style=\"{}\">{}</span>", style, text));
    }
    result
}

// ============================================================================
// as_latex_escaped (stub)
// ============================================================================

/// Convert highlighted tokens to LaTeX \textcolor output.
///
/// Example:
/// ```python
/// latex = syntect.as_latex_escaped(tokens)
/// ```
#[pyfunction]
pub fn as_latex_escaped(tokens: Vec<(String, String)>) -> String {
    // Stub: in Phase 3, this will call the real syntect util function
    let mut result = String::new();
    for (_, text) in tokens {
        result.push_str(&text);
    }
    result
}
