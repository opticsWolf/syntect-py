//! Python bindings for syntect's theme set management.
#![allow(unused)]

use pyo3::prelude::*;
use syntect::highlighting::{Theme as SyntectTheme, ThemeSet as SyntectThemeSet};
use crate::errors;
use crate::style::{PyColor, PyFontStyle, PyStyleModifier};

// ============================================================================
// PyThemeSettings (read-only wrapper)
// ============================================================================

#[pyclass(name = "ThemeSettings", skip_from_py_object)]
#[derive(Clone)]
pub struct PyThemeSettings {
    foreground: Option<PyColor>,
    background: Option<PyColor>,
    selection_background: Option<PyColor>,
    gutter_foreground: Option<PyColor>,
    gutter_background: Option<PyColor>,
}

#[pymethods]
impl PyThemeSettings {
    #[getter]
    pub fn foreground(&self) -> Option<PyColor> {
        self.foreground.clone()
    }

    #[getter]
    pub fn background(&self) -> Option<PyColor> {
        self.background.clone()
    }

    #[getter]
    pub fn selection_background(&self) -> Option<PyColor> {
        self.selection_background.clone()
    }

    #[getter]
    pub fn gutter_foreground(&self) -> Option<PyColor> {
        self.gutter_foreground.clone()
    }

    #[getter]
    pub fn gutter_background(&self) -> Option<PyColor> {
        self.gutter_background.clone()
    }

    pub fn __repr__(&self) -> String {
        format!(
            "ThemeSettings(fg={:?}, bg={:?}, sel_bg={:?})",
            self.foreground.as_ref().map(|c| c.to_hex()),
            self.background.as_ref().map(|c| c.to_hex()),
            self.selection_background.as_ref().map(|c| c.to_hex())
        )
    }
}

// ============================================================================
// PyThemeItem
// ============================================================================

#[pyclass(name = "ThemeItem", skip_from_py_object)]
#[derive(Clone)]
pub struct PyThemeItem {
    scope: String,
    foreground: Option<PyColor>,
    background: Option<PyColor>,
    font_style: u8,
    style_modifier: String,
    style: PyStyleModifier,
}

#[pymethods]
impl PyThemeItem {
    #[getter]
    pub fn scope(&self) -> String {
        self.scope.clone()
    }

    #[getter]
    pub fn foreground(&self) -> Option<PyColor> {
        self.foreground.clone()
    }

    #[getter]
    pub fn background(&self) -> Option<PyColor> {
        self.background.clone()
    }

    #[getter]
    pub fn font_style(&self) -> u8 {
        self.font_style
    }

    #[getter]
    pub fn style_modifier(&self) -> String {
        self.style_modifier.clone()
    }

    #[getter]
    pub fn style(&self) -> PyStyleModifier {
        PyStyleModifier {
            foreground: self.foreground.clone(),
            background: self.background.clone(),
            font_style: if self.font_style != 0 {
                Some(PyFontStyle { bits: self.font_style })
            } else {
                None
            },
        }
    }

    pub fn __repr__(&self) -> String {
        format!("ThemeItem(scope='{}', fg={:?}, bg={:?}, font={})",
            self.scope, self.foreground.as_ref().map(|c| c.to_hex()), self.background.as_ref().map(|c| c.to_hex()), self.font_style)
    }
}

// ============================================================================
// PyTheme (read-only wrapper)
// ============================================================================

#[pyclass(name = "Theme", skip_from_py_object)]
#[derive(Clone)]
pub struct PyTheme {
    key: String,
    name: String,
    author: String,
    settings: PyThemeSettings,
    scopes: Vec<PyThemeItem>,
}

#[pymethods]
impl PyTheme {
    #[getter]
    pub fn key(&self) -> String {
        self.key.clone()
    }

    #[getter]
    pub fn name(&self) -> String {
        self.name.clone()
    }

    #[getter]
    pub fn author(&self) -> String {
        self.author.clone()
    }

    #[getter]
    pub fn settings(&self) -> PyThemeSettings {
        self.settings.clone()
    }

