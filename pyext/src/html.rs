//! Python bindings for syntect's HTML output utilities.

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use syntect::easy::HighlightLines;
use syntect::html::{
    ClassStyle as SyntectClassStyle,
    IncludeBackground,
    css_for_theme_with_class_style,
    line_tokens_to_classed_spans,
    start_highlighted_html_snippet,
};
use crate::syntax_set::{PySyntaxReference, PySyntaxSet};
use crate::theme_set::{PyTheme, PyThemeSet};
use crate::style::PyStyle;


// ============================================================================
// Helper: convert PyClassStyle to SyntectClassStyle (no per-call leak)
// ============================================================================

/// Convert a PyClassStyle to SyntectClassStyle.
/// For kind=1 (spaced_prefixed), the prefix is &'static str (leaked once per instance).
fn py_class_style_to_syntect(cs: &PyClassStyle) -> SyntectClassStyle {
    match cs.kind {
        0 => SyntectClassStyle::Spaced,
        1 => SyntectClassStyle::SpacedPrefixed { prefix: cs.prefix_static },
        2 => SyntectClassStyle::SpacedPrefixed { prefix: "" },
        _ => SyntectClassStyle::Spaced,
    }
}


// ============================================================================
// PyClassStyle — CSS class style selector
// ============================================================================

#[pyclass(name = "ClassStyle")]
pub struct PyClassStyle {
    kind: usize,
    /// &'static str for SyntectClassStyle::SpacedPrefixed (kind=1).
    /// Leaked once per instance in spaced_prefixed() — not per call.
    /// SyntectClassStyle requires &'static str, so we can't avoid this.
    prefix_static: &'static str,
}

#[pymethods]
impl PyClassStyle {
    #[new]
    pub fn new(kind: &str) -> Self {
        match kind {
            "spaced" => PyClassStyle { kind: 0, prefix_static: "" },
            "spaced_prefixed" => PyClassStyle { kind: 1, prefix_static: "" },
            "class_attribute" => PyClassStyle { kind: 2, prefix_static: "" },
            _ => PyClassStyle { kind: 0, prefix_static: "" },
        }
    }

    #[staticmethod]
    pub fn spaced() -> PyClassStyle {
        PyClassStyle { kind: 0, prefix_static: "" }
    }

    #[staticmethod]
    pub fn spaced_prefixed(prefix: &str) -> PyResult<PyClassStyle> {
        // Leak the prefix as &'static str — only once per instance, not per call.
        // SyntectClassStyle::SpacedPrefixed requires &'static str, so this is necessary.
        let leaked = Box::leak(prefix.to_string().into_boxed_str());
        Ok(PyClassStyle { kind: 1, prefix_static: leaked })
    }

    #[staticmethod]
    pub fn class_attribute() -> PyClassStyle {
        PyClassStyle { kind: 2, prefix_static: "" }
    }

    pub fn __repr__(&self) -> String {
        match self.kind {
            0 => "ClassStyle('spaced')".to_string(),
            1 => "ClassStyle('spaced_prefixed')".to_string(),
            2 => "ClassStyle('class_attribute')".to_string(),
            _ => "ClassStyle('unknown')".to_string(),
        }
    }
}


// ============================================================================
// PyIncludeBg — background color inclusion policy
// ============================================================================

#[pyclass(name = "IncludeBg")]
pub struct PyIncludeBg {
    kind: usize,
}

#[pymethods]
impl PyIncludeBg {
    #[new]
    pub fn new(kind: &str) -> Self {
        match kind {
            "no" | "false" => PyIncludeBg { kind: 0 },
            "yes" | "true" => PyIncludeBg { kind: 1 },
            _ => PyIncludeBg { kind: 2 },
        }
    }

    #[staticmethod]
    pub fn no() -> PyIncludeBg {
        PyIncludeBg { kind: 0 }
    }

    #[staticmethod]
    pub fn yes() -> PyIncludeBg {
        PyIncludeBg { kind: 1 }
    }

