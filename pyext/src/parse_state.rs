//! Python bindings for syntect's parsing state management.
//!
//! Implements real wrappers around syntect's ParseState, ScopeStack,
//! ScopeStackOp, ParseLineOutput, and Scope types.

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use syntect::parsing::{ParseState as SyntectParseState, ParseLineOutput as SyntectParseLineOutput, Scope, ScopeStack as SyntectScopeStack, ScopeStackOp as SyntectScopeStackOp};
use crate::syntax_set::PySyntaxSet;

// ============================================================================
// Helper: convert SyntectParseLineOutput to PyParseLineOutput
// ============================================================================

fn parse_output_to_python(output: SyntectParseLineOutput) -> PyParseLineOutput {
    let ops: Vec<(usize, String)> = output.ops.iter().map(|(pos, op)| {
        let op_str = match op {
            SyntectScopeStackOp::Push(s) => format!("Push({})", s.build_string()),
            SyntectScopeStackOp::Pop(n) => format!("Pop({})", n),
            SyntectScopeStackOp::Clear(_) => "Clear".to_string(),
            SyntectScopeStackOp::Restore => "Restore".to_string(),
            SyntectScopeStackOp::Noop => "Noop".to_string(),
        };
        (*pos, op_str)
    }).collect();

    let replayed: Vec<Vec<(usize, String)>> = output.replayed.iter().map(|line_ops| {
        line_ops.iter().map(|(pos, op)| {
            let op_str = match op {
                SyntectScopeStackOp::Push(s) => format!("Push({})", s.build_string()),
                SyntectScopeStackOp::Pop(n) => format!("Pop({})", n),
                SyntectScopeStackOp::Clear(_) => "Clear".to_string(),
                SyntectScopeStackOp::Restore => "Restore".to_string(),
                SyntectScopeStackOp::Noop => "Noop".to_string(),
            };
            (*pos, op_str)
        }).collect()
    }).collect();

    PyParseLineOutput {
        ops,
        replayed,
        warnings: output.warnings,
    }
}

#[allow(dead_code)]
fn scope_stack_op_to_string(op: &SyntectScopeStackOp) -> String {
    match op {
        SyntectScopeStackOp::Push(s) => format!("Push({})", s.build_string()),
        SyntectScopeStackOp::Pop(n) => format!("Pop({})", n),
        SyntectScopeStackOp::Clear(_) => "Clear".to_string(),
        SyntectScopeStackOp::Restore => "Restore".to_string(),
        SyntectScopeStackOp::Noop => "Noop".to_string(),
    }
}

#[allow(dead_code)]
fn scope_stack_op_type(op: &SyntectScopeStackOp) -> &'static str {
    match op {
        SyntectScopeStackOp::Push(_) => "Push",
        SyntectScopeStackOp::Pop(_) => "Pop",
        SyntectScopeStackOp::Clear(_) => "Clear",
        SyntectScopeStackOp::Restore => "Restore",
        SyntectScopeStackOp::Noop => "Noop",
    }
}

// ============================================================================
// PyScope (real wrapper around syntect::parsing::Scope)
// ============================================================================

/// A scope representing a semantic classification of text.
///
/// Example:
/// ```python
/// scope = syntect.Scope.from_string("source.rust keyword")
/// print(scope.to_string())  # "source.rust keyword"
/// print(scope.len())  # 3
/// ```
#[pyclass(name = "Scope", skip_from_py_object)]
#[derive(Clone)]
pub struct PyScope {
    pub inner: Scope,
}

#[pymethods]
impl PyScope {
    #[new]
    pub fn new(value: &str) -> PyResult<Self> {
        match Scope::new(value.trim()) {
            Ok(scope) => Ok(PyScope { inner: scope }),
            Err(e) => Err(PyErr::new::<PyValueError, _>(
                format!("Invalid scope: {}", e),
            )),
        }
    }

    #[staticmethod]
    pub fn from_string(s: &str) -> PyResult<Self> {
        Self::new(s)
    }

    pub fn to_string(&self) -> String {
        self.inner.build_string()
    }

