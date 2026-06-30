//! Python bindings for syntect's dump (serialization) utilities.

use pyo3::prelude::*;
use pyo3::exceptions::PyOSError;
use std::io::BufRead;
use crate::errors;
use crate::syntax_set::PySyntaxSet;
use crate::theme_set::PyThemeSet;

// ============================================================================
// dump_syntax_set
// ============================================================================

/// Save a syntax set to a .packdump file.
///
/// Example:
/// ```python
/// syntect.dump_syntax_set(ss, "syntaxes.packdump")
/// ```
#[pyfunction]
pub fn dump_syntax_set(ss: &PySyntaxSet, path: &str) -> PyResult<()> {
    match syntect::dumps::dump_to_file(&ss.inner, path) {
        Ok(()) => Ok(()),
        Err(e) => Err(PyErr::new::<PyOSError, _>(
            errors::dump_error_to_string(&e),
        )),
    }
}

// ============================================================================
// load_syntax_set
// ============================================================================

/// Load a syntax set from a .packdump file.
///
/// Example:
/// ```python
/// ss = syntect.load_syntax_set("syntaxes.packdump")
/// ```
#[pyfunction]
pub fn load_syntax_set(path: &str) -> PyResult<PySyntaxSet> {
    match std::fs::File::open(path) {
        Ok(file) => {
            match syntect::dumps::from_reader::<syntect::parsing::SyntaxSet, _>(std::io::BufReader::new(file)) {
                Ok(ss) => Ok(PySyntaxSet { inner: ss }),
                Err(e) => Err(PyErr::new::<PyOSError, _>(
                    errors::dump_error_to_string(&e),
                )),
            }
        }
        Err(e) => Err(PyErr::new::<PyOSError, _>(
            format!("Failed to open file: {}", e),
        )),
    }
}

// ============================================================================
// dump_theme_set
// ============================================================================

/// Save a theme set to a .themedump file.
///
/// Example:
/// ```python
/// syntect.dump_theme_set(ts, "themes.themedump")
/// ```
#[pyfunction]
pub fn dump_theme_set(ts: &PyThemeSet, path: &str) -> PyResult<()> {
    match syntect::dumps::dump_to_file(&ts.inner, path) {
        Ok(()) => Ok(()),
        Err(e) => Err(PyErr::new::<PyOSError, _>(
            errors::dump_error_to_string(&e),
        )),
    }
}

// ============================================================================
// load_theme_set
// ============================================================================

/// Load a theme set from a .themedump file.
///
/// Example:
/// ```python
/// ts = syntect.load_theme_set("themes.themedump")
/// ```
#[pyfunction]
pub fn load_theme_set(path: &str) -> PyResult<PyThemeSet> {
    match std::fs::File::open(path) {
        Ok(file) => {
            match syntect::dumps::from_reader::<syntect::highlighting::ThemeSet, _>(std::io::BufReader::new(file)) {
                Ok(ts) => Ok(PyThemeSet { inner: ts }),
                Err(e) => Err(PyErr::new::<PyOSError, _>(
                    errors::dump_error_to_string(&e),
                )),
            }
        }
        Err(e) => Err(PyErr::new::<PyOSError, _>(
            format!("Failed to open file: {}", e),
        )),
    }
}
