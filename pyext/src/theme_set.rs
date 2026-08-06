//! Python bindings for syntect's theme and scope-selector types.

use pyo3::exceptions::{PyOSError, PyValueError};
use pyo3::prelude::*;
use std::str::FromStr;
use std::sync::Arc;

use syntect::highlighting::{
    Color, FontStyle, ScopeSelectors as SyntectScopeSelectors, StyleModifier,
    Theme as SyntectTheme, ThemeItem, ThemeSettings, ThemeSet as SyntectThemeSet,
    UnderlineOption,
};

use crate::errors;
use crate::style::{PyColor, PyFontStyle, PyStyleModifier};

fn to_color(color: &Option<PyColor>) -> Option<Color> {
    color.as_ref().map(|c| Color { r: c.r, g: c.g, b: c.b, a: c.a })
}

fn from_color(color: Option<&Color>) -> Option<PyColor> {
    color.map(|c| PyColor { r: c.r, g: c.g, b: c.b, a: c.a })
}

fn to_font_style(style: Option<&PyFontStyle>) -> Option<FontStyle> {
    style.map(|s| FontStyle::from_bits_truncate(s.bits))
}

fn from_style_modifier(style: &StyleModifier) -> PyStyleModifier {
    PyStyleModifier {
        foreground: from_color(style.foreground.as_ref()),
        background: from_color(style.background.as_ref()),
        font_style: style.font_style.map(|s| PyFontStyle { bits: s.bits() }),
    }
}

fn to_style_modifier(style: &PyStyleModifier) -> StyleModifier {
    StyleModifier {
        foreground: to_color(&style.foreground),
        background: to_color(&style.background),
        font_style: to_font_style(style.font_style.as_ref()),
    }
}

fn from_underline_option(value: &Option<UnderlineOption>) -> Option<PyUnderlineOption> {
    value.as_ref().map(|value| PyUnderlineOption {
        kind: match value {
            UnderlineOption::None => "none",
            UnderlineOption::Underline => "underline",
            UnderlineOption::StippledUnderline => "stippled_underline",
            UnderlineOption::SquigglyUnderline => "squiggly_underline",
        }.to_string(),
    })
}

fn to_underline_option(value: &Option<PyUnderlineOption>) -> Option<UnderlineOption> {
    value.as_ref().map(|value| match value.kind.as_str() {
        "underline" => UnderlineOption::Underline,
        "stippled_underline" => UnderlineOption::StippledUnderline,
        "squiggly_underline" => UnderlineOption::SquigglyUnderline,
        _ => UnderlineOption::None,
    })
}

fn scope_stack_to_string(stack: &syntect::parsing::ScopeStack) -> String {
    stack.as_slice()
        .iter()
        .map(|scope| scope.build_string())
        .collect::<Vec<_>>()
        .join(" ")
}

fn scope_selectors_to_string(selectors: &SyntectScopeSelectors) -> String {
    selectors.selectors.iter().map(|selector| {
        let mut result = scope_stack_to_string(&selector.path);
        for excluded in &selector.excludes {
            if !result.is_empty() {
                result.push_str(" - ");
            } else {
                result.push_str("- ");
            }
            result.push_str(&scope_stack_to_string(excluded));
        }
        result
    }).collect::<Vec<_>>().join(", ")
}

// ============================================================================
// ScopeSelectors
// ============================================================================

/// A TextMate scope selector set.
///
/// Unlike the legacy `ThemeItem.scope` string, this retains comma/pipe unions,
/// selector paths, and exclusions as parsed by syntect.
#[pyclass(name = "ScopeSelectors", from_py_object)]
#[derive(Clone)]
pub struct PyScopeSelectors {
    pub(crate) inner: SyntectScopeSelectors,
}

#[pymethods]
impl PyScopeSelectors {
    #[staticmethod]
    pub fn from_string(value: &str) -> PyResult<Self> {
        SyntectScopeSelectors::from_str(value)
            .map(|inner| PyScopeSelectors { inner })
            .map_err(|e| PyErr::new::<PyValueError, _>(format!("Invalid scope selectors: {}", e)))
    }

