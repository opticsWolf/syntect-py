//! Python bindings for syntect's theme set management.

use pyo3::prelude::*;
use syntect::highlighting::{Theme as SyntectTheme, ThemeSet as SyntectThemeSet};
use crate::errors;

// ============================================================================
// PyThemeSettings (read-only wrapper)
// ============================================================================

/// Theme settings containing default colors and gutter settings.
#[pyclass(name = "ThemeSettings")]
#[derive(Clone)]
pub struct PyThemeSettings {
    foreground: Option<String>,
    background: Option<String>,
    selection_background: Option<String>,
    gutter_foreground: Option<String>,
    gutter_background: Option<String>,
}

#[pymethods]
impl PyThemeSettings {
    #[getter]
    pub fn foreground(&self) -> Option<String> {
        self.foreground.clone()
    }

    #[getter]
    pub fn background(&self) -> Option<String> {
        self.background.clone()
    }

    #[getter]
    pub fn selection_background(&self) -> Option<String> {
        self.selection_background.clone()
    }

    #[getter]
    pub fn gutter_foreground(&self) -> Option<String> {
        self.gutter_foreground.clone()
    }

    #[getter]
    pub fn gutter_background(&self) -> Option<String> {
        self.gutter_background.clone()
    }

    pub fn __repr__(&self) -> String {
        format!(
            "ThemeSettings(fg={:?}, bg={:?}, sel_bg={:?})",
            self.foreground, self.background, self.selection_background
        )
    }
}

// ============================================================================
// PyThemeItem
// ============================================================================

/// A single theme rule mapping scopes to styles.
#[pyclass(name = "ThemeItem")]
#[derive(Clone)]
pub struct PyThemeItem {
    scope: String,
    style_modifier: String,
}

#[pymethods]
impl PyThemeItem {
    #[getter]
    pub fn scope(&self) -> String {
        self.scope.clone()
    }

    #[getter]
    pub fn style_modifier(&self) -> String {
        self.style_modifier.clone()
    }

    pub fn __repr__(&self) -> String {
        format!("ThemeItem(scope='{}', style='{}')", self.scope, self.style_modifier)
    }
}

// ============================================================================
// PyTheme (read-only wrapper)
// ============================================================================

/// A syntax highlighting theme.
#[pyclass(name = "Theme")]
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

/// A set of loaded themes.
///
/// Example:
/// ```python
/// ts = syntect.ThemeSet.load_defaults()
/// theme = ts.get_theme("base16-ocean.dark")
/// print(ts.theme_names())
/// ```
#[pyclass(name = "ThemeSet")]
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

    /// Load all `.tmTheme` files from a folder into this theme set.
    ///
    /// Example:
    /// ```python
    /// ts = syntect.ThemeSet.load_defaults()
    /// warnings = ts.add_from_folder("/path/to/themes")
    /// print(ts.theme_names())
    /// ```
    pub fn add_from_folder(&mut self, path: &str) -> PyResult<Vec<String>> {
        // Collect warnings during loading
        match SyntectThemeSet::load_from_folder(path) {
            Ok(loaded) => {
                // Merge loaded themes into self
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

    /// Create a builder to load themes from disk.
    ///
    /// Example:
    /// ```python
    /// builder = syntect.ThemeSetBuilder()
    /// builder.add_from_folder("/path/to/themes")
    /// ts = builder.build()
    /// ```
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
                    foreground: t.settings.foreground.as_ref().map(|c| format!("#{:02X}{:02X}{:02X}", c.r, c.g, c.b)),
                    background: t.settings.background.as_ref().map(|c| format!("#{:02X}{:02X}{:02X}", c.r, c.g, c.b)),
                    selection_background: t.settings.selection.as_ref().map(|c| format!("#{:02X}{:02X}{:02X}", c.r, c.g, c.b)),
                    gutter_foreground: t.settings.gutter_foreground.as_ref().map(|c| format!("#{:02X}{:02X}{:02X}", c.r, c.g, c.b)),
                    gutter_background: t.settings.gutter.as_ref().map(|c| format!("#{:02X}{:02X}{:02X}", c.r, c.g, c.b)),
                },
                scopes: t.scopes.iter().map(|s| {
                    PyThemeItem {
                        scope: format!("{:?}", s.scope),
                        style_modifier: format!("{:?}", s.style),
                    }
                }).collect(),
            }
        })
    }

    pub fn theme_names(&self) -> Vec<String> {
        self.inner.themes.keys().cloned().collect()
    }

    pub fn __repr__(&self) -> String {
        format!("ThemeSet(themes={})", self.inner.themes.len())
    }
}
