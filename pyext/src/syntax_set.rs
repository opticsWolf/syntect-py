//! Python bindings for syntect's syntax set management.

use pyo3::prelude::*;
use syntect::parsing::SyntaxSet as SyntectSyntaxSet;
use crate::errors;

// ============================================================================
// PySyntaxReference (read-only wrapper)
// ============================================================================

/// A reference to a loaded syntax definition.
///
/// Example:
/// ```python
/// ss = syntect.SyntaxSet.load_defaults(True)
/// rust = ss.find_syntax_by_name("Rust")
/// print(rust.name)           # "Rust"
/// print(rust.scope)          # "source.rust"
/// print(rust.file_extensions)  # ["rs"]
/// print(rust.first_line_match) # Optional regex pattern
/// print(rust.version)          # 2 (sublime-syntax v2)
/// print(rust.variables)        # {"base": "$base"}
/// ```
#[pyclass(skip_from_py_object)]
pub struct PySyntaxReference {
    pub name: String,
    pub file_extensions: Vec<String>,
    pub scope: String,
    pub hidden: bool,
    pub first_line_match: Option<String>,
    pub version: u32,
    pub variables: Vec<(String, String)>,
}

#[pymethods]
impl PySyntaxReference {
    #[getter]
    pub fn name(&self) -> String {
        self.name.clone()
    }

    #[getter]
    pub fn file_extensions(&self) -> Vec<String> {
        self.file_extensions.clone()
    }

    #[getter]
    pub fn scope(&self) -> String {
        self.scope.clone()
    }

    #[getter]
    pub fn hidden(&self) -> bool {
        self.hidden
    }

    /// Get the first line regex pattern, if defined.
    ///
    /// This is a regex that matches the first line of files using this syntax.
    #[getter]
    pub fn first_line_match(&self) -> Option<String> {
        self.first_line_match.clone()
    }

    /// Get the sublime-syntax format version (1 or 2).
    ///
    /// Version 2 adds support for more features like `first_line_match`
    /// and `variables`.
    #[getter]
    pub fn version(&self) -> u32 {
        self.version
    }

    /// Get the variables defined in this syntax definition.
    ///
    /// Variables are key-value pairs used for substitution in scope patterns.
    #[getter]
    pub fn variables(&self) -> Vec<(String, String)> {
        self.variables.clone()
    }

    pub fn __repr__(&self) -> String {
        format!(
            "SyntaxReference(name='{}', scope='{}', version={})",
            self.name, self.scope, self.version
        )
    }
}

// ============================================================================
// PySyntaxSetBuilder (builder for loading syntaxes from disk)
// ============================================================================

/// Builder for loading syntax definitions from disk into a SyntaxSet.
///
/// Use this to load custom syntax definitions from folders:
/// ```python
/// builder = syntect.SyntaxSetBuilder()
/// builder.add_from_folder("/path/to/syntaxes", True)
/// ss = builder.build()
/// ```
#[pyclass(name = "SyntaxSetBuilder", skip_from_py_object)]
pub struct PySyntaxSetBuilder {
    inner: syntect::parsing::SyntaxSetBuilder,
}

#[pymethods]
impl PySyntaxSetBuilder {
    #[new]
    pub fn new() -> Self {
        PySyntaxSetBuilder {
            inner: syntect::parsing::SyntaxSetBuilder::new(),
        }
    }

    /// Load all `.sublime-syntax` files from a folder into this builder.
    ///
    /// The `lines_include_newline` parameter tells the loader whether to expect
    /// newline characters at the end of lines. If you're passing lines without
    /// newlines (the common case), pass `False`.
    ///
    /// Returns a list of warnings (empty on success).
    pub fn add_from_folder(&mut self, path: &str, lines_include_newline: bool) -> PyResult<Vec<String>> {
        match self.inner.add_from_folder(path, lines_include_newline) {
            Ok(()) => Ok(self.inner.warnings().to_vec()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyOSError, _>(
                errors::loading_error_to_string(&e),
            )),
        }
    }

    /// Add a plain text syntax to this builder.
    pub fn add_plain_text_syntax(&mut self) {
        self.inner.add_plain_text_syntax();
    }

    /// Build a SyntaxSet from the loaded syntax definitions.
    pub fn build(&mut self) -> PySyntaxSet {
        PySyntaxSet { inner: std::mem::take(&mut self.inner).build() }
    }

