//! Python exception types for syntect errors.

use pyo3::create_exception;
use pyo3::exceptions::PyException;

// Create custom exception types (module name is "syntect" for the pymodule)
create_exception!(syntect, LoadingError, PyException, "Error loading a syntax or theme");
create_exception!(syntect, ParsingError, PyException, "Error parsing syntax");
create_exception!(syntect, DumpError, PyException, "Error dumping/loading binary data");
create_exception!(syntect, ParseSyntaxError, PyException, "Error parsing a syntax definition file");

/// Convert a syntect LoadingError to a Python exception string.
pub fn loading_error_to_string(e: &dyn std::error::Error) -> String {
    e.to_string()
}

/// Convert a syntect DumpError to a Python exception string.
pub fn dump_error_to_string(e: &dyn std::error::Error) -> String {
    e.to_string()
}