    pub fn to_string(&self) -> String {
        scope_selectors_to_string(&self.inner)
    }

    pub fn __repr__(&self) -> String {
        format!("ScopeSelectors('{}')", self.to_string().replace('\'', "\\'"))
    }
}

// ============================================================================
// UnderlineOption
// ============================================================================

#[pyclass(name = "UnderlineOption", from_py_object)]
#[derive(Clone)]
pub struct PyUnderlineOption {
    pub(crate) kind: String,
}

#[pymethods]
impl PyUnderlineOption {
    #[staticmethod]
    pub fn none_() -> Option<Self> { None }
    #[staticmethod]
    pub fn underline() -> Option<Self> {
        Some(Self { kind: "underline".to_string() })
    }
    #[staticmethod]
    pub fn stippled_underline() -> Option<Self> {
        Some(Self { kind: "stippled_underline".to_string() })
    }
    #[staticmethod]
    pub fn squiggly_underline() -> Option<Self> {
        Some(Self { kind: "squiggly_underline".to_string() })
    }
    pub fn __repr__(&self) -> String { format!("UnderlineOption({})", self.kind) }
}

// ============================================================================
// ThemeSettings
// ============================================================================

#[pyclass(name = "ThemeSettings", from_py_object)]
#[derive(Clone, Default)]
pub struct PyThemeSettings {
    foreground: Option<PyColor>,
    background: Option<PyColor>,
    selection_background: Option<PyColor>,
    gutter_foreground: Option<PyColor>,
    gutter_background: Option<PyColor>,
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

// Keep explicit accessors instead of relying on macro identifier concatenation,
// which is not stable without an additional proc-macro dependency.
#[pymethods]
impl PyThemeSettings {
    #[new]
    pub fn new() -> Self { Self::default() }