    #[staticmethod]
    pub fn if_different() -> PyIncludeBg {
        PyIncludeBg { kind: 2 }
    }

    pub fn __repr__(&self) -> String {
        match self.kind {
            0 => "IncludeBg('no')".to_string(),
            1 => "IncludeBg('yes')".to_string(),
            2 => "IncludeBg('if_different')".to_string(),
            _ => "IncludeBg('unknown')".to_string(),
        }
    }
}


// ============================================================================
// css_for_theme — Generate CSS for a theme (string class_style)
// ============================================================================

/// Generate CSS for a theme using a string class style specifier.
///
/// The class_style parameter should be one of: "spaced", "spaced_prefixed",
/// or "class_attribute".
#[pyfunction]
pub fn css_for_theme(theme: &PyTheme, class_style: &str) -> PyResult<String> {
    let syntect_style = match class_style {
        "spaced" => SyntectClassStyle::Spaced,
        "class_attribute" => SyntectClassStyle::SpacedPrefixed { prefix: "" },
        _ => SyntectClassStyle::SpacedPrefixed { prefix: "syn-" },
    };

    // Build real syntect theme scopes from PyTheme data
    let scopes: Vec<syntect::highlighting::ThemeItem> = theme.scopes().iter().map(|item| {
        let mut style = syntect::highlighting::StyleModifier::default();

        if let Some(fg) = item.foreground() {
            style.foreground = Some(syntect::highlighting::Color {
                r: fg.r(), g: fg.g(), b: fg.b(), a: fg.a(),
            });
        }

        if let Some(bg) = item.background() {
            style.background = Some(syntect::highlighting::Color {
                r: bg.r(), g: bg.g(), b: bg.b(), a: bg.a(),
            });
        }

        let fs = item.font_style();
        if fs & 1 != 0 {
            style.font_style = Some(syntect::highlighting::FontStyle::BOLD);
        } else if fs & 2 != 0 {
            style.font_style = Some(syntect::highlighting::FontStyle::UNDERLINE);
        } else if fs & 4 != 0 {
            style.font_style = Some(syntect::highlighting::FontStyle::ITALIC);
        }

        // Parse scope string to extract scope atoms
        let scope_str = item.scope();
        let scope_selectors = scope_string_to_selectors(&scope_str);

        syntect::highlighting::ThemeItem {
            scope: scope_selectors,
            style,
        }
    }).collect();

    let real_theme = syntect::highlighting::Theme {
        name: Some(theme.name().clone()),
        author: Some(theme.author().clone()),
        settings: syntect::highlighting::ThemeSettings::default(),
        scopes,
    };

    css_for_theme_with_class_style(&real_theme, syntect_style)
        .map_err(|e| PyErr::new::<PyValueError, _>(format!("CSS generation failed: {}", e)))
}


// ============================================================================
// css_for_theme_class — Generate CSS for a theme (PyClassStyle object)
// ============================================================================

/// Generate CSS for a theme using a PyClassStyle object.
///
/// This overload allows using the prefix from ClassStyle.spaced_prefixed("custom-").
#[pyfunction]
pub fn css_for_theme_class(theme: &PyTheme, class_style: &PyClassStyle) -> PyResult<String> {
    let syntect_style = py_class_style_to_syntect(class_style);

    // Build real syntect theme scopes from PyTheme data
    let scopes: Vec<syntect::highlighting::ThemeItem> = theme.scopes().iter().map(|item| {
        let mut style = syntect::highlighting::StyleModifier::default();

        if let Some(fg) = item.foreground() {
            style.foreground = Some(syntect::highlighting::Color {
                r: fg.r(), g: fg.g(), b: fg.b(), a: fg.a(),
            });
        }

        if let Some(bg) = item.background() {
            style.background = Some(syntect::highlighting::Color {
                r: bg.r(), g: bg.g(), b: bg.b(), a: bg.a(),
            });
        }

        let fs = item.font_style();
        if fs & 1 != 0 {
            style.font_style = Some(syntect::highlighting::FontStyle::BOLD);
        } else if fs & 2 != 0 {
            style.font_style = Some(syntect::highlighting::FontStyle::UNDERLINE);
        } else if fs & 4 != 0 {
            style.font_style = Some(syntect::highlighting::FontStyle::ITALIC);
        }

        let scope_selectors = scope_string_to_selectors(&item.scope());

        syntect::highlighting::ThemeItem {
            scope: scope_selectors,
            style,
        }
    }).collect();

    let real_theme = syntect::highlighting::Theme {
        name: Some(theme.name().clone()),
        author: Some(theme.author().clone()),
        settings: syntect::highlighting::ThemeSettings::default(),
        scopes,
    };

    css_for_theme_with_class_style(&real_theme, syntect_style)
        .map_err(|e| PyErr::new::<PyValueError, _>(format!("CSS generation failed: {}", e)))
}