    pub fn len(&self) -> u32 {
        self.inner.len()
    }

    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    /// Check if this scope is a prefix of another scope.
    pub fn is_prefix_of(&self, other: &PyScope) -> bool {
        self.inner.is_prefix_of(other.inner)
    }

    pub fn __eq__(&self, other: &PyScope) -> bool {
        self.inner == other.inner
    }

    pub fn __repr__(&self) -> String {
        format!("Scope('{}')", self.to_string())
    }
}

// ============================================================================
// PyScopeStackOp (real wrapper around syntect::parsing::ScopeStackOp)
// ============================================================================

/// An operation on a scope stack (push, pop, clear, restore).
#[pyclass(name = "ScopeStackOp", skip_from_py_object)]
pub struct PyScopeStackOp {
    inner: SyntectScopeStackOp,
}

#[pymethods]
impl PyScopeStackOp {
    /// Create a Push operation.
    #[staticmethod]
    pub fn push(scope: &PyScope) -> Self {
        PyScopeStackOp { inner: SyntectScopeStackOp::Push(scope.inner) }
    }

    /// Create a Pop operation that pops `count` scopes.
    #[staticmethod]
    pub fn pop(count: usize) -> Self {
        PyScopeStackOp { inner: SyntectScopeStackOp::Pop(count) }
    }

    /// Create a Clear operation that clears all scopes.
    #[staticmethod]
    pub fn clear_all() -> Self {
        PyScopeStackOp { inner: SyntectScopeStackOp::Clear(syntect::parsing::ClearAmount::All) }
    }

    /// Create a Clear operation that clears the top N scopes.
    #[staticmethod]
    pub fn clear_top(n: usize) -> Self {
        PyScopeStackOp { inner: SyntectScopeStackOp::Clear(syntect::parsing::ClearAmount::TopN(n)) }
    }

    /// Create a Restore operation that restores previously cleared scopes.
    #[staticmethod]
    pub fn restore() -> Self {
        PyScopeStackOp { inner: SyntectScopeStackOp::Restore }
    }

    /// Create a Noop operation.
    #[staticmethod]
    pub fn noop() -> Self {
        PyScopeStackOp { inner: SyntectScopeStackOp::Noop }
    }

    pub fn __repr__(&self) -> String {
        match self.inner {
            SyntectScopeStackOp::Push(_) => "ScopeStackOp(Push)".to_string(),
            SyntectScopeStackOp::Pop(n) => format!("ScopeStackOp(Pop, count={})", n),
            SyntectScopeStackOp::Clear(_) => "ScopeStackOp(Clear)".to_string(),
            SyntectScopeStackOp::Restore => "ScopeStackOp(Restore)".to_string(),
            SyntectScopeStackOp::Noop => "ScopeStackOp(Noop)".to_string(),
        }
    }
}

// ============================================================================
// PyScopeStack (real wrapper around syntect::parsing::ScopeStack)
// ============================================================================

/// A stack of scopes representing the current parsing state.
///
/// Example:
/// ```python
/// stack = syntect.ScopeStack()
/// stack.push(syntect.Scope("source.rust"))
/// stack.push(syntect.Scope("keyword"))
/// print(stack.as_string())  # "source.rust keyword"
/// print(stack.len())  # 2
/// ```
#[pyclass(name = "ScopeStack", skip_from_py_object)]
pub struct PyScopeStack {
    inner: SyntectScopeStack,
}

#[pymethods]
impl PyScopeStack {
    #[new]
    pub fn new() -> Self {
        PyScopeStack { inner: SyntectScopeStack::new() }
    }

    #[staticmethod]
    pub fn from_string(s: &str) -> PyResult<Self> {
        let scopes = s.split_whitespace()
            .map(|part| Scope::new(part.trim()))
            .collect::<Result<Vec<_>, _>>()
            .map_err(|e| PyErr::new::<PyValueError, _>(format!("Invalid scope in stack: {}", e)))?;
        Ok(PyScopeStack { inner: SyntectScopeStack::from_vec(scopes) })
    }