    #[getter] pub fn foreground(&self) -> Option<PyColor> { self.foreground.clone() }
    #[setter] pub fn set_foreground(&mut self, value: Option<PyColor>) { self.foreground = value; }
    #[getter] pub fn background(&self) -> Option<PyColor> { self.background.clone() }
    #[setter] pub fn set_background(&mut self, value: Option<PyColor>) { self.background = value; }
    #[getter] pub fn selection_background(&self) -> Option<PyColor> { self.selection_background.clone() }
    #[setter] pub fn set_selection_background(&mut self, value: Option<PyColor>) { self.selection_background = value; }
    #[getter] pub fn selection(&self) -> Option<PyColor> { self.selection_background.clone() }
    #[setter] pub fn set_selection(&mut self, value: Option<PyColor>) { self.selection_background = value; }
    #[getter] pub fn gutter_foreground(&self) -> Option<PyColor> { self.gutter_foreground.clone() }
    #[setter] pub fn set_gutter_foreground(&mut self, value: Option<PyColor>) { self.gutter_foreground = value; }
    #[getter] pub fn gutter_background(&self) -> Option<PyColor> { self.gutter_background.clone() }
    #[setter] pub fn set_gutter_background(&mut self, value: Option<PyColor>) { self.gutter_background = value; }
    #[getter] pub fn gutter(&self) -> Option<PyColor> { self.gutter_background.clone() }
    #[setter] pub fn set_gutter(&mut self, value: Option<PyColor>) { self.gutter_background = value; }
    #[getter] pub fn caret(&self) -> Option<PyColor> { self.caret.clone() }
    #[setter] pub fn set_caret(&mut self, value: Option<PyColor>) { self.caret = value; }
    #[getter] pub fn line_highlight(&self) -> Option<PyColor> { self.line_highlight.clone() }
    #[setter] pub fn set_line_highlight(&mut self, value: Option<PyColor>) { self.line_highlight = value; }
    #[getter] pub fn misspelling(&self) -> Option<PyColor> { self.misspelling.clone() }
    #[setter] pub fn set_misspelling(&mut self, value: Option<PyColor>) { self.misspelling = value; }
    #[getter] pub fn minimap_border(&self) -> Option<PyColor> { self.minimap_border.clone() }
    #[setter] pub fn set_minimap_border(&mut self, value: Option<PyColor>) { self.minimap_border = value; }
    #[getter] pub fn accent(&self) -> Option<PyColor> { self.accent.clone() }
    #[setter] pub fn set_accent(&mut self, value: Option<PyColor>) { self.accent = value; }
    #[getter] pub fn popup_css(&self) -> Option<String> { self.popup_css.clone() }
    #[setter] pub fn set_popup_css(&mut self, value: Option<String>) { self.popup_css = value; }
    #[getter] pub fn phantom_css(&self) -> Option<String> { self.phantom_css.clone() }
    #[setter] pub fn set_phantom_css(&mut self, value: Option<String>) { self.phantom_css = value; }
    #[getter] pub fn bracket_contents_foreground(&self) -> Option<PyColor> { self.bracket_contents_foreground.clone() }
    #[setter] pub fn set_bracket_contents_foreground(&mut self, value: Option<PyColor>) { self.bracket_contents_foreground = value; }
    #[getter] pub fn bracket_contents_options(&self) -> Option<PyUnderlineOption> { self.bracket_contents_options.clone() }
    #[getter] pub fn brackets_foreground(&self) -> Option<PyColor> { self.brackets_foreground.clone() }
    #[setter] pub fn set_brackets_foreground(&mut self, value: Option<PyColor>) { self.brackets_foreground = value; }
    #[getter] pub fn brackets_background(&self) -> Option<PyColor> { self.brackets_background.clone() }
    #[setter] pub fn set_brackets_background(&mut self, value: Option<PyColor>) { self.brackets_background = value; }
    #[getter] pub fn brackets_options(&self) -> Option<PyUnderlineOption> { self.brackets_options.clone() }
    #[getter] pub fn tags_foreground(&self) -> Option<PyColor> { self.tags_foreground.clone() }
    #[setter] pub fn set_tags_foreground(&mut self, value: Option<PyColor>) { self.tags_foreground = value; }
    #[getter] pub fn tags_options(&self) -> Option<PyUnderlineOption> { self.tags_options.clone() }
    #[getter] pub fn highlight(&self) -> Option<PyColor> { self.highlight.clone() }
    #[setter] pub fn set_highlight(&mut self, value: Option<PyColor>) { self.highlight = value; }
    #[getter] pub fn find_highlight(&self) -> Option<PyColor> { self.find_highlight.clone() }
    #[setter] pub fn set_find_highlight(&mut self, value: Option<PyColor>) { self.find_highlight = value; }
    #[getter] pub fn find_highlight_foreground(&self) -> Option<PyColor> { self.find_highlight_foreground.clone() }
    #[setter] pub fn set_find_highlight_foreground(&mut self, value: Option<PyColor>) { self.find_highlight_foreground = value; }
    #[getter] pub fn selection_foreground(&self) -> Option<PyColor> { self.selection_foreground.clone() }
    #[setter] pub fn set_selection_foreground(&mut self, value: Option<PyColor>) { self.selection_foreground = value; }
    #[getter] pub fn selection_border(&self) -> Option<PyColor> { self.selection_border.clone() }
    #[setter] pub fn set_selection_border(&mut self, value: Option<PyColor>) { self.selection_border = value; }
    #[getter] pub fn inactive_selection(&self) -> Option<PyColor> { self.inactive_selection.clone() }
    #[setter] pub fn set_inactive_selection(&mut self, value: Option<PyColor>) { self.inactive_selection = value; }
    #[getter] pub fn inactive_selection_foreground(&self) -> Option<PyColor> { self.inactive_selection_foreground.clone() }
    #[setter] pub fn set_inactive_selection_foreground(&mut self, value: Option<PyColor>) { self.inactive_selection_foreground = value; }
    #[getter] pub fn guide(&self) -> Option<PyColor> { self.guide.clone() }
    #[setter] pub fn set_guide(&mut self, value: Option<PyColor>) { self.guide = value; }
    #[getter] pub fn active_guide(&self) -> Option<PyColor> { self.active_guide.clone() }
    #[setter] pub fn set_active_guide(&mut self, value: Option<PyColor>) { self.active_guide = value; }
    #[getter] pub fn stack_guide(&self) -> Option<PyColor> { self.stack_guide.clone() }
    #[setter] pub fn set_stack_guide(&mut self, value: Option<PyColor>) { self.stack_guide = value; }
    #[getter] pub fn shadow(&self) -> Option<PyColor> { self.shadow.clone() }
    #[setter] pub fn set_shadow(&mut self, value: Option<PyColor>) { self.shadow = value; }

