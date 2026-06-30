//! Python bindings for syntect's output utilities (terminal, LaTeX).
//!
//! Implements real wrappers around syntect's as_24_bit_terminal_escaped,
//! as_latex_escaped, and other output formatting functions.

use pyo3::prelude::*;
use crate::style::{PyStyle, PyColor};


// ============================================================================
// as_terminal_escaped_impl (internal, no Python exceptions)
// ============================================================================

/// Internal implementation of terminal escape generation.
/// Used by highlight_string to generate proper terminal output.
pub fn as_terminal_escaped_impl(tokens: &[(PyStyle, String)], include_bg: bool) -> Result<String, String> {
    let mut result = String::new();

    for (style, text) in tokens {
        if include_bg {
            result.push_str(&format!("\x1b[48;2;{};{};{}m",
                style.background.r, style.background.g, style.background.b));
        }

        // Blend foreground with background for alpha transparency
        let fg = style.foreground.clone();
        let bg = style.background.clone();
        let blended_fg = if fg.a == 0xff {
            fg
        } else {
            let ratio = fg.a as u32;
            PyColor {
                r: ((fg.r as u32 * ratio + bg.r as u32 * (255 - ratio)) / 255) as u8,
                g: ((fg.g as u32 * ratio + bg.g as u32 * (255 - ratio)) / 255) as u8,
                b: ((fg.b as u32 * ratio + bg.b as u32 * (255 - ratio)) / 255) as u8,
                a: 255,
            }
        };

        result.push_str(&format!("\x1b[38;2;{};{};{}m{}",
            blended_fg.r, blended_fg.g, blended_fg.b, text));
    }

    Ok(result)
}


// ============================================================================
// as_terminal_escaped (real implementation)
// ============================================================================

/// Convert highlighted tokens to a 24-bit terminal escape string.
///
/// The tokens should be in the format returned by Highlighter.highlight_line(),
/// i.e., [(PyStyle, text), ...].
///
/// Example:
/// ```python
/// tokens = hl.highlight_line("fn main() {", ss, ts)
/// escaped = syntect.as_terminal_escaped(tokens, include_bg=True)
/// print(escaped)  # \x1b[38;2;180;142;173mfn\x1b[38;2;192;197;206m ...
/// ```
#[pyfunction]
pub fn as_terminal_escaped(tokens: Vec<(PyStyle, String)>, include_bg: bool) -> PyResult<String> {
    let mut result = String::new();

    for (style, text) in tokens {
        if include_bg {
            result.push_str(&format!("\x1b[48;2;{};{};{}m",
                style.background.r, style.background.g, style.background.b));
        }

        // Blend foreground with background for alpha transparency
        let fg = style.foreground.clone();
        let bg = style.background.clone();
        let blended_fg = if fg.a == 0xff {
            fg
        } else {
            let ratio = fg.a as u32;
            PyColor {
                r: ((fg.r as u32 * ratio + bg.r as u32 * (255 - ratio)) / 255) as u8,
                g: ((fg.g as u32 * ratio + bg.g as u32 * (255 - ratio)) / 255) as u8,
                b: ((fg.b as u32 * ratio + bg.b as u32 * (255 - ratio)) / 255) as u8,
                a: 255,
            }
        };

        result.push_str(&format!("\x1b[38;2;{};{};{}m{}",
            blended_fg.r, blended_fg.g, blended_fg.b, text));
    }

    Ok(result)
}


// ============================================================================
// as_html (real implementation)
// ============================================================================

/// Convert highlighted tokens to HTML with inline styles.
///
/// Adjacent tokens with the same style are merged into a single <span>.
///
/// Example:
/// ```python
/// tokens = hl.highlight_line("fn main() {", ss, ts)
/// html = syntect.as_html(tokens, include_bg="if_different")
/// print(html)
/// ```
#[pyfunction]
#[allow(unused_assignments)]
pub fn as_html(tokens: Vec<(PyStyle, String)>, include_bg: &str) -> PyResult<String> {
    let include_bg = match include_bg {
        "no" | "false" | "0" => IncludeBg::No,
        "yes" | "true" | "1" => IncludeBg::Yes,
        _ => IncludeBg::IfDifferent,
    };

    let mut html = String::new();
    let mut prev_style: Option<PyStyle> = None;
    let mut span_open = false;

    for (style, text) in tokens {
        // Check if we need to close the current span
        if span_open {
            if prev_style != Some(style.clone()) {
                html.push_str("</span>");
                span_open = false;
            } else {
                // Same style, just append text
                html.push_str(&escape_html(&text));
                continue;
            }
        }

        // Open a new span with inline styles
        html.push_str("<span style=\"");

        // Background color
        let should_include_bg = match include_bg {
            IncludeBg::Yes => true,
            IncludeBg::No => false,
            IncludeBg::IfDifferent => true,
        };

        if should_include_bg {
            html.push_str(&format!("background-color:{};", style.background.to_hex()));
        }

        // Font styles
        if style.font_style.bits & 2 != 0 {
            html.push_str("text-decoration:underline;");
        }
        if style.font_style.bits & 1 != 0 {
            html.push_str("font-weight:bold;");
        }
        if style.font_style.bits & 4 != 0 {
            html.push_str("font-style:italic;");
        }

        // Foreground color
        html.push_str(&format!("color:{};\">", style.foreground.to_hex()));
        html.push_str(&escape_html(&text));

        prev_style = Some(style);
        span_open = true;
    }

    if span_open {
        html.push_str("</span>");
    }

    Ok(html)
}


// ============================================================================
// as_latex_escaped (real implementation)
// ============================================================================

/// Convert highlighted tokens to LaTeX \textcolor output.
///
/// The tokens should be in the format returned by Highlighter.highlight_line().
/// Background color is ignored. Spaces and newlines are handled specially.
///
/// Example:
/// ```python
/// tokens = hl.highlight_line("fn main() {", ss, ts)
/// latex = syntect.as_latex_escaped(tokens)
/// print(latex)  # \textcolor[RGB]{180,142,173}{fn}\textcolor[RGB]{192,197,206}{ }...
/// ```
#[pyfunction]
pub fn as_latex_escaped(tokens: Vec<(PyStyle, String)>) -> PyResult<String> {
    let mut result = String::new();
    let mut prev_style: Option<PyStyle> = None;

    for (style, text) in tokens {
        // Skip spaces and newlines when style hasn't changed
        if text == " " || text == "\n" {
            if prev_style == Some(style.clone()) {
                if text == " " {
                    result.push(' ');
                }
                continue;
            }
        }

        // Close previous \textcolor if style changed
        if let Some(ps) = prev_style {
            if ps != style {
                result.push('}');
            }
        }

        // Open new \textcolor
        result.push_str(&format!(
            "\\textcolor[RGB]{{{},{},{}}}{{",
            style.foreground.r,
            style.foreground.g,
            style.foreground.b
        ));

        // Escape LaTeX special characters
        let mut escaped = String::new();
        for ch in text.chars() {
            match ch {
                '\\' => escaped.push_str("\\\\"),
                '{' => escaped.push_str("\\{"),
                '}' => escaped.push_str("\\}"),
                _ => escaped.push(ch),
            }
        }
        result.push_str(&escaped);

        prev_style = Some(style);
    }

    if prev_style.is_some() {
        result.push('}');
    }

    Ok(result)
}


// ============================================================================
// Helper enums and functions
// ============================================================================

enum IncludeBg {
    No,
    Yes,
    IfDifferent,
}

fn escape_html(text: &str) -> String {
    text.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
}
