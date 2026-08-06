//! VS Code JSON/JSONC theme conversion.
//!
//! VS Code themes are not plist themes: their editor colors and token-color
//! rules need to be mapped into syntect's `ThemeSettings` and
//! `ScopeSelectors` structures before they can be used by the highlighter.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use serde::Deserialize;
use std::collections::HashMap;
use std::str::FromStr;
use std::sync::{Mutex, OnceLock};

use syntect::highlighting::{
    Color, FontStyle, ScopeSelectors, StyleModifier, Theme as SyntectTheme,
    ThemeItem, ThemeSet as SyntectThemeSet, ThemeSettings,
};
use syntect::parsing::SyntaxSet as SyntectSyntaxSet;

use crate::errors;
use crate::theme_set::PyTheme;

#[derive(Debug, Deserialize)]
struct VscodeTokenColor {
    scope: Option<VscodeScope>,
    #[serde(default)]
    settings: VscodeTokenSettings,
}

#[derive(Debug, Deserialize)]
#[serde(untagged)]
enum VscodeScope {
    Single(String),
    Multiple(Vec<String>),
}

impl VscodeScope {
    fn to_scope_selectors(&self) -> Result<ScopeSelectors, String> {
        let value = match self {
            Self::Single(value) => value.clone(),
            Self::Multiple(values) => values.join(","),
        };
        ScopeSelectors::from_str(&value).map_err(|e| e.to_string())
    }
}