    /// Push a scope onto the stack.
    pub fn push(&mut self, scope: &PyScope) -> PyResult<()> {
        self.inner.push(scope.inner);
        Ok(())
    }

    /// Pop a scope from the stack.
    pub fn pop(&mut self) -> PyResult<()> {
        if self.inner.scopes.is_empty() {
            return Err(PyErr::new::<PyValueError, _>("Cannot pop from empty scope stack"));
        }
        self.inner.pop();
        Ok(())
    }

    /// Apply a scope stack operation (push, pop, clear, restore).
    pub fn apply(&mut self, op: &PyScopeStackOp) -> PyResult<()> {
        match self.inner.apply(&op.inner) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<PyValueError, _>(
                format!("ScopeStack error: {}", e),
            )),
        }
    }

    /// Get the scope stack as a space-separated string.
    pub fn as_string(&self) -> String {
        let mut result = String::new();
        let scopes = self.inner.as_slice();
        for (i, s) in scopes.iter().enumerate() {
            if i > 0 {
                result.push(' ');
            }
            result.push_str(&s.build_string());
        }
        result
    }

    /// Get the length of the scope stack.
    pub fn len(&self) -> usize {
        self.inner.len()
    }

    /// Check if the scope stack is empty.
    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    pub fn __repr__(&self) -> String {
        format!("ScopeStack([{}])", self.as_string())
    }
}

// ============================================================================
// PyParseLineOutput (real wrapper around syntect::parsing::ParseLineOutput)
// ============================================================================

/// Output from parsing a line, containing scope stack operations.
///
/// Example:
/// ```python
/// output = parse_state.parse_line("fn main() {", ss)
/// for pos, op in output.ops:
///     print(f"Position {pos}: {op}")
/// ```
#[pyclass(name = "ParseLineOutput", skip_from_py_object)]
pub struct PyParseLineOutput {
    ops: Vec<(usize, String)>,
    replayed: Vec<Vec<(usize, String)>>,
    warnings: Vec<String>,
}

#[pymethods]
impl PyParseLineOutput {
    #[getter]
    pub fn ops(&self) -> Vec<(usize, String)> {
        self.ops.clone()
    }

    /// Get the scope stack operation at the given index as a ScopeStackOp object.
    ///
    /// Example:
    /// ```python
    /// output = parse_state.parse_line("fn main() {", ss)
    /// for pos, op_str in output.ops:
    ///     op = output.get_scope_stack_op(i)
    ///     print(op.op_type)  # 'Push', 'Pop', 'Clear', 'Restore', 'Noop'
    /// ```
    pub fn get_scope_stack_op(&self, index: usize) -> PyResult<PyScopeStackOp> {
        if index >= self.ops.len() {
            return Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>(
                format!("Index {} out of range for ops (length {})", index, self.ops.len())
            ));
        }
        let op_str = &self.ops[index].1;
        Ok(parse_op_string_to_scope_stack_op(op_str))
    }

    /// Get the op type (Push, Pop, Clear, Restore, Noop) for the operation at the given index.
    pub fn get_op_type(&self, index: usize) -> PyResult<String> {
        if index >= self.ops.len() {
            return Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>(
                format!("Index {} out of range for ops (length {})", index, self.ops.len())
            ));
        }
        let op_str = &self.ops[index].1;
        Ok(scope_stack_op_type_str(op_str))
    }

    #[getter]
    pub fn replayed(&self) -> Vec<Vec<(usize, String)>> {
        self.replayed.clone()
    }

    #[getter]
    pub fn warnings(&self) -> Vec<String> {
        self.warnings.clone()
    }

    pub fn __repr__(&self) -> String {
        format!(
            "ParseLineOutput(ops={}, replayed={}, warnings={})",
            self.ops.len(),
            self.replayed.len(),
            self.warnings.len()
        )
    }
}

