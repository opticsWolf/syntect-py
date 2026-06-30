//! Python bindings for syntect's output utilities (terminal, LaTeX).
//!
//! Implements real wrappers around syntect's as_24_bit_terminal_escaped,
//! as_latex_escaped, split_at, modify_range, and LinesWithEndings.

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
/// The `include_bg` parameter controls background color output:
/// - "no" / "false" / "0": never include background
/// - "yes" / "true" / "1": always include background
/// - anything else: only include background if different from theme default
///
/// The `default_bg` parameter provides the theme's default background color.
/// When `include_bg="if_different"`, backgrounds matching the default are
/// omitted from the HTML output.
///
/// Example:
/// ```python
/// tokens = hl.highlight_line("fn main() {", ss, ts)
/// html = syntect.as_html(tokens, "if_different", default_bg)
/// print(html)
/// ```
#[pyfunction]
pub fn as_html(tokens: Vec<(PyStyle, String)>, include_bg: &str, default_bg: Option<PyColor>) -> PyResult<String> {
    let include_bg_value = match include_bg {
        "no" | "false" | "0" => IncludeBg::No,
        "yes" | "true" | "1" => IncludeBg::Yes,
        _ => IncludeBg::IfDifferent,
    };

    let html = generate_html_from_tokens(&tokens, include_bg_value, default_bg);
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
/// print(latex)  # \textcolor[RGB]{180,142,173}{fn}\textcolor[RGB]{192;197;206}{ }...
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

/// Internal enum for background color inclusion policy.
pub enum IncludeBg {
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

/// Generate HTML from highlighted tokens, with optional background color
/// based on the `IncludeBg` policy and the theme's default background.
///
/// This is the shared implementation used by both `as_html()` and
/// `PyHighlightResult.as_html()` to avoid code duplication.
#[allow(unused_assignments)]
pub fn generate_html_from_tokens(
    tokens: &[(PyStyle, String)],
    include_bg: IncludeBg,
    default_bg: Option<PyColor>,
) -> String {
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
                html.push_str(&escape_html(text));
                continue;
            }
        }

        // Open a new span with inline styles
        html.push_str("<span style=\"");

        // Background color
        let should_include_bg = match include_bg {
            IncludeBg::Yes => true,
            IncludeBg::No => false,
            IncludeBg::IfDifferent => default_bg.as_ref().map_or(true, |dbg| {
                style.background.r != dbg.r ||
                style.background.g != dbg.g ||
                style.background.b != dbg.b
            }),
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
        html.push_str(&escape_html(text));

        prev_style = Some(style.clone());
        span_open = true;
    }

    if span_open {
        html.push_str("</span>");
    }

    html
}


// ============================================================================
// split_at — Split tokens at position
// ============================================================================

/// Split a list of (style, text) tokens at a character position.
///
/// Returns two lists: tokens before the split position and tokens from the split position.
/// If the split falls in the middle of a token's text, that token is split.
///
/// Example:
/// ```python
/// tokens = [(style1, "hello"), (style2, "world")]
/// left, right = syntect.split_at(tokens, 5)
/// # left = [(style1, "hello")]
/// # right = [(style2, "world")]
/// ```
#[pyfunction]
pub fn split_at(
    tokens: Vec<(PyStyle, String)>,
    position: usize,
) -> PyResult<(Vec<(PyStyle, String)>, Vec<(PyStyle, String)>)> {
    let mut left: Vec<(PyStyle, String)> = Vec::new();
    let mut right: Vec<(PyStyle, String)> = Vec::new();
    let mut remaining = position;

    for (style, text) in tokens {
        if remaining > 0 {
            if remaining >= text.len() {
                left.push((style.clone(), text.clone()));
                remaining -= text.len();
            } else {
                left.push((style.clone(), text[..remaining].to_string()));
                right.push((style, text[remaining..].to_string()));
                remaining = 0;
            }
        } else {
            right.push((style, text));
        }
    }

    Ok((left, right))
}


// ============================================================================
// modify_range — Modify tokens in a range
// ============================================================================