#[derive(Debug, Default, Deserialize)]
struct VscodeTokenSettings {
    foreground: Option<String>,
    background: Option<String>,
    #[serde(rename = "fontStyle")]
    font_style: Option<String>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
struct VscodeTheme {
    name: Option<String>,
    author: Option<String>,
    #[serde(rename = "type")]
    _theme_type: Option<String>,
    #[serde(default)]
    colors: HashMap<String, Option<String>>,
    #[serde(default)]
    token_colors: Vec<VscodeTokenColor>,
}

fn hex_to_color(value: &str) -> Option<Color> {
    let value = value.trim();
    if value.starts_with('#') && value.len() == 7 {
        return Some(Color {
            r: u8::from_str_radix(&value[1..3], 16).ok()?,
            g: u8::from_str_radix(&value[3..5], 16).ok()?,
            b: u8::from_str_radix(&value[5..7], 16).ok()?,
            a: 255,
        });
    }
    if value.starts_with("rgb(") && value.ends_with(')') {
        let parts = value[4..value.len() - 1]
            .split(',')
            .map(str::trim)
            .collect::<Vec<_>>();
        if parts.len() == 3 {
            return Some(Color {
                r: parts[0].parse().ok()?,
                g: parts[1].parse().ok()?,
                b: parts[2].parse().ok()?,
                a: 255,
            });
        }
    }
    None
}

fn named_color(value: &str) -> Option<Color> {
    let (r, g, b) = match value.trim().to_ascii_lowercase().as_str() {
        "black" => (0, 0, 0),
        "white" => (255, 255, 255),
        "red" => (255, 0, 0),
        "green" => (0, 128, 0),
        "blue" => (0, 0, 255),
        "yellow" => (255, 255, 0),
        "cyan" | "aqua" => (0, 255, 255),
        "magenta" | "fuchsia" => (255, 0, 255),
        "orange" => (255, 165, 0),
        "pink" => (255, 192, 192),
        "purple" => (128, 0, 128),
        "brown" => (165, 42, 42),
        "gray" | "grey" => (128, 128, 128),
        "silver" => (192, 192, 192),
        "teal" => (0, 128, 128),
        "lime" => (0, 255, 0),
        "olive" => (128, 128, 0),
        "indigo" => (75, 75, 238),
        "violet" => (238, 130, 238),
        "coral" => (255, 127, 80),
        "salmon" => (250, 128, 128),
        "khaki" => (188, 143, 78),
        "tan" => (210, 180, 140),
        "beige" => (245, 245, 220),
        "cream" => (255, 253, 215),
        "ivory" => (255, 255, 240),
        "linen" => (250, 240, 230),
        "lace" => (255, 250, 240),
        "snow" => (255, 250, 250),
        "mint" => (189, 245, 239),
        "sage" => (165, 188, 165),
        "gold" => (255, 215, 0),
        "bronze" => (205, 127, 53),
        "copper" => (184, 115, 67),
        "brass" => (184, 152, 32),
        _ => return None,
    };
    Some(Color { r, g, b, a: 255 })
}

fn resolve_color(value: &str) -> Option<Color> {
    hex_to_color(value).or_else(|| named_color(value))
}

fn parse_font_style(value: &str) -> Option<FontStyle> {
    let mut bits = 0u8;
    for part in value.split(|c: char| c == ',' || c.is_whitespace()) {
        match part.trim().to_ascii_lowercase().as_str() {
            "bold" => bits |= 1,
            "underline" | "underlined" => bits |= 2,
            "italic" => bits |= 4,
            _ => {}
        }
    }
    (bits != 0).then(|| FontStyle::from_bits_truncate(bits))
}

fn convert_theme(theme: &VscodeTheme) -> Result<SyntectTheme, String> {
    let mut settings = ThemeSettings::default();
    for (key, value) in &theme.colors {
        let Some(value) = value else { continue };
        let color = resolve_color(value);
        match key.as_str() {
            "editor.background" => settings.background = color,
            "editor.foreground" => {
                settings.foreground = color;
                settings.caret = color;
            }
            "foreground" => settings.foreground = color,
            "editorCursor.background" => settings.caret = color,
            "editor.lineHighlightBackground" => settings.line_highlight = color,
            "list.highlightForeground" => {
                settings.find_highlight_foreground = color;
                settings.accent = color;
            }
            "editorGutter.background" => settings.gutter = color,
            "editorLineNumber.foreground" => settings.gutter_foreground = color,
            "editor.selectionBackground" => settings.selection = color,
            "list.inactiveSelectionBackground" => settings.inactive_selection = color,
            "list.inactiveSelectionForeground" => settings.inactive_selection_foreground = color,
            "editor.findMatchBackground" | "peekViewEditor.matchHighlightBorder" => {
                settings.highlight = color;
                settings.find_highlight = color;
            }
            "editorIndentGuide.background" => settings.guide = color,
            "breadcrumb.activeSelectionForeground" => settings.active_guide = color,
            "breadcrumb.foreground" => settings.stack_guide = color,
            "selection.background" => {
                settings.tags_foreground = color;
                settings.brackets_foreground = color;
            }
            "widget.shadow" | "scrollbar.shadow" => settings.shadow = color,
            _ => {}
        }
    }

    let mut scopes = Vec::with_capacity(theme.token_colors.len());
    for token in &theme.token_colors {
        let scope = match &token.scope {
            Some(scope) => scope.to_scope_selectors()?,
            None => ScopeSelectors::from_str("*").map_err(|e| e.to_string())?,
        };
        scopes.push(ThemeItem {
            scope,
            style: StyleModifier {
                foreground: token.settings.foreground.as_deref().and_then(resolve_color),
                background: token.settings.background.as_deref().and_then(resolve_color),
                font_style: token.settings.font_style.as_deref().and_then(parse_font_style),
            },
        });
    }

    Ok(SyntectTheme {
        name: theme.name.clone(),
        author: theme.author.clone(),
        settings,
        scopes,
    })
}

fn parse_theme(content: &str) -> Result<SyntectTheme, String> {
    let value = jsonc_parser::parse_to_serde_value(
        content,
        &jsonc_parser::ParseOptions::default(),
    ).map_err(|e| format!("JSONC parse error: {}", e))?;
    let theme: VscodeTheme = serde_json::from_value(value)
        .map_err(|e| format!("Theme parse error: {}", e))?;
    convert_theme(&theme)
}

/// Return whether `content` looks like a VS Code JSON/JSONC theme.
#[pyfunction]
pub fn is_vscode_theme(content: &str) -> bool {
    let trimmed = content.trim_start();
    trimmed.starts_with('{') && trimmed.contains("\"tokenColors\"")
}

/// Return whether `content` looks like a plist `.tmTheme`.
#[pyfunction]
pub fn is_plist_theme(content: &str) -> bool {
    let trimmed = content.trim_start_matches('\u{feff}').trim_start();
    trimmed.starts_with("<?xml")
        || trimmed.starts_with("<plist")
        // Some bundled themes place copyright comments before the XML header.
        || (trimmed.contains("<plist") && trimmed.contains("</plist>"))
}

/// Parse a VS Code JSON/JSONC theme into a syntect Theme.
#[pyfunction]
pub fn parse_vscode_theme(content: &str) -> PyResult<PyTheme> {
    parse_theme(content)
        .map(|theme| PyTheme::from_syntect("", &theme))
        .map_err(|e| PyErr::new::<PyValueError, _>(e))
}

fn global_themes() -> &'static Mutex<SyntectThemeSet> {
    static THEMES: OnceLock<Mutex<SyntectThemeSet>> = OnceLock::new();
    THEMES.get_or_init(|| Mutex::new(SyntectThemeSet::load_defaults()))
}