    pub fn __repr__(&self) -> String {
        format!("ThemeSettings(fg={:?}, bg={:?}, caret={:?})",
            self.foreground.as_ref().map(|c| c.to_hex()),
            self.background.as_ref().map(|c| c.to_hex()),
            self.caret.as_ref().map(|c| c.to_hex()))
    }
}

fn py_settings_from_syntect(settings: &ThemeSettings) -> PyThemeSettings {
    PyThemeSettings {
        foreground: from_color(settings.foreground.as_ref()),
        background: from_color(settings.background.as_ref()),
        selection_background: from_color(settings.selection.as_ref()),
        gutter_foreground: from_color(settings.gutter_foreground.as_ref()),
        gutter_background: from_color(settings.gutter.as_ref()),
        caret: from_color(settings.caret.as_ref()),
        line_highlight: from_color(settings.line_highlight.as_ref()),
        misspelling: from_color(settings.misspelling.as_ref()),
        minimap_border: from_color(settings.minimap_border.as_ref()),
        accent: from_color(settings.accent.as_ref()),
        popup_css: settings.popup_css.clone(),
        phantom_css: settings.phantom_css.clone(),
        bracket_contents_foreground: from_color(settings.bracket_contents_foreground.as_ref()),
        bracket_contents_options: from_underline_option(&settings.bracket_contents_options),
        brackets_foreground: from_color(settings.brackets_foreground.as_ref()),
        brackets_background: from_color(settings.brackets_background.as_ref()),
        brackets_options: from_underline_option(&settings.brackets_options),
        tags_foreground: from_color(settings.tags_foreground.as_ref()),
        tags_options: from_underline_option(&settings.tags_options),
        highlight: from_color(settings.highlight.as_ref()),
        find_highlight: from_color(settings.find_highlight.as_ref()),
        find_highlight_foreground: from_color(settings.find_highlight_foreground.as_ref()),
        selection_foreground: from_color(settings.selection_foreground.as_ref()),
        selection_border: from_color(settings.selection_border.as_ref()),
        inactive_selection: from_color(settings.inactive_selection.as_ref()),
        inactive_selection_foreground: from_color(settings.inactive_selection_foreground.as_ref()),
        guide: from_color(settings.guide.as_ref()),
        active_guide: from_color(settings.active_guide.as_ref()),
        stack_guide: from_color(settings.stack_guide.as_ref()),
        shadow: from_color(settings.shadow.as_ref()),
    }
}

// ============================================================================
// ThemeItem and Theme
// ============================================================================

#[pyclass(name = "ThemeItem", from_py_object)]
#[derive(Clone)]
pub struct PyThemeItem {
    scope: Arc<String>,
    scope_selectors: PyScopeSelectors,
    style: PyStyleModifier,
}

#[pymethods]
impl PyThemeItem {
    #[new]
    pub fn new(scope: &PyScopeSelectors, style: &PyStyleModifier) -> Self {
        Self {
            scope: Arc::new(scope.to_string()),
            scope_selectors: scope.clone(),
            style: style.clone(),
        }
    }