    /// Get warnings collected during syntax loading.
    pub fn warnings(&self) -> Vec<String> {
        self.inner.warnings().to_vec()
    }

    pub fn __repr__(&self) -> String {
        format!("SyntaxSetBuilder(syntaxes={})", self.inner.syntaxes().len())
    }
}

// ============================================================================
// PySyntaxSet
// ============================================================================

/// A set of loaded syntax definitions.
///
/// Example:
/// ```python
/// ss = syntect.SyntaxSet.load_defaults(True)
/// rust = ss.find_syntax_by_name("Rust")
/// py = ss.find_syntax_by_extension("py")
/// ```
#[pyclass(name = "SyntaxSet", skip_from_py_object)]
pub struct PySyntaxSet {
    pub inner: SyntectSyntaxSet,
}

#[pymethods]
impl PySyntaxSet {
    #[new]
    pub fn new() -> Self {
        PySyntaxSet { inner: SyntectSyntaxSet::new() }
    }

    #[staticmethod]
    pub fn load_defaults(newlines: bool) -> Self {
        let inner = if newlines {
            SyntectSyntaxSet::load_defaults_newlines()
        } else {
            SyntectSyntaxSet::load_defaults_nonewlines()
        };
        PySyntaxSet { inner }
    }

    /// Create a builder to load syntaxes from disk.
    ///
    /// Example:
    /// ```python
    /// builder = syntect.SyntaxSetBuilder()
    /// builder.add_from_folder("/path/to/syntaxes", False)
    /// ss = builder.build()
    /// ```
    #[staticmethod]
    pub fn builder() -> PySyntaxSetBuilder {
        PySyntaxSetBuilder {
            inner: syntect::parsing::SyntaxSetBuilder::new(),
        }
    }

