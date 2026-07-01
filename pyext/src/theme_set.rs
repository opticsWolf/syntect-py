//! Python bindings for syntect's theme set management.

use pyo3::prelude::*;
use std::sync::Arc;
use syntect::highlighting::{Theme as SyntectTheme, ThemeSet as SyntectThemeSet};
use crate::errors;
use crate::style::{PyColor, PyFontStyle, PyStyleModifier};

// ============================================================================
// PyUnderlineOption (enum for bracket/tag options)
// ============================================================================

/// Underline style for bracket matching and tag highlighting.
#[pyclass(name = "UnderlineOption", skip_from_py_object)]
#[derive(Clone)]
pub struct PyUnderlineOption {
    pub kind: String,
}

#[pymethods]
impl PyUnderlineOption {
    #[staticmethod]
    pub fn none_() -> Option<PyUnderlineOption> {
        None
    }

    #[staticmethod]
    pub fn underline() -> Option<PyUnderlineOption> {
        Some(PyUnderlineOption { kind: "underline".to_string() })
    }

    #[staticmethod]
    pub fn stippled_underline() -> Option<PyUnderlineOption> {
        Some(PyUnderlineOption { kind: "stippled_underline".to_string() })
    }

    #[staticmethod]
    pub fn squiggly_underline() -> Option<PyUnderlineOption> {
        Some(PyUnderlineOption { kind: "squiggly_underline".to_string() })
    }

    pub fn __repr__(&self) -> String {
        format!("UnderlineOption({})", self.kind)
    }
}

/// Convert upstream UnderlineOption to PyUnderlineOption
fn to_underline_option(opt: &Option<syntect::highlighting::UnderlineOption>) -> Option<PyUnderlineOption> {
    match opt {
        None => None,
        Some(u) => Some(PyUnderlineOption {
            kind: format!("{:?}", u),
        }),
    }
}

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
    // NEW fields from upstream ThemeSettings
    caret: Option<PyColor>,
    line_highlight: Option<PyColor>,
    misspelling: Option<PyColor>,
    minimap_border: Option<PyColor>,
    accent: Option<PyColor>,
    popup_css: Option<String>,
    phantom_css: Option<String>,
    bracket_contents_foreground: Option<PyColor>,
    bracket_contents_options: Option<PyUnderlineOption>,
    brackets_foreground: Option<PyColor>,
    brackets_background: Option<PyColor>,
    brackets_options: Option<PyUnderlineOption>,
    tags_foreground: Option<PyColor>,
    tags_options: Option<PyUnderlineOption>,
    highlight: Option<PyColor>,
    find_highlight: Option<PyColor>,
    find_highlight_foreground: Option<PyColor>,
    selection_foreground: Option<PyColor>,
    selection_border: Option<PyColor>,
    inactive_selection: Option<PyColor>,
    inactive_selection_foreground: Option<PyColor>,
    guide: Option<PyColor>,
    active_guide: Option<PyColor>,
    stack_guide: Option<PyColor>,
    shadow: Option<PyColor>,
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

    // NEW getters for all additional ThemeSettings fields
    #[getter]
    pub fn caret(&self) -> Option<PyColor> {
        self.caret.clone()
    }

    #[getter]
    pub fn line_highlight(&self) -> Option<PyColor> {
        self.line_highlight.clone()
    }

    #[getter]
    pub fn misspelling(&self) -> Option<PyColor> {
        self.misspelling.clone()
    }

    #[getter]
    pub fn minimap_border(&self) -> Option<PyColor> {
        self.minimap_border.clone()
    }

    #[getter]
    pub fn accent(&self) -> Option<PyColor> {
        self.accent.clone()
    }

    #[getter]
    pub fn popup_css(&self) -> Option<String> {
        self.popup_css.clone()
    }

    #[getter]
    pub fn phantom_css(&self) -> Option<String> {
        self.phantom_css.clone()
    }

    #[getter]
    pub fn bracket_contents_foreground(&self) -> Option<PyColor> {
        self.bracket_contents_foreground.clone()
    }

    #[getter]
    pub fn bracket_contents_options(&self) -> Option<PyUnderlineOption> {
        self.bracket_contents_options.clone()
    }

    #[getter]
    pub fn brackets_foreground(&self) -> Option<PyColor> {
        self.brackets_foreground.clone()
    }

    #[getter]
    pub fn brackets_background(&self) -> Option<PyColor> {
        self.brackets_background.clone()
    }

    #[getter]
    pub fn brackets_options(&self) -> Option<PyUnderlineOption> {
        self.brackets_options.clone()
    }

    #[getter]
    pub fn tags_foreground(&self) -> Option<PyColor> {
        self.tags_foreground.clone()
    }

    #[getter]
    pub fn tags_options(&self) -> Option<PyUnderlineOption> {
        self.tags_options.clone()
    }

    #[getter]
    pub fn highlight(&self) -> Option<PyColor> {
        self.highlight.clone()
    }

    #[getter]
    pub fn find_highlight(&self) -> Option<PyColor> {
        self.find_highlight.clone()
    }

    #[getter]
    pub fn find_highlight_foreground(&self) -> Option<PyColor> {
        self.find_highlight_foreground.clone()
    }

    #[getter]
    pub fn selection_foreground(&self) -> Option<PyColor> {
        self.selection_foreground.clone()
    }

    #[getter]
    pub fn selection_border(&self) -> Option<PyColor> {
        self.selection_border.clone()
    }

    #[getter]
    pub fn inactive_selection(&self) -> Option<PyColor> {
        self.inactive_selection.clone()
    }

    #[getter]
    pub fn inactive_selection_foreground(&self) -> Option<PyColor> {
        self.inactive_selection_foreground.clone()
    }

    #[getter]
    pub fn guide(&self) -> Option<PyColor> {
        self.guide.clone()
    }

    #[getter]
    pub fn active_guide(&self) -> Option<PyColor> {
        self.active_guide.clone()
    }

    #[getter]
    pub fn stack_guide(&self) -> Option<PyColor> {
        self.stack_guide.clone()
    }

    #[getter]
    pub fn shadow(&self) -> Option<PyColor> {
        self.shadow.clone()
    }

    pub fn __repr__(&self) -> String {
        format!(
            "ThemeSettings(fg={:?}, bg={:?}, sel_bg={:?}, caret={:?})",
            self.foreground.as_ref().map(|c| c.to_hex()),
            self.background.as_ref().map(|c| c.to_hex()),
            self.selection_background.as_ref().map(|c| c.to_hex()),
            self.caret.as_ref().map(|c| c.to_hex())
        )
    }
}