fn theme_from_content(content: &str) -> Result<SyntectTheme, String> {
    if is_vscode_theme(content) {
        parse_theme(content)
    } else if is_plist_theme(content) {
        let mut reader = std::io::Cursor::new(content.as_bytes());
        SyntectThemeSet::load_from_reader(&mut reader)
            .map_err(|e| errors::loading_error_to_string(&e))
    } else {
        Err("Theme content is neither a VS Code JSON/JSONC theme nor a plist theme".to_string())
    }
}

/// Load bundled themes during module initialization.
///
/// Bundled files are optional, so invalid or unavailable files are ignored in
/// the same way mordant treats a bad user theme: one bad theme must not make
/// importing the package fail. The explicit public folder loader below remains
/// strict and reports errors to callers.
pub(crate) fn load_bundled_themes(path: &std::path::Path) {
    let Ok(entries) = std::fs::read_dir(path) else { return };
    let mut paths = entries
        .filter_map(|entry| entry.ok().map(|entry| entry.path()))
        .filter(|path| {
            path.is_file() && path.extension().is_some_and(|extension| {
                extension.eq_ignore_ascii_case("tmTheme") || extension.eq_ignore_ascii_case("json")
            })
        })
        .collect::<Vec<_>>();
    paths.sort();

    let Ok(mut themes) = global_themes().lock() else { return };
    for path in paths {
        let Some(name) = path.file_stem().and_then(|stem| stem.to_str()) else { continue };
        let Ok(content) = std::fs::read_to_string(&path) else { continue };
        let Ok(theme) = theme_from_content(&content) else { continue };
        themes.themes.insert(name.to_string(), theme);
    }
}

/// Register a plist or VS Code theme in the process-wide convenience set.
#[pyfunction]
pub fn add_custom_theme(name: &str, content: &str) -> PyResult<()> {
    let theme = theme_from_content(content)
        .map_err(|e| PyErr::new::<PyValueError, _>(e))?;

    global_themes().lock()
        .map_err(|_| PyErr::new::<PyValueError, _>("Global theme set is poisoned"))?
        .themes.insert(name.to_string(), theme);
    Ok(())
}

/// Load `.tmTheme` and VS Code `.json` files from a directory.
///
/// Files are processed in lexical order. The file stem becomes the registry
/// key, matching mordant's embedded-theme loader. Invalid files return an
/// error with the path so callers do not silently get a partial theme set.
#[pyfunction]
pub fn load_themes_from_folder(path: &str) -> PyResult<Vec<String>> {
    let mut paths = std::fs::read_dir(path)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyOSError, _>(format!("{}: {}", path, e)))?
        .filter_map(|entry| entry.ok().map(|entry| entry.path()))
        .filter(|path| {
            path.is_file() && path.extension().is_some_and(|extension| {
                extension.eq_ignore_ascii_case("tmTheme") || extension.eq_ignore_ascii_case("json")
            })
        })
        .collect::<Vec<_>>();
    paths.sort();

    let mut loaded = Vec::with_capacity(paths.len());
    for path in paths {
        let name = path.file_stem()
            .and_then(|stem| stem.to_str())
            .ok_or_else(|| PyErr::new::<PyValueError, _>(format!("Invalid theme filename: {}", path.display())))?;
        let content = std::fs::read_to_string(&path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyOSError, _>(format!("{}: {}", path.display(), e)))?;
        add_custom_theme(name, &content).map_err(|e| {
            PyErr::new::<PyValueError, _>(format!("{}: {}", path.display(), e))
        })?;
        loaded.push(name.to_string());
    }
    Ok(loaded)
}

/// List names in the process-wide convenience theme set.
#[pyfunction]
pub fn list_themes() -> PyResult<Vec<String>> {
    Ok(global_themes().lock()
        .map_err(|_| PyErr::new::<PyValueError, _>("Global theme set is poisoned"))?
        .themes.keys().cloned().collect())
}

/// List names in syntect's default syntax set.
#[pyfunction]
pub fn list_syntaxes() -> Vec<String> {
    SyntectSyntaxSet::load_defaults_newlines()
        .syntaxes()
        .iter()
        .map(|syntax| syntax.name.clone())
        .collect()
}
