//! Python bindings for syntect's .tmPreferences metadata loading.
//!
//! Exposes Metadata, MetadataSet, and MetadataItem types for accessing
//! Sublime Text preferences loaded from .tmPreferences files.

use pyo3::prelude::*;

// ============================================================================
// PyMetadataItem — Items loaded from .tmPreferences
// ============================================================================

/// Items loaded from a `.tmPreferences` file for a particular scope.
///
/// These include indent rules, comment patterns, and other editor preferences.
///
/// Example:
/// ```python
/// item = metadata.items
/// print(item.line_comment)  # "//" for C-style languages
/// print(item.indent_parens)  # True
/// ```
#[pyclass(name = "MetadataItem", skip_from_py_object)]
#[derive(Clone, Debug)]
pub struct PyMetadataItem {
    pub increase_indent_pattern: Option<String>,
    pub decrease_indent_pattern: Option<String>,
    pub bracket_indent_next_line_pattern: Option<String>,
    pub disable_indent_next_line_pattern: Option<String>,
    pub unindented_line_pattern: Option<String>,
    pub indent_parens: Option<bool>,
    pub shell_variables: Vec<(String, String)>,
    pub line_comment: Option<String>,
    pub block_comment: Option<(String, String)>,
}

#[pymethods]
impl PyMetadataItem {
    #[getter]
    pub fn increase_indent_pattern(&self) -> Option<String> {
        self.increase_indent_pattern.clone()
    }

    #[getter]
    pub fn decrease_indent_pattern(&self) -> Option<String> {
        self.decrease_indent_pattern.clone()
    }

    #[getter]
    pub fn bracket_indent_next_line_pattern(&self) -> Option<String> {
        self.bracket_indent_next_line_pattern.clone()
    }

    #[getter]
    pub fn disable_indent_next_line_pattern(&self) -> Option<String> {
        self.disable_indent_next_line_pattern.clone()
    }

    #[getter]
    pub fn unindented_line_pattern(&self) -> Option<String> {
        self.unindented_line_pattern.clone()
    }

    #[getter]
    pub fn indent_parens(&self) -> Option<bool> {
        self.indent_parens
    }

    #[getter]
    pub fn shell_variables(&self) -> Vec<(String, String)> {
        self.shell_variables.clone()
    }

    #[getter]
    pub fn line_comment(&self) -> Option<String> {
        self.line_comment.clone()
    }

    #[getter]
    pub fn block_comment(&self) -> Option<(String, String)> {
        self.block_comment.clone()
    }

    pub fn __repr__(&self) -> String {
        format!(
            "MetadataItem(line_comment={:?}, indent_parens={:?})",
            self.line_comment, self.indent_parens
        )
    }
}

// ============================================================================
// PyMetadataSet — Metadata for a scope selector
// ============================================================================

/// Metadata for a particular scope selector.
///
/// Each metadata set applies to a specific scope pattern and contains
/// indent rules, comment patterns, and other editor preferences.
///
/// Example:
/// ```python
/// for mset in metadata.sets:
///     print(mset.selector_string)  # "source.python"
///     print(mset.items.line_comment)  # "//"
/// ```
#[pyclass(name = "MetadataSet", skip_from_py_object)]
#[derive(Clone)]
pub struct PyMetadataSet {
    pub selector_string: String,
    pub items: PyMetadataItem,
}

#[pymethods]
impl PyMetadataSet {
    #[getter]
    pub fn selector_string(&self) -> String {
        self.selector_string.clone()
    }

    #[getter]
    pub fn items(&self) -> PyMetadataItem {
        self.items.clone()
    }

    pub fn __repr__(&self) -> String {
        format!("MetadataSet(selector='{}', items={:?})", self.selector_string, self.items)
    }
}

// ============================================================================
// PyMetadata — Collection of metadata sets
// ============================================================================

/// Collection of metadata sets loaded from `.tmPreferences` files.
///
/// Metadata includes indent rules, comment patterns, and other editor
/// preferences loaded from `.tmPreferences` files bundled with syntax
/// definitions.
///
/// Example:
/// ```python
/// ss = syntect.SyntaxSet.load_defaults(True)
/// if ss.metadata:
///     for mset in ss.metadata.sets:
///         print(mset.selector_string, mset.items.line_comment)
/// ```
#[pyclass(name = "Metadata", skip_from_py_object)]
pub struct PyMetadata {
    pub sets: Vec<PyMetadataSet>,
}

#[pymethods]
impl PyMetadata {
    #[getter]
    pub fn sets(&self) -> Vec<PyMetadataSet> {
        self.sets.clone()
    }

    pub fn __len__(&self) -> usize {
        self.sets.len()
    }

    pub fn __repr__(&self) -> String {
        format!("Metadata(sets={})", self.sets.len())
    }
}

// ============================================================================
// Convert upstream Metadata to Python types
// ============================================================================

#[cfg(feature = "metadata")]
pub fn convert_metadata(
    metadata: &syntect::parsing::Metadata,
) -> PyMetadata {
    let sets: Vec<PyMetadataSet> = metadata.scoped_metadata.iter().map(|ms| {
        let items = convert_metadata_items(&ms.items);
        PyMetadataSet {
            selector_string: ms.selector_string.clone(),
            items,
        }
    }).collect();
    PyMetadata { sets }
}

#[cfg(feature = "metadata")]
fn convert_metadata_items(
    items: &syntect::parsing::MetadataItems,
) -> PyMetadataItem {
    PyMetadataItem {
        increase_indent_pattern: items.increase_indent_pattern.as_ref().map(|r| r.as_str().to_string()),
        decrease_indent_pattern: items.decrease_indent_pattern.as_ref().map(|r| r.as_str().to_string()),
        bracket_indent_next_line_pattern: items.bracket_indent_next_line_pattern.as_ref().map(|r| r.as_str().to_string()),
        disable_indent_next_line_pattern: items.disable_indent_next_line_pattern.as_ref().map(|r| r.as_str().to_string()),
        unindented_line_pattern: items.unindented_line_pattern.as_ref().map(|r| r.as_str().to_string()),
        indent_parens: items.indent_parens,
        shell_variables: items.shell_variables.iter().map(|(k, v)| (k.clone(), v.clone())).collect(),
        line_comment: items.line_comment.clone(),
        block_comment: items.block_comment.clone(),
    }
}
