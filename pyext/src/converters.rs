//! Shared conversion helpers between Python and syntect types.
//!
//! This module centralizes all Py↔Rust type conversions to avoid duplication
//! across the codebase.


use crate::style::{PyColor, PyFontStyle, PyStyle};
use syntect::highlighting::{Color as SyntectColor, FontStyle as SyntectFontStyle, Style as SyntectStyle};

/// Convert a syntect Style to a Python PyStyle.
pub fn syntect_style_to_py(style: &SyntectStyle) -> PyStyle {
    PyStyle {
        foreground: syntect_color_to_py(&style.foreground),
        background: syntect_color_to_py(&style.background),
        font_style: syntect_font_style_to_py(style.font_style),
    }
}

/// Convert a syntect Color to a Python PyColor.
pub fn syntect_color_to_py(color: &SyntectColor) -> PyColor {
    PyColor {
        r: color.r,
        g: color.g,
        b: color.b,
        a: color.a,
    }
}

/// Convert a syntect FontStyle to a Python PyFontStyle.
pub fn syntect_font_style_to_py(fs: SyntectFontStyle) -> PyFontStyle {
    PyFontStyle { bits: fs.bits() }
}

/// Convert a Python PyColor to a syntect Color.
#[allow(dead_code)]
pub fn py_color_to_syntect(color: &PyColor) -> SyntectColor {
    SyntectColor {
        r: color.r,
        g: color.g,
        b: color.b,
        a: color.a,
    }
}

/// Convert a Python PyFontStyle to a syntect FontStyle.
/// Uses from_bits() to correctly handle combined styles (e.g. bold+italic=5).
#[allow(dead_code)]
pub fn py_font_style_to_syntect(fs: &PyFontStyle) -> SyntectFontStyle {
    SyntectFontStyle::from_bits(fs.bits).unwrap_or_else(SyntectFontStyle::empty)
}

/// Create a default (empty) syntect FontStyle.
#[allow(dead_code)]
pub fn default_font_style() -> SyntectFontStyle {
    SyntectFontStyle::empty()
}

/// Create a syntect FontStyle from bits.
/// Uses from_bits() to correctly handle combined styles (e.g. bold+italic=5).
#[allow(dead_code)]
pub fn font_style_from_bits(bits: u8) -> SyntectFontStyle {
    SyntectFontStyle::from_bits(bits).unwrap_or_else(SyntectFontStyle::empty)
}

/// Convert a Python PyStyle to a syntect Style.
#[allow(dead_code)]
pub fn py_style_to_syntect(style: &PyStyle) -> SyntectStyle {
    SyntectStyle {
        foreground: py_color_to_syntect(&style.foreground),
        background: py_color_to_syntect(&style.background),
        font_style: py_font_style_to_syntect(&style.font_style),
    }
}
