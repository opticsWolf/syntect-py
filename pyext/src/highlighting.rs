//! Python bindings for advanced syntect::highlighting types.
//!
//! Exposes ScoredStyle and ScopeRangeIterator for advanced users.

use pyo3::prelude::*;

// ============================================================================
// PyScoredStyle — Cached style score for theme matching
// ============================================================================

/// A style with associated match scores for each component.
///
/// Used internally by the highlighting engine to resolve conflicts between
/// overlapping scope rules. Higher scores indicate stronger matches.
///
/// Example (advanced):
/// ```python
/// # ScoredStyle is used internally by Highlighter
/// # Exposed for advanced debugging and analysis
/// ```
#[pyclass(name = "ScoredStyle", skip_from_py_object)]
pub struct PyScoredStyle {
    pub foreground_r: u8,
    pub foreground_g: u8,
    pub foreground_b: u8,
    pub foreground_a: u8,
    pub foreground_score: f64,
    pub background_r: u8,
    pub background_g: u8,
    pub background_b: u8,
    pub background_a: u8,
    pub background_score: f64,
    pub font_style: u8,
    pub font_style_score: f64,
}

#[pymethods]
impl PyScoredStyle {
    #[getter]
    pub fn foreground_r(&self) -> u8 {
        self.foreground_r
    }

    #[getter]
    pub fn foreground_g(&self) -> u8 {
        self.foreground_g
    }

    #[getter]
    pub fn foreground_b(&self) -> u8 {
        self.foreground_b
    }

    #[getter]
    pub fn foreground_a(&self) -> u8 {
        self.foreground_a
    }

    #[getter]
    pub fn foreground_score(&self) -> f64 {
        self.foreground_score
    }

    #[getter]
    pub fn background_r(&self) -> u8 {
        self.background_r
    }

    #[getter]
    pub fn background_g(&self) -> u8 {
        self.background_g
    }

    #[getter]
    pub fn background_b(&self) -> u8 {
        self.background_b
    }

    #[getter]
    pub fn background_a(&self) -> u8 {
        self.background_a
    }

    #[getter]
    pub fn background_score(&self) -> f64 {
        self.background_score
    }

    #[getter]
    pub fn font_style(&self) -> u8 {
        self.font_style
    }

    #[getter]
    pub fn font_style_score(&self) -> f64 {
        self.font_style_score
    }

    #[new]
    pub fn new(
        fg_r: u8, fg_g: u8, fg_b: u8, fg_a: u8, fg_score: f64,
        bg_r: u8, bg_g: u8, bg_b: u8, bg_a: u8, bg_score: f64,
        font_style: u8, font_style_score: f64,
    ) -> Self {
        PyScoredStyle {
            foreground_r: fg_r, foreground_g: fg_g, foreground_b: fg_b, foreground_a: fg_a,
            foreground_score: fg_score,
            background_r: bg_r, background_g: bg_g, background_b: bg_b, background_a: bg_a,
            background_score: bg_score,
            font_style: font_style, font_style_score: font_style_score,
        }
    }

    pub fn __repr__(&self) -> String {
        format!(
            "ScoredStyle(fg=#{:02x}{:02x}{:02x}({:.2}), bg=#{:02x}{:02x}{:02x}({:.2}), fs={:02x}({:.2}))",
            self.foreground_r, self.foreground_g, self.foreground_b, self.foreground_score,
            self.background_r, self.background_g, self.background_b, self.background_score,
            self.font_style, self.font_style_score
        )
    }
}

// ============================================================================
// PyScopeRangeIterator — Iterate over scope ranges in a line
// ============================================================================

/// Iterator that yields (start, end, scope) tuples for a highlighted line.
///
/// This iterator walks through a line of text and yields the scope that
/// applies to each character range.
///
/// Example:
/// ```python
/// # Create from parse ops
/// for start, end, scope in syntect.ScopeRangeIterator(ops, line):
///     print(f"{start}-{end}: {scope}")
/// ```
#[pyclass(name = "ScopeRangeIterator", skip_from_py_object)]
#[derive(Clone)]
pub struct PyScopeRangeIterator {
    ops: Vec<(usize, String)>,
    line: String,
    index: usize,
    last_str_index: usize,
    current_scope: String,
}

#[pymethods]
impl PyScopeRangeIterator {
    #[new]
    pub fn new(ops: Vec<(usize, String)>, line: &str) -> Self {
        PyScopeRangeIterator {
            ops,
            line: line.to_string(),
            index: 0,
            last_str_index: 0,
            current_scope: String::new(),
        }
    }

    pub fn __iter__(&self) -> PyScopeRangeIterator {
        self.clone()
    }

    pub fn __next__(&mut self) -> Option<(usize, usize, String)> {
        if self.index >= self.ops.len() {
            return None;
        }

        let (_pos, op_str) = &self.ops[self.index];
        self.index += 1;

        // Extract scope from Push operation
        if op_str.starts_with("Push(") && op_str.ends_with(')') {
            self.current_scope = op_str[5..op_str.len()-1].to_string();
        }

        // Calculate end position
        let next_pos = if self.index < self.ops.len() {
            self.ops[self.index].0
        } else {
            self.line.len()
        };

        let result = (self.last_str_index, next_pos, self.current_scope.clone());
        self.last_str_index = next_pos;

        Some(result)
    }
}
