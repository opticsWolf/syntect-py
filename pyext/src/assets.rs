//! Python bindings for an embedded-assets compatibility layer.
//!
//! The published `syntect-assets` dump is tied to the upstream syntect data
//! layout and cannot be deserialized by this fork without introducing a second
//! incompatible syntect crate. This wrapper therefore uses the fork's own
//! default dumps and exposes the same useful fallback/theme-set API. The bat
//! grammar dump remains tracked as the next data-vendoring step in P5.

use pyo3::prelude::*;
use pyo3::exceptions::PyOSError;
use syntect::highlighting::{Theme, ThemeSet};
use syntect::parsing::SyntaxSet;

use crate::syntax_set::PySyntaxSet;
use crate::theme_set::{PyTheme, PyThemeSet};

#[pyclass(name = "Assets", unsendable)]
pub struct PyAssets {
    syntax_set: SyntaxSet,
    theme_set: ThemeSet,
    fallback_theme: String,
}

fn load_bundled_fallback_theme() -> Option<Theme> {
    let content = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/syntect/themes/Monokai Extended.tmTheme"));
    let mut reader = std::io::Cursor::new(content.as_bytes());
    ThemeSet::load_from_reader(&mut reader).ok()
}

#[pymethods]
impl PyAssets {
    /// Load the fork-compatible embedded syntax/theme defaults.
    #[staticmethod]
    pub fn from_binary() -> Self {
        let mut theme_set = ThemeSet::load_defaults();
        if let Some(theme) = load_bundled_fallback_theme() {
            theme_set.themes.insert("Monokai Extended".to_string(), theme);
        }
        Self {
            syntax_set: SyntaxSet::load_defaults_newlines(),
            theme_set,
            fallback_theme: "Monokai Extended".to_string(),
        }
    }

    pub fn set_fallback_theme(&mut self, name: &str) {
        self.fallback_theme = name.to_string();
    }

    pub fn get_syntax_set(&self) -> PyResult<PySyntaxSet> {
        Ok(PySyntaxSet { inner: self.syntax_set.clone() })
    }

    /// Resolve a theme, falling back to the configured theme and then the
    /// first available default if the requested name is unknown.
    pub fn get_theme(&self, name: &str) -> PyResult<PyTheme> {
        let key = if self.theme_set.themes.contains_key(name) {
            name
        } else if self.theme_set.themes.contains_key(&self.fallback_theme) {
            self.fallback_theme.as_str()
        } else {
            self.theme_set.themes.keys().next().map(String::as_str)
                .ok_or_else(|| PyErr::new::<PyOSError, _>("Assets contain no themes"))?
        };
        let theme = self.theme_set.themes.get(key)
            .ok_or_else(|| PyErr::new::<PyOSError, _>("Assets contain no themes"))?;
        Ok(PyTheme::from_syntect(key, theme))
    }

    pub fn theme_names(&self) -> Vec<String> {
        self.theme_set.themes.keys().cloned().collect()
    }

    pub fn get_theme_set(&self) -> PyThemeSet {
        let mut theme_set = ThemeSet::new();
        theme_set.themes.extend(self.theme_set.themes.iter().map(|(name, theme)| {
            (name.clone(), theme.clone())
        }));
        PyThemeSet { inner: theme_set }
    }

    pub fn __repr__(&self) -> String {
        format!("Assets(syntaxes={}, themes={})", self.syntax_set.syntaxes().len(), self.theme_set.themes.len())
    }
}

/// Create a fresh embedded-assets handle.
#[pyfunction]
pub fn load_assets() -> PyAssets {
    PyAssets::from_binary()
}
