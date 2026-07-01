"""Stub conformance test — ensures .pyi matches the runtime API.

This test imports the module, inspects every class/function via dir(),
and verifies that the stub file (syntect.pyi) declares the same public
names.  A drift between stub and runtime is a bug that breaks mypy.

Run with: pytest tests/test_stub_conformance.py -v
"""
import ast
import os
import syntect


# Mapping of stub class names to runtime class names
# Only PySyntaxReference has a Py prefix in the runtime
STUB_TO_RUNTIME = {
    "SyntaxReference": "PySyntaxReference",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pyi_names(path: str) -> dict[str, set[str]]:
    """Parse syntect.pyi and return {class_name: {method_names}}.

    Also returns module-level function names in a special key.
    """
    with open(path) as f:
        tree = ast.parse(f.read())

    result: dict[str, set[str]] = {}
    module_funcs: set[str] = set()

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            methods: set[str] = set()
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.add(item.name)
                elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    methods.add(item.target.id)
            result[node.name] = methods
        elif isinstance(node, ast.FunctionDef):
            module_funcs.add(node.name)

    result["__module__"] = module_funcs
    return result


def _runtime_names() -> dict[str, set[str]]:
    """Inspect the loaded syntect module via dir()."""
    result: dict[str, set[str]] = {}
    module_funcs: set[str] = set()

    for name in dir(syntect):
        obj = getattr(syntect, name)
        if isinstance(obj, type):
            methods: set[str] = set()
            for m in dir(obj):
                if not m.startswith("_") or m in ("__iter__", "__next__", "__len__", "__repr__", "__contains__", "__getitem__", "__call__"):
                    methods.add(m)
            result[name] = methods
        elif callable(obj):
            module_funcs.add(name)

    result["__module__"] = module_funcs
    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_stub_matches_runtime():
    """Every public name in the Rust module must appear in the stub, and vice versa."""
    stub_dir = os.path.dirname(os.path.abspath(__file__))
    pyi_path = os.path.join(stub_dir, "..", "syntect.pyi")
    pyi_names = _pyi_names(pyi_path)
    runtime_names = _runtime_names()

    # Check module-level functions (filter out dunder methods)
    stub_funcs = {f for f in pyi_names.get("__module__", set()) if not f.startswith("__")}
    runtime_funcs = {f for f in runtime_names.get("__module__", set()) if not f.startswith("__")}

    missing_from_stub = runtime_funcs - stub_funcs
    extra_in_stub = stub_funcs - runtime_funcs

    if missing_from_stub:
        raise AssertionError(
            f"Runtime functions missing from stub: {sorted(missing_from_stub)}"
        )
    if extra_in_stub:
        raise AssertionError(
            f"Stub functions not in runtime: {sorted(extra_in_stub)}"
        )

    # Check each class - map stub names to runtime names
    for stub_cls_name, stub_methods in pyi_names.items():
        if stub_cls_name == "__module__":
            continue
        runtime_cls_name = STUB_TO_RUNTIME.get(stub_cls_name, stub_cls_name)
        runtime_methods = runtime_names.get(runtime_cls_name)
        if runtime_methods is None:
            raise AssertionError(
                f"Stub class '{stub_cls_name}' (runtime: '{runtime_cls_name}') not found in runtime"
            )

        # Filter out dunder methods and inherited Exception methods
        real_stub = {m for m in stub_methods if not m.startswith("__")}
        real_runtime = {m for m in runtime_methods if not m.startswith("__")} - {"add_note", "args", "with_traceback", "__cause__", "__context__", "__traceback__", "__suppress_context__", "__dict__"}

        missing_methods = real_runtime - real_stub
        extra_methods = real_stub - real_runtime

        if missing_methods:
            raise AssertionError(
                f"Methods in runtime but missing from stub for '{stub_cls_name}': "
                f"{sorted(missing_methods)}"
            )
        if extra_methods:
            raise AssertionError(
                f"Methods in stub but missing from runtime for '{stub_cls_name}': "
                f"{sorted(extra_methods)}"
            )


def test_metadata_method_exists():
    """Metadata method should be exposed on SyntaxSet."""
    ss = syntect.SyntaxSet.load_defaults(False)
    assert hasattr(ss, "metadata"), "SyntaxSet should have metadata property"


def test_syntax_reference_hidden_exists():
    """SyntaxReference.hidden should be accessible."""
    ss = syntect.SyntaxSet.load_defaults(False)
    rust = ss.find_syntax_by_name("Rust")
    assert rust is not None
    assert hasattr(rust, "hidden"), "SyntaxReference should have hidden attribute"
    assert isinstance(rust.hidden, bool)


def test_syntax_set_find_for_file():
    """SyntaxSet.find_syntax_for_file should be accessible."""
    ss = syntect.SyntaxSet.load_defaults(False)
    result = ss.find_syntax_for_file("test.rs")
    assert result is None or hasattr(result, "name")


def test_syntax_set_find_plain_text():
    """SyntaxSet.find_syntax_plain_text should be accessible."""
    ss = syntect.SyntaxSet.load_defaults(False)
    result = ss.find_syntax_plain_text()
    assert result is not None
    assert hasattr(result, "name")


def test_syntax_set_warnings():
    """SyntaxSet.warnings should be accessible."""
    ss = syntect.SyntaxSet.load_defaults(False)
    result = ss.warnings()
    assert isinstance(result, list)


def test_syntax_set_builder_methods():
    """SyntaxSetBuilder should expose all expected methods."""
    builder = syntect.SyntaxSetBuilder()
    assert hasattr(builder, "add_from_folder")
    assert hasattr(builder, "add_plain_text_syntax")
    assert hasattr(builder, "build")
    assert hasattr(builder, "warnings")


def test_theme_set_dump_methods():
    """ThemeSet should expose from_dump and to_dump."""
    ts = syntect.ThemeSet.load_defaults()
    assert hasattr(ts, "from_dump")
    assert hasattr(ts, "to_dump")


def test_syntax_set_dump_methods():
    """SyntaxSet should expose from_dump and to_dump."""
    ss = syntect.SyntaxSet.load_defaults(False)
    assert hasattr(ss, "from_dump")
    assert hasattr(ss, "to_dump")