    #[getter] pub fn scope(&self) -> String { (*self.scope).clone() }
    #[getter] pub fn scope_selectors(&self) -> PyScopeSelectors { self.scope_selectors.clone() }
    #[getter] pub fn foreground(&self) -> Option<PyColor> { self.style.foreground.clone() }
    #[getter] pub fn background(&self) -> Option<PyColor> { self.style.background.clone() }
    #[getter] pub fn font_style(&self) -> u8 { self.style.font_style.as_ref().map_or(0, |s| s.bits) }
    #[getter] pub fn style_modifier(&self) -> PyStyleModifier { self.style.clone() }
    #[getter] pub fn style(&self) -> PyStyleModifier { self.style.clone() }

    pub fn __repr__(&self) -> String {
        format!("ThemeItem(scope='{}', font={})", *self.scope, self.font_style())
    }
}

fn py_item_from_syntect(item: &ThemeItem) -> PyThemeItem {
    let selectors = PyScopeSelectors { inner: item.scope.clone() };
    PyThemeItem {
        scope: Arc::new(scope_selectors_to_string(&item.scope)),
        scope_selectors: selectors,
        style: from_style_modifier(&item.style),
    }
}

#[pyclass(name = "Theme", from_py_object)]
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
    #[new]
    #[pyo3(signature = (name=None, author=None, settings=None, scopes=None))]
    pub fn new(
        name: Option<String>,
        author: Option<String>,
        settings: Option<PyThemeSettings>,
        scopes: Option<Vec<PyThemeItem>>,
    ) -> Self {
        Self {
            key: Arc::new(String::new()),
            name: Arc::new(name.unwrap_or_default()),
            author: Arc::new(author.unwrap_or_default()),
            settings: settings.unwrap_or_default(),
            scopes: scopes.unwrap_or_default(),
        }
    }

    #[getter] pub fn key(&self) -> String { (*self.key).clone() }
    #[getter] pub fn name(&self) -> String { (*self.name).clone() }
    #[getter] pub fn author(&self) -> String { (*self.author).clone() }
    #[getter] pub fn settings(&self) -> PyThemeSettings { self.settings.clone() }
    #[getter] pub fn scopes(&self) -> Vec<PyThemeItem> { self.scopes.clone() }

    pub fn __repr__(&self) -> String {
        format!("Theme(name='{}', author='{}')", *self.name, *self.author)
    }
}

impl PyThemeSettings {
    pub(crate) fn to_syntect(&self) -> ThemeSettings {
        ThemeSettings {
            foreground: to_color(&self.foreground),
            background: to_color(&self.background),
            caret: to_color(&self.caret),
            line_highlight: to_color(&self.line_highlight),
            misspelling: to_color(&self.misspelling),
            minimap_border: to_color(&self.minimap_border),
            accent: to_color(&self.accent),
            popup_css: self.popup_css.clone(),
            phantom_css: self.phantom_css.clone(),
            bracket_contents_foreground: to_color(&self.bracket_contents_foreground),
            bracket_contents_options: to_underline_option(&self.bracket_contents_options),
            brackets_foreground: to_color(&self.brackets_foreground),
            brackets_background: to_color(&self.brackets_background),
            brackets_options: to_underline_option(&self.brackets_options),
            tags_foreground: to_color(&self.tags_foreground),
            tags_options: to_underline_option(&self.tags_options),
            highlight: to_color(&self.highlight),
            find_highlight: to_color(&self.find_highlight),
            find_highlight_foreground: to_color(&self.find_highlight_foreground),
            gutter: to_color(&self.gutter_background),
            gutter_foreground: to_color(&self.gutter_foreground),
            selection: to_color(&self.selection_background),
            selection_foreground: to_color(&self.selection_foreground),
            selection_border: to_color(&self.selection_border),
            inactive_selection: to_color(&self.inactive_selection),
            inactive_selection_foreground: to_color(&self.inactive_selection_foreground),
            guide: to_color(&self.guide),
            active_guide: to_color(&self.active_guide),
            stack_guide: to_color(&self.stack_guide),
            shadow: to_color(&self.shadow),
        }
    }
}

impl PyThemeItem {
    pub(crate) fn to_syntect(&self) -> ThemeItem {
        ThemeItem { scope: self.scope_selectors.inner.clone(), style: to_style_modifier(&self.style) }
    }
}