// ============================================================================
// highlighted_html_for_string_py — Full highlighted HTML string
// ============================================================================

/// Generate full highlighted HTML for a string.
///
/// The `include_bg` parameter controls background color output:
/// - "no" / "false" / "0": never include background
/// - "yes" / "true" / "1": always include background
/// - anything else: only include background if different from theme default
///
/// The `start_line` parameter sets the starting line number for the HTML output.
#[pyfunction]
pub fn highlighted_html_for_string_py(
    code: &str,
    syntax_ref: &PySyntaxReference,
    theme: &PyTheme,
    syntax_set: &PySyntaxSet,
    theme_set: &PyThemeSet,
    include_bg: &str,
    start_line: usize,
) -> PyResult<String> {
    let syntax = syntax_set.inner.find_syntax_by_name(&syntax_ref.name)
        .ok_or_else(|| PyErr::new::<PyValueError, _>(
            format!("Syntax not found: {}", syntax_ref.name)
        ))?;

    let real_theme = theme_set.inner.themes.get(&theme.key())
        .ok_or_else(|| PyErr::new::<PyValueError, _>(
            format!("Theme not found: {}", theme.key())
        ))?;

    // Determine IncludeBackground policy
    let bg_policy: syntect::html::IncludeBackground = match include_bg {
        "no" | "false" | "0" => IncludeBackground::No,
        "yes" | "true" | "1" => IncludeBackground::Yes,
        _ => IncludeBackground::IfDifferent(real_theme.settings.background.unwrap_or(
            syntect::highlighting::Color { r: 0, g: 0, b: 0, a: 255 }
        )),
    };

    let mut highlighter = HighlightLines::new(syntax, real_theme);
    let mut html = String::new();

    // Open <pre><code> with line-numbering if start_line > 0
    let (pre_tag, _default_bg) = start_highlighted_html_snippet(real_theme);
    html.push_str(&pre_tag);

    for (line_idx, line) in code.split('\n').enumerate() {
        let line_num = start_line + line_idx;

        match highlighter.highlight_line(line, &syntax_set.inner) {
            Ok(regions) => {
                // Use syntect's upstream styled_line_to_highlighted_html with bg_policy
                match syntect::html::styled_line_to_highlighted_html(
                    &regions.iter().map(|(s, t)| (*s, *t)).collect::<Vec<_>>(),
                    bg_policy,
                ) {
                    Ok(line_html) => {
                        html.push_str(&format!("<span class=\"line\" id=\"l{}\">", line_num));
                        html.push_str(&line_html);
                        html.push_str("</span>\n");
                    }
                    Err(_) => {
                        html.push_str("\n");
                    }
                }
            }
            Err(_) => {
                html.push_str(&format!("<span class=\"line\" id=\"l{}\">{}</span>\n",
                    line_num, html_escape(line)));
            }
        }
    }

    html.push_str("</code></pre>\n");
    Ok(html)
}

fn html_escape(s: &str) -> String {
    s.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;").replace('"', "&quot;")
}


// ============================================================================
// highlighted_html_at_line_and_column_number — HTML with line numbers
// ============================================================================

