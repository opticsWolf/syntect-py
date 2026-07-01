//! Lazy HighlightResult — html/terminal computed on first access via OnceLock.
//!
//! Stores native syntect tokens so HTML/terminal can be generated lazily
//! without re-running the lexer.

use pyo3::prelude::*;
use std::sync::OnceLock;
use crate::style::{PyStyle, PyColor};
use syntect::highlighting::Style as SyntectStyle;

#[pyclass(name = "HighlightResult", skip_from_py_object)]
pub struct PyHighlightResult {
    pub tokens: Vec<(PyStyle, String)>,
    /// Native syntect tokens for lazy HTML/terminal generation.
    /// Stored separately to avoid PyStyle overhead during lexing.
    pub native_tokens: Vec<(SyntectStyle, String)>,
    /// Lazy HTML — computed once on first access from native_tokens.
    pub html: OnceLock<String>,
    /// Lazy terminal — computed once on first access from native_tokens.
    pub terminal_escaped: OnceLock<String>,
}

#[pymethods]
impl PyHighlightResult {
    #[getter]
    pub fn tokens(&self) -> Vec<(PyStyle, String)> {
        self.tokens.clone()
    }

    #[getter]
    pub fn html(&self) -> String {
        self.html.get_or_init(|| {
            // Generate HTML from native syntect tokens (no PyStyle overhead)
            if self.native_tokens.is_empty() {
                return String::new();
            }
            let native_refs: Vec<_> = self.native_tokens.iter()
                .map(|(s, t)| (*s, t.as_str()))
                .collect();
            let inner_html = crate::util::generate_html_from_syntect_tokens(
                &native_refs, crate::util::IncludeBg::Yes, None
            );
            format!("<pre><code>{}</code></pre>", inner_html)
        }).clone()
    }

    #[getter]
    pub fn terminal_escaped(&self) -> String {
        self.terminal_escaped.get_or_init(|| {
            // Generate terminal from native syntect tokens
            let native_refs: Vec<_> = self.native_tokens.iter()
                .map(|(s, t)| (*s, t.as_str()))
                .collect();
            crate::util::generate_terminal_from_syntect_tokens(&native_refs, false)
        }).clone()
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
        Ok(crate::util::as_terminal_escaped_impl_convenience(&self.tokens, include_bg))
    }

    pub fn as_latex_escaped(&self) -> PyResult<String> {
        Ok(crate::util::as_latex_escaped_impl_convenience(&self.tokens))
    }

    pub fn __repr__(&self) -> String {
        format!(
            "HighlightResult(tokens={}, html_len={}, terminal_len={})",
            self.tokens.len(),
            self.html.get().map_or(0, |s| s.len()),
            self.terminal_escaped.get().map_or(0, |s| s.len())
        )
    }
}