// Helper: parse op string back to ScopeStackOp
fn parse_op_string_to_scope_stack_op(op_str: &str) -> PyScopeStackOp {
    if op_str.starts_with("Push(") && op_str.ends_with(')') {
        let inner = &op_str[5..op_str.len()-1];
        if let Ok(scope) = PyScope::new(inner) {
            return PyScopeStackOp { inner: SyntectScopeStackOp::Push(scope.inner) };
        }
    }
    if op_str.starts_with("Pop(") && op_str.ends_with(')') {
        if let Ok(n) = op_str[4..op_str.len()-1].parse::<usize>() {
            return PyScopeStackOp { inner: SyntectScopeStackOp::Pop(n) };
        }
    }
    if op_str == "Clear" {
        return PyScopeStackOp { inner: SyntectScopeStackOp::Clear(syntect::parsing::ClearAmount::All) };
    }
    if op_str == "Restore" {
        return PyScopeStackOp { inner: SyntectScopeStackOp::Restore };
    }
    if op_str == "Noop" {
        return PyScopeStackOp { inner: SyntectScopeStackOp::Noop };
    }
    PyScopeStackOp { inner: SyntectScopeStackOp::Noop }
}

fn scope_stack_op_type_str(op_str: &str) -> String {
    if op_str.starts_with("Push(") { return "Push".to_string(); }
    if op_str.starts_with("Pop(") { return "Pop".to_string(); }
    if op_str == "Clear" { return "Clear".to_string(); }
    if op_str == "Restore" { return "Restore".to_string(); }
    if op_str == "Noop" { return "Noop".to_string(); }
    "Unknown".to_string()
}

// ============================================================================
// PyMatchPower — Scope matching score
// ============================================================================

/// A score representing how well a scope matches a theme rule.
///
/// Higher values indicate stronger matches. Used internally by the
/// highlighting engine to resolve conflicts between overlapping scope rules.
///
/// Example:
/// ```python
/// # MatchPower is used internally; exposed for advanced debugging
/// print(match_power.value)  # e.g., 0.0, 1.0, etc.
/// ```
#[pyclass(name = "MatchPower", skip_from_py_object)]
#[derive(Clone)]
pub struct PyMatchPower {
    value: f64,
}

#[pymethods]
impl PyMatchPower {
    #[new]
    pub fn new(value: f64) -> Self {
        PyMatchPower { value }
    }

    #[getter]
    pub fn value(&self) -> f64 {
        self.value
    }

    pub fn __repr__(&self) -> String {
        format!("MatchPower({:.4})", self.value)
    }

    pub fn __float__(&self) -> f64 {
        self.value
    }
}

// ============================================================================
// PyClearAmount — Clear operation parameter
// ============================================================================

/// Controls how many scopes are cleared in a Clear operation.
///
/// Example:
/// ```python
/// op = syntect.ScopeStackOp.clear_all()  # Clear all scopes
/// op = syntect.ScopeStackOp.clear_top(2)  # Clear top 2 scopes
/// ```
#[pyclass(name = "ClearAmount", skip_from_py_object)]
#[derive(Clone)]
pub struct PyClearAmount {
    kind: String,
    value: usize,
}

#[pymethods]
impl PyClearAmount {
    #[staticmethod]
    pub fn all_() -> Self {
        PyClearAmount { kind: "all".to_string(), value: 0 }
    }

    #[staticmethod]
    pub fn top_n(n: usize) -> Self {
        PyClearAmount { kind: "top_n".to_string(), value: n }
    }

    #[getter]
    pub fn kind(&self) -> String {
        self.kind.clone()
    }

    #[getter]
    pub fn value(&self) -> usize {
        self.value
    }

    pub fn __repr__(&self) -> String {
        if self.kind == "all" {
            "ClearAmount(all)".to_string()
        } else {
            format!("ClearAmount(top_n={})", self.value)
        }
    }
}

// ============================================================================
// PyContextId — Context identifier
// ============================================================================

/// An opaque identifier for a syntax context.
///
/// Context IDs are used internally to reference contexts across syntax
/// definitions. They combine a syntax index and a context index.
///
/// Example:
/// ```python
/// # ContextId is used internally; exposed for debugging
/// print(context_id.syntax_index)  # which syntax
/// print(context_id.context_index)  # which context
/// ```
#[pyclass(name = "ContextId", skip_from_py_object)]
#[derive(Clone)]
pub struct PyContextId {
    syntax_index: usize,
    context_index: usize,
}

