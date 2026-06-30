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
        // Delegate to shared implementation to avoid code duplication
        Ok(crate::util::as_terminal_escaped_impl_convenience(&self.tokens, include_bg))
    }

    pub fn as_latex_escaped(&self) -> PyResult<String> {
        // Delegate to shared implementation to avoid code duplication
        Ok(crate::util::as_latex_escaped_impl_convenience(&self.tokens))
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

