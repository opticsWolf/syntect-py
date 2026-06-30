//! Python bindings for syntect's HTML output utilities.

use pyo3::prelude::*;

// ============================================================================
// css_for_theme (stub)
// ============================================================================

/// Generate CSS for a theme.
///
/// Example:
/// ```python
/// css = syntect.css_for_theme(theme, "spaced")
/// ```
#[pyfunction]
pub fn css_for_theme(theme_name: &str, class_style: &str) -> String {
    format!(
        "/* CSS for theme: {} */\n/* class_style: {} */",
        theme_name, class_style
    )
}

// ============================================================================
// highlighted_html_for_string (stub)
// ============================================================================

/// Generate highlighted HTML for a string.
///
/// Example:
/// ```python
/// html = syntect.highlighted_html_for_string(code, syntax, theme, ss)
/// ```
#[pyfunction]
pub fn highlighted_html_for_string(
    code: &str,
    syntax: &str,
    _theme: &str,
) -> String {
    format!(
        "<pre><code class=\"{}\">{}</code></pre>",
        syntax,
        code.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;")
    )
}

// ============================================================================
// highlighted_html_at_line_and_column_number (stub)
// ============================================================================

/// Generate highlighted HTML with line and column number attributes.
#[pyfunction]
pub fn highlighted_html_at_line_and_column_number(
    code: &str,
    syntax: &str,
    _theme: &str,
    start_line: usize,
) -> String {
    let lines: Vec<&str> = code.split('\n').collect();
    let mut html = String::from("<pre><code>");
    for (i, line) in lines.iter().enumerate() {
        if i > 0 {
            html.push('\n');
        }
        html.push_str(&format!(
            "<span data-line=\"{}\">{}</span>",
            start_line + i,
            line.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;")
        ));
    }
    html.push_str("</code></pre>");
    html
}