#[pymethods]
impl PyContextId {
    #[new]
    pub fn new(syntax_index: usize, context_index: usize) -> Self {
        PyContextId {
            syntax_index,
            context_index,
        }
    }

    #[getter]
    pub fn syntax_index(&self) -> usize {
        self.syntax_index
    }

    #[getter]
    pub fn context_index(&self) -> usize {
        self.context_index
    }

    pub fn __repr__(&self) -> String {
        format!("ContextId(syntax={}, context={})", self.syntax_index, self.context_index)
    }

    pub fn __eq__(&self, other: &PyContextId) -> bool {
        self.syntax_index == other.syntax_index && self.context_index == other.context_index
    }
}

// ============================================================================
// PyParseState (real wrapper around syntect::parsing::ParseState)
// ============================================================================

/// Parser state for incremental syntax parsing.
///
/// This is a **real stateful parser** — it maintains internal state between
/// `parse_line()` calls, allowing context-sensitive parsing across lines.
///
/// Example:
/// ```python
/// parse_state = syntect.ParseState("Rust", ss)
/// output1 = parse_state.parse_line("fn main() {", ss)
/// output2 = parse_state.parse_line("    let x = 42;", ss)
/// # Stateful: output2 ops reflect context from output1
/// print(parse_state.is_speculative())  # True during backtracking
/// print(parse_state.syntax_name)       # "Rust"
/// ```
#[pyclass(name = "ParseState", skip_from_py_object)]
pub struct PyParseState {
    inner: SyntectParseState,
    syntax_name: String,
}

#[pymethods]
impl PyParseState {
    /// Create a new ParseState for the given syntax.
    ///
    /// Example:
    /// ```python
    /// ss = syntect.SyntaxSet.load_defaults(True)
    /// ps = syntect.ParseState("Rust", ss)
    /// ```
    #[new]
    pub fn new(syntax_name: &str, syntax_set: &PySyntaxSet) -> PyResult<Self> {
        let syntax_ref = syntax_set.inner.find_syntax_by_name(syntax_name)
            .ok_or_else(|| PyErr::new::<PyValueError, _>(
                format!("Syntax not found: {}", syntax_name)
            ))?;
        Ok(PyParseState {
            inner: SyntectParseState::new(&syntax_ref),
            syntax_name: syntax_name.to_string(),
        })
    }

    /// Parse a line and return the scope stack operations.
    ///
    /// This uses the real stateful parser — state persists between calls,
    /// allowing context-sensitive parsing across lines.
    ///
    /// Example:
    /// ```python
    /// output = parse_state.parse_line("fn main() {", ss)
    /// for pos, op in output.ops:
    ///     print(f"Position {pos}: {op}")
    /// ```
    pub fn parse_line(&mut self, line: &str, syntax_set: &PySyntaxSet) -> PyResult<PyParseLineOutput> {
        match self.inner.parse_line(line, &syntax_set.inner) {
            Ok(output) => Ok(parse_output_to_python(output)),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Parsing error: {}", e),
            )),
        }
    }

    /// Check if the parser is in speculative (branch) mode.
    ///
    /// Returns `True` when the parser is in a branch point (backtracking
    /// mode), which happens during complex syntax parsing. Returns `False`
    /// when the parser is in a deterministic state.
    ///
    /// Example:
    /// ```python
    /// ps = syntect.ParseState("Rust", ss)
    /// print(ps.is_speculative())  # False for simple syntaxes
    /// ```
    pub fn is_speculative(&self) -> bool {
        self.inner.is_speculative()
    }

    /// Get the name of the syntax this ParseState is configured for.
    #[getter]
    pub fn syntax_name(&self) -> String {
        self.syntax_name.clone()
    }

    pub fn __repr__(&self) -> String {
        format!("ParseState(syntax='{}', speculative={})", self.syntax_name, self.inner.is_speculative())
    }
}