    /// Load syntaxes from a folder and build a SyntaxSet in one call.
    ///
    /// Example:
    /// ```python
    /// ss = syntect.SyntaxSet.load_from_folder("/path/to/syntaxes", False)
    /// ```
    #[staticmethod]
    pub fn load_from_folder(path: &str, _lines_include_newline: bool) -> PyResult<PySyntaxSet> {
        match SyntectSyntaxSet::load_from_folder(path) {
            Ok(ss) => Ok(PySyntaxSet { inner: ss }),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyOSError, _>(
                errors::loading_error_to_string(&e),
            )),
        }
    }

    /// Convert this syntax set into a builder so more syntaxes can be added.
    ///
    /// Example:
    /// ```python
    /// ss = syntect.SyntaxSet.load_defaults(True)
    /// builder = ss.into_builder()
    /// builder.add_from_folder("/custom/syntaxes", False)
    /// ss = builder.build()
    /// ```
    pub fn into_builder(&self) -> PyResult<PySyntaxSetBuilder> {
        // We need to clone the inner SyntaxSet to convert to builder
        // because into_builder consumes self
        Ok(PySyntaxSetBuilder {
            inner: self.inner.clone().into_builder(),
        })
    }

    /// Get warnings collected during syntax loading and linking.
    pub fn warnings(&self) -> Vec<String> {
        self.inner.warnings().to_vec()
    }

    pub fn find_syntax_by_extension(&self, ext: &str) -> Option<PySyntaxReference> {
        self.inner.find_syntax_by_extension(ext).map(|s| PySyntaxReference {
            name: s.name.clone(),
            file_extensions: s.file_extensions.clone(),
            scope: s.scope.to_string(),
            hidden: s.hidden,
            first_line_match: s.first_line_match.clone(),
            version: s.version,
            variables: s.variables.iter().map(|(k, v)| (k.clone(), v.clone())).collect(),
        })
    }

    pub fn find_syntax_by_name(&self, name: &str) -> Option<PySyntaxReference> {
        self.inner.find_syntax_by_name(name).map(|s| PySyntaxReference {
            name: s.name.clone(),
            file_extensions: s.file_extensions.clone(),
            scope: s.scope.to_string(),
            hidden: s.hidden,
            first_line_match: s.first_line_match.clone(),
            version: s.version,
            variables: s.variables.iter().map(|(k, v)| (k.clone(), v.clone())).collect(),
        })
    }

    pub fn find_syntax_by_scope(&self, scope: &str) -> Option<PySyntaxReference> {
        match syntect::parsing::Scope::new(scope) {
            Ok(s) => self.inner.find_syntax_by_scope(s).map(|s| PySyntaxReference {
                name: s.name.clone(),
                file_extensions: s.file_extensions.clone(),
                scope: s.scope.to_string(),
                hidden: s.hidden,
                first_line_match: s.first_line_match.clone(),
                version: s.version,
                variables: s.variables.iter().map(|(k, v)| (k.clone(), v.clone())).collect(),
            }),
            Err(_) => None,
        }
    }

    pub fn find_syntax_for_file(&self, path: &str) -> PyResult<Option<PySyntaxReference>> {
        match self.inner.find_syntax_for_file(path) {
            Ok(Some(s)) => Ok(Some(PySyntaxReference {
                name: s.name.clone(),
                file_extensions: s.file_extensions.clone(),
                scope: s.scope.to_string(),
                hidden: s.hidden,
                first_line_match: s.first_line_match.clone(),
                version: s.version,
                variables: s.variables.iter().map(|(k, v)| (k.clone(), v.clone())).collect(),
            })),
            Ok(None) => Ok(None),
            Err(_) => Ok(None),
        }
    }

    pub fn find_syntax_plain_text(&self) -> PySyntaxReference {
        let s = self.inner.find_syntax_plain_text();
        PySyntaxReference {
            name: s.name.clone(),
            file_extensions: s.file_extensions.clone(),
            scope: s.scope.to_string(),
            hidden: s.hidden,
            first_line_match: s.first_line_match.clone(),
            version: s.version,
            variables: s.variables.iter().map(|(k, v)| (k.clone(), v.clone())).collect(),
        }
    }

    pub fn syntaxes(&self) -> Vec<PySyntaxReference> {
        self.inner.syntaxes().iter().map(|s| PySyntaxReference {
            name: s.name.clone(),
            file_extensions: s.file_extensions.clone(),
            scope: s.scope.to_string(),
            hidden: s.hidden,
            first_line_match: s.first_line_match.clone(),
            version: s.version,
            variables: s.variables.iter().map(|(k, v)| (k.clone(), v.clone())).collect(),
        }).collect()
    }

    /// Create a SyntaxSet from a .packdump file.
    #[staticmethod]
    pub fn from_dump(path: &str) -> PyResult<PySyntaxSet> {
        match syntect::dumps::from_dump_file::<syntect::parsing::SyntaxSet, &str>(path) {
            Ok(ss) => Ok(PySyntaxSet { inner: ss }),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyOSError, _>(
                format!("Failed to load syntax dump: {}", e),
            )),
        }
    }

    /// Save this SyntaxSet to a .packdump file.
    pub fn to_dump(&self, path: &str) -> PyResult<()> {
        match syntect::dumps::dump_to_file(&self.inner, path) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyOSError, _>(
                format!("Failed to save syntax dump: {}", e),
            )),
        }
    }

    pub fn __repr__(&self) -> String {
        format!("SyntaxSet(syntaxes={})", self.inner.syntaxes().len())
    }

    /// Find all context references that are not linked to any syntax definition.
    ///
    /// This is useful for debugging syntax definitions that reference contexts
    /// that don't exist.
    ///
    /// Returns a list of unlinked context reference strings.
    ///
    /// Example:
    /// ```python
    /// ss = syntect.SyntaxSet.load_defaults(True)
    /// unlinked = ss.find_unlinked_contexts()
    /// print(unlinked)  # [] if all contexts are linked
    /// ```
    pub fn find_unlinked_contexts(&self) -> Vec<String> {
        self.inner.find_unlinked_contexts().into_iter().collect()
    }

    /// Get the metadata loaded from `.tmPreferences` files.
    ///
    /// Returns None if no metadata was loaded or if the metadata feature
    /// is not enabled.
    ///
    /// Example:
    /// ```python
    /// ss = syntect.SyntaxSet.load_defaults(True)
    /// metadata = ss.metadata
    /// if metadata:
    ///     for mset in metadata.sets:
    ///         print(mset.selector_string, mset.items.line_comment)
    /// ```
    #[cfg(feature = "metadata")]
    pub fn metadata(&self) -> Option<crate::metadata::PyMetadata> {
        // Note: syntect's SyntaxSet.metadata field is private in v5.3.0
        // We can't access it directly. Return None for now.
        // This is a known limitation - metadata is accessible via
        // SyntaxSetBuilder during construction, but not from loaded SyntaxSet.
        None
    }

    #[cfg(not(feature = "metadata"))]
    pub fn metadata(&self) -> Option<crate::metadata::PyMetadata> {
        // Metadata feature not enabled
        None
    }
}