/// Replace the style of tokens in a character range with a new style.
///
/// The range is [range_start, range_end) in character positions.
/// Tokens within this range get their style replaced with `new_style`.
///
/// Example:
/// ```python
/// tokens = [(style1, "hello"), (style2, "world")]
/// modified = syntect.modify_range(tokens, 0, 5, new_style)
/// ```
#[pyfunction]
pub fn modify_range(
    tokens: Vec<(PyStyle, String)>,
    range_start: usize,
    range_end: usize,
    new_style: PyStyle,
) -> PyResult<Vec<(PyStyle, String)>> {
    let mut result: Vec<(PyStyle, String)> = Vec::new();
    let mut char_pos = 0usize;

    for (style, text) in tokens {
        let text_len = text.len();

        // Case 1: entire text is before the range
        if char_pos + text_len <= range_start {
            result.push((style, text));
            char_pos += text_len;
            continue;
        }

        // Case 2: entire text is after the range
        if char_pos >= range_end {
            result.push((style, text));
            char_pos += text_len;
            continue;
        }

        // Case 3: text overlaps with the range
        let range_start_in_text = if char_pos < range_start {
            range_start - char_pos
        } else {
            0
        };

        let range_end_in_text = if char_pos + text_len > range_end {
            range_end - char_pos
        } else {
            text_len
        };

        // Only split if necessary (avoid empty strings from zero-length ranges)
        if range_start_in_text > 0 {
            result.push((style.clone(), text[..range_start_in_text].to_string()));
        }
        if range_start_in_text < range_end_in_text {
            result.push((new_style.clone(), text[range_start_in_text..range_end_in_text].to_string()));
        }
        if range_end_in_text < text_len {
            result.push((style, text[range_end_in_text..].to_string()));
        }

        char_pos += text_len;
    }

    Ok(result)
}


// ============================================================================
// LinesWithEndings — Python iterator class
// ============================================================================

/// Iterator that yields (line, ending) tuples from a string.
///
/// Each line is returned with its trailing newline/CR+LF intact.
/// The last line may not have an ending if the string doesn't end with a newline.
///
/// Example:
/// ```python
/// for line, ending in syntect.lines_with_endings("hello\nworld\n"):
///     print(repr(line), repr(ending))
/// # Output: ('hello', '\n') ('world', '\n')
/// ```
#[pyclass(name = "LinesWithEndings", skip_from_py_object)]
#[derive(Clone)]
pub struct PyLinesWithEndings {
    #[allow(dead_code)]
    content: String,
    index: usize,
    chars: Vec<char>,
}

#[pymethods]
impl PyLinesWithEndings {
    #[new]
    pub fn new(content: &str) -> Self {
        PyLinesWithEndings {
            content: content.to_string(),
            index: 0,
            chars: content.chars().collect(),
        }
    }

    pub fn __iter__(&self) -> PyLinesWithEndings {
        self.clone()
    }

    pub fn __next__(&mut self) -> Option<(String, String)> {
        if self.index >= self.chars.len() {
            return None;
        }

        let start = self.index;
        let mut line_end = start;

        while line_end < self.chars.len() {
            let ch = self.chars[line_end];
            if ch == '\n' {
                // Found newline ending
                self.index = line_end + 1;
                let line = String::from_iter(self.chars[start..line_end].iter());
                let ending = String::from_iter(self.chars[start..self.index].iter());
                return Some((line, ending));
            } else if ch == '\r' {
                // Check for \r\n
                if line_end + 1 < self.chars.len() && self.chars[line_end + 1] == '\n' {
                    self.index = line_end + 2;
                    let line = String::from_iter(self.chars[start..line_end].iter());
                    let ending = String::from_iter(self.chars[start..self.index].iter());
                    return Some((line, ending));
                } else {
                    // Just \r
                    self.index = line_end + 1;
                    let line = String::from_iter(self.chars[start..line_end].iter());
                    let ending = String::from_iter(self.chars[start..self.index].iter());
                    return Some((line, ending));
                }
            }
            line_end += 1;
        }

        // No newline found — return remaining text as last line
        if start < self.chars.len() {
            let line = String::from_iter(self.chars[start..].iter());
            self.index = self.chars.len();
            return Some((line, String::new()));
        }

        None
    }
}


// ============================================================================
// lines_with_endings — Create LinesWithEndings iterator
// ============================================================================

/// Create a LinesWithEndings iterator for a string.
///
/// Yields (line, ending) tuples where ending includes the newline characters.
#[pyfunction]
pub fn lines_with_endings(content: &str) -> PyLinesWithEndings {
    PyLinesWithEndings::new(content)
}