    #[getter]
    pub fn scopes(&self) -> Vec<PyThemeItem> {
        self.scopes.clone()
    }

    pub fn __repr__(&self) -> String {
        format!("Theme(name='{}', author='{}')", self.name, self.author)
    }
}

// ============================================================================
// PyThemeSet
// ============================================================================

#[pyclass(name = "ThemeSet", skip_from_py_object)]
pub struct PyThemeSet {
    pub inner: SyntectThemeSet,
}

#[pymethods]
impl PyThemeSet {
    #[new]
    pub fn new() -> Self {
        PyThemeSet { inner: SyntectThemeSet::new() }
    }

    #[staticmethod]
    pub fn load_defaults() -> Self {
        PyThemeSet { inner: SyntectThemeSet::load_defaults() }
    }

    pub fn add_from_folder(&mut self, path: &str) -> PyResult<Vec<String>> {
        match SyntectThemeSet::load_from_folder(path) {
            Ok(loaded) => {
                for (name, theme) in loaded.themes {
                    self.inner.themes.insert(name, theme);
                }
                Ok(vec![])
            }
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyOSError, _>(
                errors::loading_error_to_string(&e),
            )),
        }
    }

    #[staticmethod]
    pub fn builder() -> PyResult<PyThemeSet> {
        Ok(PyThemeSet { inner: SyntectThemeSet::new() })
    }

    pub fn get_theme(&self, key: &str) -> Option<PyTheme> {
        self.inner.themes.get(key).map(|t: &SyntectTheme| {
            PyTheme {
                key: key.to_string(),
                name: t.name.clone().unwrap_or_default(),
                author: t.author.clone().unwrap_or_default(),
                settings: PyThemeSettings {
                    foreground: t.settings.foreground.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: 255,
                    }),
                    background: t.settings.background.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: 255,
                    }),
                    selection_background: t.settings.selection.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: 255,
                    }),
                    gutter_foreground: t.settings.gutter_foreground.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: 255,
                    }),
                    gutter_background: t.settings.gutter.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: 255,
                    }),
                },
                scopes: t.scopes.iter().map(|s| {
                    let fm = PyStyleModifier {
                        foreground: s.style.foreground.as_ref().map(|c| PyColor {
                            r: c.r, g: c.g, b: c.b, a: 255,
                        }),
                        background: s.style.background.as_ref().map(|c| PyColor {
                            r: c.r, g: c.g, b: c.b, a: 255,
                        }),
                        font_style: s.style.font_style.map(|fs| PyFontStyle { bits: fs.bits() }),
                    };
                    PyThemeItem {
                        scope: format!("{:?}", s.scope),
                        foreground: s.style.foreground.as_ref().map(|c| PyColor {
                            r: c.r, g: c.g, b: c.b, a: 255,
                        }),
                        background: s.style.background.as_ref().map(|c| PyColor {
                            r: c.r, g: c.g, b: c.b, a: 255,
                        }),
                        font_style: s.style.font_style.map_or(0, |fs| fs.bits()),
                        style_modifier: format!("{:?}", s.style),
                        style: fm,
                    }
                }).collect(),
            }
        })
    }

    pub fn theme_names(&self) -> Vec<String> {
        self.inner.themes.keys().cloned().collect()
    }

    /// Create a ThemeSet from a .themedump file.
    #[staticmethod]
    pub fn from_dump(path: &str) -> PyResult<PyThemeSet> {
        match syntect::dumps::from_dump_file::<syntect::highlighting::ThemeSet, &str>(path) {
            Ok(ts) => Ok(PyThemeSet { inner: ts }),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyOSError, _>(
                format!("Failed to load theme dump: {}", e),
            )),
        }
    }

    /// Save this ThemeSet to a .themedump file.
    pub fn to_dump(&self, path: &str) -> PyResult<()> {
        match syntect::dumps::dump_to_file(&self.inner, path) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyOSError, _>(
                format!("Failed to save theme dump: {}", e),
            )),
        }
    }

    pub fn __repr__(&self) -> String {
        format!("ThemeSet(themes={})", self.inner.themes.len())
    }
}