// ============================================================================
// PyThemeItem
// ============================================================================

#[pyclass(name = "ThemeItem", skip_from_py_object)]
#[derive(Clone)]
pub struct PyThemeItem {
    scope: Arc<String>,
    foreground: Option<PyColor>,
    background: Option<PyColor>,
    font_style: u8,
    style_modifier: Arc<String>,
    #[allow(dead_code)]
    style: PyStyleModifier,
}

#[pymethods]
impl PyThemeItem {
    #[getter]
    pub fn scope(&self) -> String {
        (*self.scope).clone()
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
        (*self.style_modifier).clone()
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
            *self.scope, self.foreground.as_ref().map(|c| c.to_hex()), self.background.as_ref().map(|c| c.to_hex()), self.font_style)
    }
}

// ============================================================================
// PyTheme (read-only wrapper)
// ============================================================================

#[pyclass(name = "Theme", skip_from_py_object)]
#[derive(Clone)]
pub struct PyTheme {
    key: Arc<String>,
    name: Arc<String>,
    author: Arc<String>,
    settings: PyThemeSettings,
    scopes: Vec<PyThemeItem>,
}

#[pymethods]
impl PyTheme {
    #[getter]
    pub fn key(&self) -> String {
        (*self.key).clone()
    }

    #[getter]
    pub fn name(&self) -> String {
        (*self.name).clone()
    }

    #[getter]
    pub fn author(&self) -> String {
        (*self.author).clone()
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
        format!("Theme(name='{}', author='{}')", *self.name, *self.author)
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
                key: Arc::new(key.to_string()),
                name: Arc::new(t.name.clone().unwrap_or_default()),
                author: Arc::new(t.author.clone().unwrap_or_default()),
                settings: PyThemeSettings {
                    foreground: t.settings.foreground.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    background: t.settings.background.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    selection_background: t.settings.selection.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    gutter_foreground: t.settings.gutter_foreground.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    gutter_background: t.settings.gutter.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    // NEW fields
                    caret: t.settings.caret.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    line_highlight: t.settings.line_highlight.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    misspelling: t.settings.misspelling.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    minimap_border: t.settings.minimap_border.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    accent: t.settings.accent.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    popup_css: t.settings.popup_css.clone(),
                    phantom_css: t.settings.phantom_css.clone(),
                    bracket_contents_foreground: t.settings.bracket_contents_foreground.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    bracket_contents_options: to_underline_option(&t.settings.bracket_contents_options),
                    brackets_foreground: t.settings.brackets_foreground.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    brackets_background: t.settings.brackets_background.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    brackets_options: to_underline_option(&t.settings.brackets_options),
                    tags_foreground: t.settings.tags_foreground.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    tags_options: to_underline_option(&t.settings.tags_options),
                    highlight: t.settings.highlight.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    find_highlight: t.settings.find_highlight.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    find_highlight_foreground: t.settings.find_highlight_foreground.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    selection_foreground: t.settings.selection_foreground.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    selection_border: t.settings.selection_border.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    inactive_selection: t.settings.inactive_selection.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    inactive_selection_foreground: t.settings.inactive_selection_foreground.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    guide: t.settings.guide.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    active_guide: t.settings.active_guide.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    stack_guide: t.settings.stack_guide.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                    shadow: t.settings.shadow.as_ref().map(|c| PyColor {
                        r: c.r, g: c.g, b: c.b, a: c.a,
                    }),
                },
                scopes: t.scopes.iter().map(|s| {
                    let fm = PyStyleModifier {
                        foreground: s.style.foreground.as_ref().map(|c| PyColor {
                            r: c.r, g: c.g, b: c.b, a: c.a,
                        }),
                        background: s.style.background.as_ref().map(|c| PyColor {
                            r: c.r, g: c.g, b: c.b, a: c.a,
                        }),
                        font_style: s.style.font_style.map(|fs| PyFontStyle { bits: fs.bits() }),
                    };
                    // Build a real scope selector string from the ScopeSelectors,
                    // not a Debug dump — this is needed for CSS generation.
                    let scope_str = s.scope.selectors.iter().map(|sel| {
                        sel.path.scopes.iter().map(|sc| {
                            sc.build_string()
                        }).collect::<Vec<_>>().join(" ")
                    }).collect::<Vec<_>>().join(", ");
                    PyThemeItem {
                        scope: Arc::new(scope_str),
                        foreground: s.style.foreground.as_ref().map(|c| PyColor {
                            r: c.r, g: c.g, b: c.b, a: c.a,
                        }),
                        background: s.style.background.as_ref().map(|c| PyColor {
                            r: c.r, g: c.g, b: c.b, a: c.a,
                        }),
                        font_style: s.style.font_style.map_or(0, |fs| fs.bits()),
                        style_modifier: Arc::new(format!("{:?}", s.style)),
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
