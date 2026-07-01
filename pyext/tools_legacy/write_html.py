#!/usr/bin/env python
#
# DEPRECATED: This script used to generate pyext/src/html.rs but is now stale.
# The checked-in html.rs is hand-maintained and is the source of truth.
# DO NOT RUN THIS SCRIPT — it will overwrite html.rs with a stripped-down
# version that breaks the build.
#
# See docs/IMPROVEMENT_PLAN.md §4.1 for details.
#

content = r'''//! Python bindings for syntect's HTML output utilities.

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use syntect::easy::HighlightLines;
use syntect::html::{
    ClassStyle as SyntectClassStyle,
    css_for_theme_with_class_style,
    start_highlighted_html_snippet,
};
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

    let real_theme = syntect::highlighting::Theme {
        name: Some(theme.name().clone()),
        author: Some(theme.author().clone()),
        settings: syntect::highlighting::ThemeSettings::default(),
        scopes: Vec::new(),
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
                        font_style: crate::style::PyFontStyle { bits: style.font_style },
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
'''

with open('D:/User/Documents/Python/syntect-py/pyext/src/html.rs', 'w') as f:
    f.write(content)
print('html.rs written successfully')
