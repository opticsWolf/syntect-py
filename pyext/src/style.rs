//! Python bindings for syntect's color and font style types.

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;

#[pyclass(name = "Color", from_py_object)]
#[derive(Clone, PartialEq)]
pub struct PyColor {
    pub r: u8,
    pub g: u8,
    pub b: u8,
    pub a: u8,
}

#[pymethods]
impl PyColor {
    #[getter]
    pub fn r(&self) -> u8 {
        self.r
    }

    #[getter]
    pub fn g(&self) -> u8 {
        self.g
    }

    #[getter]
    pub fn b(&self) -> u8 {
        self.b
    }

    #[getter]
    pub fn a(&self) -> u8 {
        self.a
    }

    #[new]
    pub fn new(r: u8, g: u8, b: u8, a: u8) -> Self {
        PyColor { r, g, b, a }
    }

    #[staticmethod]
    pub fn from_hex(hex_str: &str) -> PyResult<PyColor> {
        let hex = hex_str.trim();
        let clean = if hex.starts_with('#') { &hex[1..] } else { hex };
        if clean.len() != 6 {
            return Err(PyErr::new::<PyValueError, _>(
                "Hex string must be 6 characters (e.g., '#FF0000' or 'FF0000')",
            ));
        }
        match u32::from_str_radix(clean, 16) {
            Ok(val) => Ok(PyColor {
                r: ((val >> 16) & 0xFF) as u8,
                g: ((val >> 8) & 0xFF) as u8,
                b: (val & 0xFF) as u8,
                a: 255,
            }),
            Err(_) => Err(PyErr::new::<PyValueError, _>("Invalid hex string")),
        }
    }

    pub fn to_hex(&self) -> String {
        format!("#{:02X}{:02X}{:02X}", self.r, self.g, self.b)
    }

    pub fn __repr__(&self) -> String {
        format!("Color(r={}, g={}, b={}, a={})", self.r, self.g, self.b, self.a)
    }

    pub fn __eq__(&self, other: &PyColor) -> bool {
        self.r == other.r && self.g == other.g && self.b == other.b && self.a == other.a
    }
}

#[pyclass(name = "FontStyle", from_py_object)]
#[derive(Clone, PartialEq)]
pub struct PyFontStyle {
    pub bits: u8,
}

#[pymethods]
impl PyFontStyle {
    #[getter]
    pub fn bits(&self) -> u8 {
        self.bits
    }

    #[new]
    pub fn new(bits: u8) -> Self {
        PyFontStyle { bits }
    }

    #[classattr]
    pub const BOLD: PyFontStyle = PyFontStyle { bits: 1 };
    #[classattr]
    pub const ITALIC: PyFontStyle = PyFontStyle { bits: 4 };
    #[classattr]
    pub const UNDERLINE: PyFontStyle = PyFontStyle { bits: 2 };

    pub fn __or__(&self, other: &PyFontStyle) -> Self {
        PyFontStyle { bits: self.bits | other.bits }
    }

    pub fn __and__(&self, other: &PyFontStyle) -> Self {
        PyFontStyle { bits: self.bits & other.bits }
    }

    pub fn __xor__(&self, other: &PyFontStyle) -> Self {
        PyFontStyle { bits: self.bits ^ other.bits }
    }

    pub fn __invert__(&self) -> Self {
        PyFontStyle { bits: !self.bits }
    }

    pub fn __repr__(&self) -> String {
        let mut result = String::new();
        if self.bits & 1 != 0 {
            result.push_str("BOLD");
        }
        if self.bits & 2 != 0 {
            if !result.is_empty() {
                result.push_str(" | ");
            }
            result.push_str("UNDERLINE");
        }
        if self.bits & 4 != 0 {
            if !result.is_empty() {
                result.push_str(" | ");
            }
            result.push_str("ITALIC");
        }
        if result.is_empty() {
            result.push_str("(empty)");
        }
        format!("FontStyle({})", result)
    }
}

#[pyclass(name = "Style", from_py_object)]
#[derive(Clone, PartialEq)]
pub struct PyStyle {
    pub foreground: PyColor,
    pub background: PyColor,
    pub font_style: PyFontStyle,
}

#[pymethods]
impl PyStyle {
    #[new]
    pub fn new(
        foreground: PyColor,
        background: PyColor,
        font_style: PyFontStyle,
    ) -> Self {
        PyStyle { foreground, background, font_style }
    }

    #[getter]
    pub fn foreground(&self) -> PyColor {
        self.foreground.clone()
    }

    #[getter]
    pub fn background(&self) -> PyColor {
        self.background.clone()
    }

    #[getter]
    pub fn font_style(&self) -> PyFontStyle {
        self.font_style.clone()
    }

    pub fn __repr__(&self) -> String {
        format!("Style(fg={}, bg={}, style={})",
            self.foreground.to_hex(),
            self.background.to_hex(),
            self.font_style.bits)
    }

    pub fn __eq__(&self, other: &PyStyle) -> bool {
        self.foreground.r == other.foreground.r &&
        self.foreground.g == other.foreground.g &&
        self.foreground.b == other.foreground.b &&
        self.background.r == other.background.r &&
        self.background.g == other.background.g &&
        self.background.b == other.background.b &&
        self.font_style.bits == other.font_style.bits
    }

    #[staticmethod]
    pub fn from_hex_styles(fg_hex: &str, bg_hex: &str, font_bits: u8) -> PyResult<PyStyle> {
        let fg = PyColor::from_hex(fg_hex)?;
        let bg = PyColor::from_hex(bg_hex)?;
        Ok(PyStyle {
            foreground: fg,
            background: bg,
            font_style: PyFontStyle { bits: font_bits },
        })
    }
}

#[pyclass(name = "StyleModifier", from_py_object)]
#[derive(Clone, PartialEq)]
pub struct PyStyleModifier {
    foreground: Option<PyColor>,
    background: Option<PyColor>,
    font_style: Option<PyFontStyle>,
}

#[pymethods]
impl PyStyleModifier {
    #[getter]
    pub fn foreground(&self) -> Option<PyColor> {
        self.foreground.clone()
    }

    #[getter]
    pub fn background(&self) -> Option<PyColor> {
        self.background.clone()
    }

    #[getter]
    pub fn font_style(&self) -> Option<PyFontStyle> {
        self.font_style.clone()
    }

    #[new]
    pub fn new(
        foreground: Option<PyColor>,
        background: Option<PyColor>,
        font_style: Option<PyFontStyle>,
    ) -> Self {
        PyStyleModifier { foreground, background, font_style }
    }

    pub fn __repr__(&self) -> String {
        format!(
            "StyleModifier(fg={:?}, bg={:?}, font={:?})",
            self.foreground.as_ref().map(|c| c.to_hex()),
            self.background.as_ref().map(|c| c.to_hex()),
            self.font_style.as_ref().map(|fs| fs.bits)
        )
    }
}
