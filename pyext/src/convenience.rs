//! Phase 5: Convenience & Polish - Enhanced HighlightResult with output methods

use pyo3::prelude::*;
use crate::style::{PyStyle, PyColor};




#[pyclass(name = "HighlightResult", skip_from_py_object)]
pub struct PyHighlightResult {
    pub tokens: Vec<(PyStyle, String)>,
    pub html: String,
    pub terminal_escaped: String,
}

#[pymethods]
impl PyHighlightResult {
    #[getter]
    pub fn tokens(&self) -> Vec<(PyStyle, String)> {
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

    pub fn as_html(&self, include_bg: &str, default_bg: Option<PyColor>) -> PyResult<String> {
        let include_bg_value = match include_bg {
            "no" | "false" | "0" => crate::util::IncludeBg::No,
            "yes" | "true" | "1" => crate::util::IncludeBg::Yes,
            _ => crate::util::IncludeBg::IfDifferent,
        };

        let html = crate::util::generate_html_from_tokens(&self.tokens, include_bg_value, default_bg);
        Ok(html)
    }

    pub fn as_terminal_escaped(&self, include_bg: bool) -> PyResult<String> {
        let mut result = String::new();

        for (style, text) in &self.tokens {
            if include_bg {
                result.push_str(&format!("\x1b[48;2;{};{};{}m",
                    style.background.r, style.background.g, style.background.b));
            }

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

    pub fn as_latex_escaped(&self) -> PyResult<String> {
        let mut result = String::new();
        let mut prev_style: Option<PyStyle> = None;

        for (style, text) in &self.tokens {
            if text == " " || text == "\n" {
                if prev_style == Some(style.clone()) {
                    if text == " " {
                        result.push(' ');
                    }
                    continue;
                }
            }

            if let Some(ps) = prev_style {
                if ps != style.clone() {
                    result.push('}');
                }
            }

            result.push_str(&format!(
                "\\textcolor[RGB]{{{},{},{}}}{{",
                style.foreground.r,
                style.foreground.g,
                style.foreground.b
            ));

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

            prev_style = Some(style.clone());
        }

        if prev_style.is_some() {
            result.push('}');
        }

        Ok(result)
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

