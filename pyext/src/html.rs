//! Python bindings for syntect's HTML output utilities.

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use syntect::easy::HighlightLines;
use syntect::html::{
    ClassStyle as SyntectClassStyle,
    css_for_theme_with_class_style,
    start_highlighted_html_snippet,
};
use syntect::parsing::Scope as SyntectScope;
use crate::syntax_set::{PySyntaxReference, PySyntaxSet};
use crate::theme_set::{PyTheme, PyThemeSet};
use crate::style::PyStyle;


#[pyclass(name = "ClassStyle")]
pub struct PyClassStyle {
    kind: usize,
}

#[pymethods]
impl PyClassStyle {
    #[new]
    pub fn new(kind: &str) -> Self {
        match kind {
            "spaced" => PyClassStyle { kind: 0 },
            "spaced_prefixed" => PyClassStyle { kind: 1 },
            "class_attribute" => PyClassStyle { kind: 2 },
            _ => PyClassStyle { kind: 0 },
        }
    }

    #[staticmethod]
    pub fn spaced() -> PyClassStyle {
        PyClassStyle { kind: 0 }
    }

    #[staticmethod]
    pub fn spaced_prefixed(_prefix: &str) -> PyResult<PyClassStyle> {
        Ok(PyClassStyle { kind: 1 })
    }

    #[staticmethod]
    pub fn class_attribute() -> PyClassStyle {
        PyClassStyle { kind: 2 }
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
                r: fg.r(),
                g: fg.g(),
                b: fg.b(),
                a: fg.a(),
            });
        }

        if let Some(bg) = item.background() {
            style.background = Some(syntect::highlighting::Color {
                r: bg.r(),
                g: bg.g(),
                b: bg.b(),
                a: bg.a(),
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
        let scope_selectors = parse_scope_selectors(&scope_str);

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


#[pyfunction]
pub fn highlighted_html_for_string_py(
    code: &str,
    syntax_ref: &PySyntaxReference,
    theme: &PyTheme,
    syntax_set: &PySyntaxSet,
    theme_set: &PyThemeSet,
    _include_bg: &str,
    _start_line: usize,
) -> PyResult<String> {
    let syntax = syntax_set.inner.find_syntax_by_name(&syntax_ref.name)
        .ok_or_else(|| PyErr::new::<PyValueError, _>(
            format!("Syntax not found: {}", syntax_ref.name)
        ))?;

    let real_theme = theme_set.inner.themes.get(&theme.key())
        .ok_or_else(|| PyErr::new::<PyValueError, _>(
            format!("Theme not found: {}", theme.key())
        ))?;

    let result = syntect::html::highlighted_html_for_string(code, &syntax_set.inner, &syntax, real_theme);
    match result {
        Ok(html) => Ok(html),
        Err(e) => Err(PyErr::new::<PyValueError, _>(format!("HTML generation failed: {}", e))),
    }
}


#[pyfunction]
#[allow(unused_assignments)]
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
// Helper: Parse scope selectors from string representation
// ============================================================================

/// Parse a scope string like "ScopeSelectors { selectors: [ScopeSelector { path: ScopeStack { ... scopes: [<scope1> <scope2>] } }] }"
/// and extract the scope atoms to create proper ScopeSelectors.
fn parse_scope_selectors(scope_str: &str) -> syntect::highlighting::ScopeSelectors {
    let mut selectors: Vec<syntect::highlighting::ScopeSelector> = Vec::new();
    
    // Extract all <scope> patterns from the string
    let mut in_scopes_section = false;
    let mut current_scopes: Vec<String> = Vec::new();
    
    for ch in scope_str.chars() {
        if ch == '<' {
            in_scopes_section = true;
        }
        if in_scopes_section {
            if ch == '>' {
                in_scopes_section = false;
            } else if ch != ' ' && ch != '\n' && ch != '\t' {
                current_scopes.push(ch.to_string());
            }
        }
        if !in_scopes_section && (ch == ']' || ch == '}') && !current_scopes.is_empty() {
            // End of scopes section
            let scope_str: String = current_scopes.iter().cloned().collect();
            if let Ok(scope) = SyntectScope::new(&scope_str) {
                selectors.push(syntect::highlighting::ScopeSelector {
                    path: syntect::parsing::ScopeStack::from_vec(vec![scope]),
                    excludes: Vec::new(),
                });
            }
            current_scopes.clear();
        }
    }
    
    syntect::highlighting::ScopeSelectors {
        selectors,
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
