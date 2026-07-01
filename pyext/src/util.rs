//! Python bindings for syntect's output utilities (terminal, LaTeX).
//!
//! Implements real wrappers around syntect's as_24_bit_terminal_escaped,
//! as_latex_escaped, split_at, modify_range, and LinesWithEndings.
//!
//! **Optimized path**: Functions suffixed with `_from_syntect` work directly with
//! syntect's native types, avoiding PyStyle allocation overhead.

use pyo3::prelude::*;
use crate::style::{PyStyle, PyColor};
use syntect::highlighting::{Style as SyntectStyle, Color as SyntectColor, FontStyle as SyntectFontStyle};


// ============================================================================
// as_terminal_escaped_impl (internal, no Python exceptions)
// ============================================================================

/// Internal implementation of terminal escape generation.
/// Used by highlight_string to generate proper terminal output.
#[allow(dead_code)]
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

/// Internal implementation of terminal escape generation (convenience version).
/// Used by PyHighlightResult.as_terminal_escaped() to avoid code duplication.
pub fn as_terminal_escaped_impl_convenience(tokens: &[(PyStyle, String)], include_bg: bool) -> String {
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

    result
}

/// Internal implementation of LaTeX escape generation (convenience version).
/// Used by PyHighlightResult.as_latex_escaped() to avoid code duplication.
pub fn as_latex_escaped_impl_convenience(tokens: &[(PyStyle, String)]) -> String {
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
            if ps != style.clone() {
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

        // Escape all TeX special characters: \ { } & % $ # _ ^ ~
        let mut escaped = String::new();
        for ch in text.chars() {
            match ch {
                '\\' => escaped.push_str("\\textbackslash{}"),
                '{' => escaped.push_str("\\{"),
                '}' => escaped.push_str("\\}"),
                '&' => escaped.push_str("\\&"),
                '%' => escaped.push_str("\\%"),
                '$' => escaped.push_str("\\$"),
                '#' => escaped.push_str("\\#"),
                '_' => escaped.push_str("\\_"),
                '^' => escaped.push_str("\\textasciicircum{}"),
                '~' => escaped.push_str("\\textasciitilde{}"),
                c => escaped.push(c),
            }
        }
        result.push_str(&escaped);

        prev_style = Some(style.clone());
    }

    if prev_style.is_some() {
        result.push('}');
    }

    result
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
    let mut any_token = false;

    for (style, text) in tokens {
        any_token = true;
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

    // Append terminal reset to prevent color leaking past output
    if any_token {
        result.push_str("\x1b[0m");
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

        // Escape all TeX special characters: \ { } & % $ # _ ^ ~
        let mut escaped = String::new();
        for ch in text.chars() {
            match ch {
                '\\' => escaped.push_str("\\textbackslash{}"),
                '{' => escaped.push_str("\\{"),
                '}' => escaped.push_str("\\}"),
                '&' => escaped.push_str("\\&"),
                '%' => escaped.push_str("\\%"),
                '$' => escaped.push_str("\\$"),
                '#' => escaped.push_str("\\#"),
                '_' => escaped.push_str("\\_"),
                '^' => escaped.push_str("\\textasciicircum{}"),
                '~' => escaped.push_str("\\textasciitilde{}"),
                c => escaped.push(c),
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
// Optimized output generation from syntect native types (zero PyStyle overhead)
// ============================================================================

/// Optimized HTML generation directly from syntect's native `(Style, &str)` tuples.
/// Avoids creating PyStyle objects entirely — used by highlight_string for the
/// fast path where we only need output, not Python-exposed tokens.
#[allow(unused_assignments)]
pub fn generate_html_from_syntect_tokens<'a>(
    tokens: &[(SyntectStyle, &'a str)],
    include_bg: IncludeBg,
    default_bg: Option<SyntectColor>,
) -> String {
    let mut html = String::with_capacity(tokens.iter().map(|(_, t)| t.len()).sum());
    let mut prev_style: Option<SyntectStyle> = None;
    let mut span_open = false;

    for (style, text) in tokens {
        if span_open {
            if prev_style != Some(*style) {
                html.push_str("</span>");
                span_open = false;
            } else {
                escape_html_into(text, &mut html);
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
            write_bg_color_hex(&style.background, &mut html);
        }

        // Font styles
        let fs = style.font_style;
        if fs.contains(SyntectFontStyle::UNDERLINE) {
            html.push_str("text-decoration:underline;");
        }
        if fs.contains(SyntectFontStyle::BOLD) {
            html.push_str("font-weight:bold;");
        }
        if fs.contains(SyntectFontStyle::ITALIC) {
            html.push_str("font-style:italic;");
        }

        // Foreground color
        write_fg_color_hex(&style.foreground, &mut html);
        html.push_str(">\"");
        escape_html_into(text, &mut html);

        prev_style = Some(*style);
        span_open = true;
    }

    if span_open {
        html.push_str("</span>");
    }

    html
}

/// Optimized terminal escape generation directly from syntect's native types.
pub fn generate_terminal_from_syntect_tokens(
    tokens: &[(SyntectStyle, &str)],
    include_bg: bool,
) -> String {
    let mut result = String::with_capacity(tokens.iter().map(|(_, t)| t.len()).sum::<usize>() + 256);

    for (style, text) in tokens {
        if include_bg {
            write_bg_ansi(&style.background, &mut result);
        }

        // Blend foreground with background for alpha transparency
        let blended_fg = blend_color(&style.foreground, &style.background);
        write_fg_ansi(&blended_fg, text, &mut result);
    }

    result
}

/// Blend foreground with background for alpha transparency.
fn blend_color(fg: &SyntectColor, bg: &SyntectColor) -> SyntectColor {
    if fg.a == 0xff {
        *fg
    } else {
        let ratio = fg.a as u32;
        SyntectColor {
            r: ((fg.r as u32 * ratio + bg.r as u32 * (255 - ratio)) / 255) as u8,
            g: ((fg.g as u32 * ratio + bg.g as u32 * (255 - ratio)) / 255) as u8,
            b: ((fg.b as u32 * ratio + bg.b as u32 * (255 - ratio)) / 255) as u8,
            a: 255,
        }
    }
}

/// Write background color as hex into HTML buffer.
#[inline]
fn write_bg_color_hex(color: &SyntectColor, html: &mut String) {
    html.push_str("background-color:#");
    write_hex_u8(color.r, html);
    write_hex_u8(color.g, html);
    write_hex_u8(color.b, html);
    html.push(';');
}

/// Write foreground color as hex into HTML buffer.
#[inline]
fn write_fg_color_hex(color: &SyntectColor, html: &mut String) {
    html.push_str("color:#");
    write_hex_u8(color.r, html);
    write_hex_u8(color.g, html);
    write_hex_u8(color.b, html);
    html.push('>');
}

/// Write a u8 as two hex digits into a string buffer.
#[inline]
fn write_hex_u8(val: u8, buf: &mut String) {
    const HEX: &[u8; 16] = b"0123456789ABCDEF";
    buf.push(char::from(HEX[(val >> 4) as usize] as char));
    buf.push(char::from(HEX[(val & 0xF) as usize] as char));
}

/// Write background ANSI escape sequence.
#[inline]
fn write_bg_ansi(color: &SyntectColor, buf: &mut String) {
    buf.push_str("\x1b[48;2;");
    write_u8_dec(color.r, buf);
    buf.push(';');
    write_u8_dec(color.g, buf);
    buf.push(';');
    write_u8_dec(color.b, buf);
    buf.push('m');
}

/// Write foreground ANSI escape sequence with text.
#[inline]
fn write_fg_ansi(color: &SyntectColor, text: &str, buf: &mut String) {
    buf.push_str("\x1b[38;2;");
    write_u8_dec(color.r, buf);
    buf.push(';');
    write_u8_dec(color.g, buf);
    buf.push(';');
    write_u8_dec(color.b, buf);
    buf.push('m');
    buf.push_str(text);
}

/// Write a u8 as decimal digits into a string buffer (no format! overhead).
#[inline]
fn write_u8_dec(val: u8, buf: &mut String) {
    if val < 10 {
        buf.push(char::from(b'0' + val as u8));
    } else if val < 100 {
        buf.push(char::from(b'0' + (val / 10) as u8));
        buf.push(char::from(b'0' + (val % 10) as u8));
    } else {
        buf.push(char::from(b'0' + (val / 100) as u8));
        buf.push(char::from(b'0' + ((val / 10) % 10) as u8));
        buf.push(char::from(b'0' + (val % 10) as u8));
    }
}

/// Escape HTML special characters directly into a buffer (no intermediate String).
#[inline]
fn escape_html_into(text: &str, buf: &mut String) {
    let mut last_start = 0;
    for (i, ch) in text.char_indices() {
        match ch {
            '&' | '<' | '>' | '"' => {
                buf.push_str(&text[last_start..i]);
                match ch {
                    '&' => buf.push_str("&amp;"),
                    '<' => buf.push_str("&lt;"),
                    '>' => buf.push_str("&gt;"),
                    '"' => buf.push_str("&quot;"),
                    _ => unreachable!(),
                }
                last_start = i + ch.len_utf8();
            }
            _ => {}
        }
    }
    buf.push_str(&text[last_start..]);
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
/// The position parameter is in **characters**, not bytes. This correctly handles
/// multi-byte Unicode characters. For example, a Chinese character counts as 1
/// position, not 3 bytes.
///
/// Uses single-pass char_indices() walk — O(n) instead of O(n²).
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
    let mut split_done = false;

    for (style, text) in tokens {
        if split_done {
            right.push((style, text));
            continue;
        }

        let char_len = text.chars().count();
        if remaining >= char_len {
            left.push((style.clone(), text.clone()));
            remaining -= char_len;
        } else if remaining == 0 {
            // Split at start of this token — all goes to right
            right.push((style, text));
            split_done = true;
        } else {
            // Single-pass: find byte offset at char position 'remaining'
            let byte_idx = text.char_indices()
                .nth(remaining)
                .map_or(text.len(), |(i, _)| i);
            left.push((style.clone(), text[..byte_idx].to_string()));
            right.push((style, text[byte_idx..].to_string()));
            split_done = true;
        }
    }

    Ok((left, right))
}


// ============================================================================
// modify_range — Modify tokens in a range
// ============================================================================

/// Replace the style of tokens in a character range with a new style.
///
/// The range is [range_start, range_end) in **character** positions (not bytes).
/// This correctly handles multi-byte Unicode characters. For example, a Chinese
/// character counts as 1 position, not 3 bytes.
///
/// Uses single-pass char_indices() walk — O(n) instead of O(n²).
///
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
        let char_len = text.chars().count();

        // Case 1: entire text is before the range
        if char_pos + char_len <= range_start {
            result.push((style, text));
            char_pos += char_len;
            continue;
        }

        // Case 2: entire text is after the range
        if char_pos >= range_end {
            result.push((style, text));
            char_pos += char_len;
            continue;
        }

        // Case 3: text overlaps with the range
        let range_start_in_text = if char_pos < range_start {
            range_start - char_pos
        } else {
            0
        };

        let range_end_in_text = if char_pos + char_len > range_end {
            range_end - char_pos
        } else {
            char_len
        };

        // Single-pass: compute byte indices once for both start and end
        if range_start_in_text > 0 {
            let start_idx = text.char_indices().nth(range_start_in_text).map_or(text.len(), |(i, _)| i);
            result.push((style.clone(), text[..start_idx].to_string()));
        }
        if range_start_in_text < range_end_in_text {
            let start_idx = text.char_indices().nth(range_start_in_text).map_or(text.len(), |(i, _)| i);
            let end_idx = text.char_indices().nth(range_end_in_text).map_or(text.len(), |(i, _)| i);
            result.push((new_style.clone(), text[start_idx..end_idx].to_string()));
        }
        if range_end_in_text < char_len {
            let end_idx = text.char_indices().nth(range_end_in_text).map_or(text.len(), |(i, _)| i);
            result.push((style, text[end_idx..].to_string()));
        }

        char_pos += char_len;
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
/// Optimized to use str::find instead of Vec<char> materialization.
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
    content: String,
    index: usize,
}

#[pymethods]
impl PyLinesWithEndings {
    #[new]
    pub fn new(content: &str) -> Self {
        PyLinesWithEndings {
            content: content.to_string(),
            index: 0,
        }
    }

    pub fn __iter__(&self) -> PyLinesWithEndings {
        self.clone()
    }

    pub fn __next__(&mut self) -> Option<(String, String)> {
        let content = &self.content;
        if self.index >= content.len() {
            return None;
        }

        let start = self.index;
        let remaining = &content[self.index..];

        // Check for \r\n first (must come before plain \n check)
        if let Some(crlf_pos) = remaining.find("\r\n") {
            let line = content[start..self.index + crlf_pos].to_string();
            let ending = "\r\n".to_string();
            self.index += crlf_pos + 2;
            return Some((line, ending));
        }

        // Check for standalone \r
        if let Some(cr_pos) = remaining.find('\r') {
            let line = content[start..self.index + cr_pos].to_string();
            let ending = "\r".to_string();
            self.index += cr_pos + 1;
            return Some((line, ending));
        }

        // Check for standalone \n
        if let Some(nl_pos) = remaining.find('\n') {
            let line = content[start..self.index + nl_pos].to_string();
            let ending = "\n".to_string();
            self.index += nl_pos + 1;
            return Some((line, ending));
        }

        // No newline found — return remaining text as last line
        if start < content.len() {
            let line = content[start..].to_string();
            self.index = content.len();
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

// ============================================================================
// Unit tests for pure helpers
// ============================================================================

#[cfg(test)]
mod tests {
    use crate::util::*;
    use crate::highlighter::split_lines_with_endings;

    #[test]
    fn test_split_lines_with_endings_lf() {
        let result = split_lines_with_endings("hello\nworld\n");
        assert_eq!(result.len(), 2);
        assert_eq!(result[0], ("hello".to_string(), "\n".to_string()));
        assert_eq!(result[1], ("world".to_string(), "\n".to_string()));
    }

    #[test]
    fn test_split_lines_with_endings_crlf() {
        let result = split_lines_with_endings("hello\r\nworld\r\n");
        assert_eq!(result.len(), 2);
        assert_eq!(result[0], ("hello".to_string(), "\r\n".to_string()));
        assert_eq!(result[1], ("world".to_string(), "\r\n".to_string()));
    }

    #[test]
    fn test_split_lines_with_endings_mixed() {
        let result = split_lines_with_endings("a\nb\r\nc\rd");
        assert_eq!(result.len(), 4);
        assert_eq!(result[0], ("a".to_string(), "\n".to_string()));
        assert_eq!(result[1], ("b".to_string(), "\r\n".to_string()));
        assert_eq!(result[2], ("c".to_string(), "\r".to_string()));
        assert_eq!(result[3], ("d".to_string(), "".to_string()));
    }

    #[test]
    fn test_split_lines_with_endings_no_trailing() {
        let result = split_lines_with_endings("hello");
        assert_eq!(result.len(), 1);
        assert_eq!(result[0], ("hello".to_string(), "".to_string()));
    }

    #[test]
    fn test_split_lines_with_endings_empty() {
        let result = split_lines_with_endings("");
        assert_eq!(result.len(), 0);
    }

    #[test]
    fn test_escape_html() {
        assert_eq!(escape_html(""), "");
        assert_eq!(escape_html("hello"), "hello");
        assert_eq!(escape_html("<script>"), "&lt;script&gt;");
        assert_eq!(escape_html("a&b<c>d\"e"), "a&amp;b&lt;c&gt;d&quot;e");
    }

    #[test]
    fn test_split_at_boundary() {
        let style = crate::style::PyStyle {
            foreground: crate::style::PyColor { r: 255, g: 0, b: 0, a: 255 },
            background: crate::style::PyColor { r: 0, g: 0, b: 0, a: 255 },
            font_style: crate::style::PyFontStyle { bits: 0 },
        };
        let tokens = vec![
            (style.clone(), "hello".to_string()),
            (style.clone(), "world".to_string()),
        ];
        let (left, right) = split_at(tokens.clone(), 5).unwrap();
        assert_eq!(left.len(), 1);
        assert_eq!(left[0].1, "hello");
        assert_eq!(right.len(), 1);
        assert_eq!(right[0].1, "world");
    }

    #[test]
    fn test_split_at_zero() {
        let style = crate::style::PyStyle {
            foreground: crate::style::PyColor { r: 255, g: 0, b: 0, a: 255 },
            background: crate::style::PyColor { r: 0, g: 0, b: 0, a: 255 },
            font_style: crate::style::PyFontStyle { bits: 0 },
        };
        let tokens = vec![(style, "hello".to_string())];
        let (left, right) = split_at(tokens, 0).unwrap();
        assert_eq!(left.len(), 0);
        assert_eq!(right.len(), 1);
        assert_eq!(right[0].1, "hello");
    }

    #[test]
    fn test_modify_range_full_token() {
        let style1 = crate::style::PyStyle {
            foreground: crate::style::PyColor { r: 255, g: 0, b: 0, a: 255 },
            background: crate::style::PyColor { r: 0, g: 0, b: 0, a: 255 },
            font_style: crate::style::PyFontStyle { bits: 0 },
        };
        let style2 = crate::style::PyStyle {
            foreground: crate::style::PyColor { r: 0, g: 255, b: 0, a: 255 },
            background: crate::style::PyColor { r: 0, g: 0, b: 0, a: 255 },
            font_style: crate::style::PyFontStyle { bits: 0 },
        };
        let new_style = crate::style::PyStyle {
            foreground: crate::style::PyColor { r: 0, g: 0, b: 255, a: 255 },
            background: crate::style::PyColor { r: 0, g: 0, b: 0, a: 255 },
            font_style: crate::style::PyFontStyle { bits: 0 },
        };
        let tokens = vec![
            (style1, "hello".to_string()),
            (style2, "world".to_string()),
        ];
        let result = modify_range(tokens, 0, 5, new_style).unwrap();
        assert_eq!(result.len(), 2);
        assert_eq!(result[0].1, "hello");
        assert_eq!(result[0].0.foreground.r, 0);
        assert_eq!(result[0].0.foreground.g, 0);
        assert_eq!(result[0].0.foreground.b, 255);
        assert_eq!(result[1].1, "world");
    }
}