#[pyfunction]
pub fn highlighted_html_at_line_and_column_number(
    code: &str,
    syntax_ref: &PySyntaxReference,
    theme: &PyTheme,
    syntax_set: &PySyntaxSet,
    theme_set: &PyThemeSet,
    start_line: usize,
) -> PyResult<String> {
    let syntax = syntax_set.inner.find_syntax_by_name(&syntax_ref.name)
        .ok_or_else(|| PyErr::new::<PyValueError, _>(
            format!("Syntax not found: {}", syntax_ref.name)
        ))?;

    let real_theme = theme_set.inner.themes.get(&theme.key())
        .ok_or_else(|| PyErr::new::<PyValueError, _>(
            format!("Theme not found: {}", theme.key())
        ))?;

    let mut highlighter = HighlightLines::new(syntax, real_theme);
    let mut html = String::new();

    let (pre_tag, _bg) = start_highlighted_html_snippet(real_theme);
    html.push_str(&pre_tag);

    for (line_idx, line) in code.split('\n').enumerate() {
        let line_num = start_line + line_idx;

        match highlighter.highlight_line(line, &syntax_set.inner) {
            Ok(ranges) => {
                let mut line_html = format!("<span data-line=\"{}\">", line_num);
                let mut prev_style: Option<PyStyle> = None;
                let mut span_open = false;

                for (style, text) in ranges {
                    let py_style = PyStyle {
                        foreground: crate::style::PyColor { r: style.foreground.r, g: style.foreground.g, b: style.foreground.b, a: style.foreground.a },
                        background: crate::style::PyColor { r: style.background.r, g: style.background.g, b: style.background.b, a: style.background.a },
                        font_style: crate::style::PyFontStyle { bits: style.font_style.bits() },
                    };

                    if span_open {
                        if prev_style != Some(py_style.clone()) {
                            line_html.push_str("</span>");
                            span_open = false;
                        }
                    }

                    if !span_open {
                        line_html.push_str("<span style=\"");
                        line_html.push_str(&format!("color:{};", py_style.foreground.to_hex()));
                        if py_style.font_style.bits & 1 != 0 {
                            line_html.push_str("font-weight:bold;");
                        }
                        if py_style.font_style.bits & 4 != 0 {
                            line_html.push_str("font-style:italic;");
                        }
                        line_html.push_str("\">");
                        span_open = true;
                    }

                    line_html.push_str(&text.replace('&', "&amp;")
                                        .replace('<', "&lt;")
                                        .replace('>', "&gt;"));

                    prev_style = Some(py_style);
                }

                if span_open {
                    line_html.push_str("</span>");
                }

                html.push_str(&line_html);
                html.push('\n');
            }
            Err(_) => {
                html.push_str(&format!("<span data-line=\"{}\">{}</span>\n",
                    line_num,
                    line.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;")));
            }
        }
    }

    html.push_str("</pre>\n");
    Ok(html)
}


// ============================================================================
// Helper: Parse scope selectors from scope string
// ============================================================================

/// Parse a scope string (e.g., "source.rust keyword.declaration") into ScopeSelectors.
/// Each whitespace-separated atom becomes a separate scope in the selector path.
fn scope_string_to_selectors(scope_str: &str) -> syntect::highlighting::ScopeSelectors {
    let parts: Vec<&str> = scope_str.split_whitespace().collect();
    let scopes: Vec<syntect::parsing::Scope> = parts
        .iter()
        .filter_map(|s| syntect::parsing::Scope::new(s.trim()).ok())
        .collect();
    
    syntect::highlighting::ScopeSelectors {
        selectors: scopes.into_iter().map(|s| {
            syntect::highlighting::ScopeSelector {
                path: syntect::parsing::ScopeStack::from_vec(vec![s]),
                excludes: Vec::new(),
            }
        }).collect(),
    }
}


// ============================================================================
// Alias functions for API compatibility
// ============================================================================

/// Alias for css_for_theme - generates CSS for a theme.
#[pyfunction]
pub fn generate_css(theme: &PyTheme, class_style: &str) -> PyResult<String> {
    css_for_theme(theme, class_style)
}

/// Alias for highlighted_html_for_string_py - creates full highlighted HTML.
#[pyfunction]
pub fn create_html_file(
    code: &str,
    syntax_ref: &PySyntaxReference,
    theme: &PyTheme,
    syntax_set: &PySyntaxSet,
    theme_set: &PyThemeSet,
) -> PyResult<String> {
    highlighted_html_for_string_py(code, syntax_ref, theme, syntax_set, theme_set, "if_different", 1)
}


// ============================================================================
// PyClassedHTMLGenerator — Class-based HTML output
// ============================================================================

/// A generator that produces class-based HTML output for highlighted syntax.
#[pyclass(name = "ClassedHTMLGenerator", skip_from_py_object)]
pub struct PyClassedHTMLGenerator {
    syntax_set: syntect::parsing::SyntaxSet,
    #[allow(dead_code)]
    syntax_ref: syntect::parsing::SyntaxReference,
    parse_state: syntect::parsing::ParseState,
    scope_stack: syntect::parsing::ScopeStack,
    open_spans: isize,
    html: String,
    style: SyntectClassStyle,
}

#[pymethods]
impl PyClassedHTMLGenerator {
    #[new]
    pub fn new(
        syntax_ref: &PySyntaxReference,
        syntax_set: &PySyntaxSet,
        class_style: &PyClassStyle,
    ) -> PyResult<Self> {
        let syntect_style = py_class_style_to_syntect(class_style);

        let syntax = syntax_set.inner.find_syntax_by_name(&syntax_ref.name)
            .ok_or_else(|| PyErr::new::<PyValueError, _>(
                format!("Syntax not found: {}", syntax_ref.name)
            ))?;

        let ss_clone = syntax_set.inner.clone();
        let sr_clone = syntax.clone();
        let parse_state = syntect::parsing::ParseState::new(&sr_clone);

        Ok(PyClassedHTMLGenerator {
            syntax_set: ss_clone,
            syntax_ref: sr_clone,
            parse_state,
            scope_stack: syntect::parsing::ScopeStack::new(),
            open_spans: 0,
            html: String::new(),
            style: syntect_style,
        })
    }

    /// Parse HTML for a line of code (with newline included in output).
    pub fn parse_html_for_line_which_includes_newline(
        &mut self, line: &str
    ) -> PyResult<()> {
        let output = self.parse_state.parse_line(line, &self.syntax_set)
            .map_err(|e| PyErr::new::<PyValueError, _>(format!("HTML generation failed: {}", e)))?;
        let (html_part, span_delta) = line_tokens_to_classed_spans(
            line,
            &output.ops,
            self.style.clone(),
            &mut self.scope_stack,
        ).map_err(|e| PyErr::new::<PyValueError, _>(format!("HTML generation failed: {}", e)))?;

        self.html.push_str(&html_part);
        self.open_spans += span_delta;
        Ok(())
    }

    /// Parse HTML for a line of code (without newline).
    pub fn parse_html_for_line(&mut self, line: &str) -> PyResult<()> {
        self.parse_html_for_line_which_includes_newline(line)?;
        if self.html.ends_with('\n') {
            self.html.pop();
        }
        Ok(())
    }

    /// Finalize the generated HTML and return it as a string.
    pub fn finalize(&mut self) -> String {
        for _ in 0..self.open_spans {
            self.html.push_str("</span>");
        }
        self.html.clone()
    }

    pub fn __repr__(&self) -> String {
        "ClassedHTMLGenerator()".to_string()
    }
}


// ============================================================================
// tokens_to_classed_spans — Convert tokens to classed HTML
// ============================================================================

#[pyfunction]
pub fn tokens_to_classed_spans(
    tokens: Vec<(PyStyle, String)>,
    class_style: &PyClassStyle,
) -> PyResult<String> {
    let syntect_style = py_class_style_to_syntect(class_style);

    // Build a simple ops list from the tokens (each token is a single span)
    let ops: Vec<(usize, syntect::parsing::ScopeStackOp)> = tokens.iter().enumerate()
        .map(|(i, _)| (i, syntect::parsing::ScopeStackOp::Push(syntect::parsing::Scope::new("token").unwrap())))
        .collect();

    let result = line_tokens_to_classed_spans(
        &tokens.iter().map(|(_, t)| t.clone()).collect::<Vec<String>>().join(""),
        &ops,
        syntect_style,
        &mut syntect::parsing::ScopeStack::new(),
    );

    match result {
        Ok((html, _delta)) => Ok(html),
        Err(e) => Err(PyErr::new::<PyValueError, _>(format!("HTML generation failed: {}", e))),
    }
}


// ============================================================================
// line_tokens_to_classed_spans_py — Python version
// ============================================================================

#[pyfunction]
pub fn line_tokens_to_classed_spans_py(
    line: &str,
    ops: Vec<(usize, String)>,
    class_style: &PyClassStyle,
) -> PyResult<(String, isize)> {
    let syntect_style = py_class_style_to_syntect(class_style);

    // Convert string-based ops to real ScopeStackOps
    let real_ops: Vec<(usize, syntect::parsing::ScopeStackOp)> = ops
        .into_iter()
        .map(|(pos, op_str)| {
            let op = match op_str.as_str() {
                "Push" => {
                    if let Ok(scope) = syntect::parsing::Scope::new("source") {
                        (pos, syntect::parsing::ScopeStackOp::Push(scope))
                    } else {
                        (pos, syntect::parsing::ScopeStackOp::Push(syntect::parsing::Scope::new("source").unwrap()))
                    }
                }
                "Pop" => (pos, syntect::parsing::ScopeStackOp::Pop(1)),
                "PopTo" => (pos, syntect::parsing::ScopeStackOp::Pop(1)),
                _ => (pos, syntect::parsing::ScopeStackOp::Push(syntect::parsing::Scope::new("source").unwrap())),
            };
            op
        })
        .collect();

    let result = line_tokens_to_classed_spans(
        line,
        &real_ops,
        syntect_style,
        &mut syntect::parsing::ScopeStack::new(),
    );

    match result {
        Ok((html, delta)) => Ok((html, delta)),
        Err(e) => Err(PyErr::new::<PyValueError, _>(format!("HTML generation failed: {}", e))),
    }
}


// ============================================================================
// styled_line_to_highlighted_html — Convert styled tokens to inline HTML
// ============================================================================

#[pyfunction]
pub fn styled_line_to_highlighted_html(
    tokens: Vec<(PyStyle, String)>,
    include_bg: &str,
    default_bg: Option<crate::style::PyColor>,
) -> PyResult<String> {
    // Determine IncludeBackground policy
    let bg: syntect::html::IncludeBackground = match include_bg {
        "no" | "false" | "0" => IncludeBackground::No,
        "yes" | "true" | "1" => IncludeBackground::Yes,
        _ => IncludeBackground::IfDifferent(default_bg.map_or(
            syntect::highlighting::Color { r: 0, g: 0, b: 0, a: 255 },
            |c| syntect::highlighting::Color { r: c.r, g: c.g, b: c.b, a: c.a },
        )),
    };

    // Convert PyStyle tuples to syntect tuples
    let syntect_tokens: Vec<(syntect::highlighting::Style, &str)> = tokens
        .iter()
        .map(|(s, t)| (
            syntect::highlighting::Style {
                foreground: syntect::highlighting::Color { r: s.foreground.r, g: s.foreground.g, b: s.foreground.b, a: s.foreground.a },
                background: syntect::highlighting::Color { r: s.background.r, g: s.background.g, b: s.background.b, a: s.background.a },
                font_style: syntect::highlighting::FontStyle::from_bits(s.font_style.bits).unwrap_or_default(),
            },
            t.as_str(),
        ))
        .collect();

    match syntect::html::styled_line_to_highlighted_html(&syntect_tokens, bg) {
        Ok(html) => Ok(html),
        Err(e) => Err(PyErr::new::<PyValueError, _>(format!("HTML generation failed: {}", e))),
    }
}