impl PyTheme {
    pub(crate) fn to_syntect(&self) -> SyntectTheme {
        SyntectTheme {
            name: (!self.name.is_empty()).then(|| (*self.name).clone()),
            author: (!self.author.is_empty()).then(|| (*self.author).clone()),
            settings: self.settings.to_syntect(),
            scopes: self.scopes.iter().map(PyThemeItem::to_syntect).collect(),
        }
    }

    pub(crate) fn from_syntect(key: &str, theme: &SyntectTheme) -> Self {
        Self {
            key: Arc::new(key.to_string()),
            name: Arc::new(theme.name.clone().unwrap_or_default()),
            author: Arc::new(theme.author.clone().unwrap_or_default()),
            settings: py_settings_from_syntect(&theme.settings),
            scopes: theme.scopes.iter().map(py_item_from_syntect).collect(),
        }
    }
}

// ============================================================================
// ThemeSet
// ============================================================================

#[pyclass(name = "ThemeSet", skip_from_py_object)]
pub struct PyThemeSet {
    pub inner: SyntectThemeSet,
}

#[pymethods]
impl PyThemeSet {
    #[new]
    pub fn new() -> Self { Self { inner: SyntectThemeSet::new() } }

    #[staticmethod]
    pub fn load_defaults() -> Self { Self { inner: SyntectThemeSet::load_defaults() } }

    pub fn add_from_folder(&mut self, path: &str) -> PyResult<Vec<String>> {
        let loaded = SyntectThemeSet::load_from_folder(path)
            .map_err(|e| PyErr::new::<PyOSError, _>(errors::loading_error_to_string(&e)))?;
        let names = loaded.themes.keys().cloned().collect::<Vec<_>>();
        self.inner.themes.extend(loaded.themes);
        Ok(names)
    }

    #[staticmethod]
    pub fn load_theme_from_reader(content: &str) -> PyResult<PyTheme> {
        let mut reader = std::io::Cursor::new(content.as_bytes());
        SyntectThemeSet::load_from_reader(&mut reader)
            .map(|theme| PyTheme::from_syntect("", &theme))
            .map_err(|e| PyErr::new::<PyValueError, _>(errors::loading_error_to_string(&e)))
    }

    pub fn add_theme(&mut self, name: &str, theme: &PyTheme) {
        self.inner.themes.insert(name.to_string(), theme.to_syntect());
    }

    pub fn add_theme_from_reader(&mut self, name: &str, content: &str) -> PyResult<()> {
        let theme = Self::load_theme_from_reader(content)?;
        self.add_theme(name, &theme);
        Ok(())
    }

    #[staticmethod]
    pub fn builder() -> PyResult<PyThemeSet> { Ok(Self::new()) }

    #[pyo3(signature = (key, fallback=None))]
    pub fn get_theme(&self, key: &str, fallback: Option<&str>) -> Option<PyTheme> {
        let resolved_key = if self.inner.themes.contains_key(key) {
            key
        } else {
            fallback.filter(|name| self.inner.themes.contains_key(*name))?
        };
        self.inner.themes.get(resolved_key).map(|theme| PyTheme::from_syntect(resolved_key, theme))
    }

    pub fn theme_names(&self) -> Vec<String> { self.inner.themes.keys().cloned().collect() }

    #[staticmethod]
    pub fn from_dump(path: &str) -> PyResult<PyThemeSet> {
        match syntect::dumps::from_dump_file::<SyntectThemeSet, &str>(path) {
            Ok(ts) => Ok(Self { inner: ts }),
            Err(e) => Err(PyErr::new::<PyOSError, _>(format!("Failed to load theme dump: {}", e))),
        }
    }

    pub fn to_dump(&self, path: &str) -> PyResult<()> {
        syntect::dumps::dump_to_file(&self.inner, path)
            .map_err(|e| PyErr::new::<PyOSError, _>(format!("Failed to save theme dump: {}", e)))
    }

    pub fn __repr__(&self) -> String { format!("ThemeSet(themes={})", self.inner.themes.len()) }
}
