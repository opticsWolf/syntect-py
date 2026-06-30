//! Python bindings for syntect's color and font style types.

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use syntect::highlighting::{Color, FontStyle, Style, StyleModifier};

// ============================================================================
// PyColor
// ============================================================================

/// A color in RGBA format.
///
/// Example:
/// ```python
/// c = syntect.Color(255, 0, 0, 255)  # Red
/// c = syntect.Color.from_hex("#FF0000")  # Red from hex
/// hex = c.to_hex()  # "#FF0000"
/// ```
#[pyclass(name = "Color")]
#[derive(Clone)]
pub struct PyColor {
    pub r: u8,
    pub g: u8,
    pub b: u8,
    pub a: u8,
}

#[pymethods]
impl PyColor {
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

// ============================================================================
// PyFontStyle
// ============================================================================

/// Font style flags (bold, italic, underline).
///
/// Supports bitwise operations:
/// ```python
/// style = syntect.FontStyle.BOLD | syntect.FontStyle.ITALIC
/// ```
#[pyclass(name = "FontStyle")]
#[derive(Clone)]
pub struct PyFontStyle {
    pub bits: u8,
}

#[pymethods]
impl PyFontStyle {
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

// ============================================================================
// PyStyle
// ============================================================================

/// A style combining foreground/background colors and font style.
#[pyclass(name = "Style")]
#[derive(Clone)]
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

    pub fn __repr__(&self) -> String {
        format!(
            "Style(fg={}, bg={}, style={})",
            self.foreground.to_hex(),
            self.background.to_hex(),
            self.font_style.bits
        )
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
}

// ============================================================================
// PyStyleModifier
// ============================================================================

/// A partial style change (some fields may be None).
#[pyclass(name = "StyleModifier")]
#[derive(Clone)]
pub struct PyStyleModifier {
    foreground: Option<PyColor>,
    background: Option<PyColor>,
    font_style: Option<PyFontStyle>,
}

#[pymethods]
impl PyStyleModifier {
    #[new]
    pub fn new(
        foreground: Option<PyColor>,
        background: Option<PyColor>,
        font_style: Option<PyFontStyle>,
    ) -> Self {
        PyStyleModifier { foreground, background, font_style }
    }
}
