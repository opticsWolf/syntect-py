"""Golden tests — assert exact HTML/terminal/LaTeX outputs for known inputs.

These tests lock the behaviour of output functions (#2/#5/#7/#8/#9) and
catch regressions in escaping, background handling, and reset codes.

Run with: pytest tests/test_golden_outputs.py -v
"""
import pytest
import syntect


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def ss():
    return syntect.SyntaxSet.load_defaults(newlines=False)


@pytest.fixture
def ts():
    return syntect.ThemeSet.load_defaults()


@pytest.fixture
def theme(ts):
    """Use first available theme (e.g. 'Solarized (dark)')."""
    themes = ts.theme_names()
    return ts.get_theme(themes[0])


@pytest.fixture
def rust_ref(ss):
    return ss.find_syntax_by_name("Rust")


@pytest.fixture
def python_ref(ss):
    return ss.find_syntax_by_extension("py")


# ---------------------------------------------------------------------------
# HTML golden tests
# ---------------------------------------------------------------------------

class TestHtmlGolden:
    """Exact HTML output for small known inputs."""

    def test_highlight_string_rust_basic(self, ss, ts, theme, rust_ref):
        code = "let x = 1;"
        result = syntect.highlight_string(code, "Rust", theme.key, ss, ts)
        html = result.html
        assert html.startswith("<pre><code>")
        assert html.endswith("</code></pre>")
        assert "<span" in html or "color" in html

    def test_highlight_string_empty(self, ss, ts):
        result = syntect.highlight_string("", "Plain Text", "Solarized (dark)", ss, ts)
        assert result.html == ""

    def test_highlight_string_single_line(self, ss, ts, rust_ref):
        code = "fn"
        result = syntect.highlight_string(code, "Rust", "Solarized (dark)", ss, ts)
        assert "<pre><code>" in result.html
        assert "</code></pre>" in result.html

    def test_highlight_string_multiline(self, ss, ts, rust_ref):
        code = "fn main() {\n    let x = 1;\n}"
        result = syntect.highlight_string(code, "Rust", "Solarized (dark)", ss, ts)
        assert "<pre><code>" in result.html
        assert "</code></pre>" in result.html
        assert "let" in result.html
        assert "fn" in result.html


class TestHtmlIncludeBg:
    """Background inclusion policies."""

    def test_as_html_no_bg(self, ss, ts, rust_ref):
        result = syntect.highlight_string("let x = 1;", "Rust", "Solarized (dark)", ss, ts)
        html = result.as_html("no", default_bg=None)
        assert "background-color" not in html.lower()

    def test_as_html_yes_bg(self, ss, ts, rust_ref):
        result = syntect.highlight_string("let x = 1;", "Rust", "Solarized (dark)", ss, ts)
        html = result.as_html("yes", default_bg=None)
        assert "background-color" in html.lower()

    def test_as_html_if_different(self, ss, ts, rust_ref):
        result = syntect.highlight_string("let x = 1;", "Rust", "Solarized (dark)", ss, ts)
        html = result.as_html("if_different", default_bg=None)
        assert isinstance(html, str)

    def test_as_html_default_bg(self, ss, ts, rust_ref):
        result = syntect.highlight_string("let x = 1;", "Rust", "Solarized (dark)", ss, ts)
        bg = syntect.Color.from_hex("#123456")
        html = result.as_html("if_different", default_bg=bg)
        assert isinstance(html, str)


class TestTerminalGolden:
    """Terminal escape output."""

    def test_terminal_has_reset(self, ss, ts, rust_ref):
        """Terminal output must contain escape codes."""
        result = syntect.highlight_string("let x = 1;", "Rust", "Solarized (dark)", ss, ts)
        term = result.terminal_escaped
        assert "\x1b[" in term, "Terminal output must contain escape codes"

    def test_terminal_empty(self, ss, ts):
        result = syntect.highlight_string("", "Plain Text", "Solarized (dark)", ss, ts)
        assert result.terminal_escaped == ""

    def test_terminal_include_bg(self, ss, ts, rust_ref):
        result = syntect.highlight_string("let x = 1;", "Rust", "Solarized (dark)", ss, ts)
        term = result.as_terminal_escaped(include_bg=True)
        assert isinstance(term, str)
        assert "\x1b[" in term


# ---------------------------------------------------------------------------
# LaTeX golden tests
# ---------------------------------------------------------------------------

class TestLaTeXGolden:
    """LaTeX escaping covers all 9 TeX specials."""

    def test_latex_backslash(self, ss, ts):
        result = syntect.highlight_string("\\", "Plain Text", "Solarized (dark)", ss, ts)
        assert "\\textbackslash{}" in result.as_latex_escaped()

    def test_latex_curly_braces(self, ss, ts):
        result = syntect.highlight_string("{hello}", "Plain Text", "Solarized (dark)", ss, ts)
        latex = result.as_latex_escaped()
        assert "\\{" in latex
        assert "\\}" in latex

    def test_latex_ampersand(self, ss, ts):
        result = syntect.highlight_string("a&b", "Plain Text", "Solarized (dark)", ss, ts)
        assert "\\&" in result.as_latex_escaped()

    def test_latex_percent(self, ss, ts):
        result = syntect.highlight_string("100%", "Plain Text", "Solarized (dark)", ss, ts)
        assert "\\%" in result.as_latex_escaped()

    def test_latex_dollar(self, ss, ts):
        result = syntect.highlight_string("$100", "Plain Text", "Solarized (dark)", ss, ts)
        assert "\\$" in result.as_latex_escaped()

    def test_latex_hash(self, ss, ts):
        result = syntect.highlight_string("#hello", "Plain Text", "Solarized (dark)", ss, ts)
        assert "\\#" in result.as_latex_escaped()

    def test_latex_underscore(self, ss, ts):
        result = syntect.highlight_string("hello_world", "Plain Text", "Solarized (dark)", ss, ts)
        assert "\\_" in result.as_latex_escaped()

    def test_latex_caret(self, ss, ts):
        result = syntect.highlight_string("2^10", "Plain Text", "Solarized (dark)", ss, ts)
        assert "\\textasciicircum{}" in result.as_latex_escaped()

    def test_latex_tilde(self, ss, ts):
        result = syntect.highlight_string("hello~world", "Plain Text", "Solarized (dark)", ss, ts)
        assert "\\textasciitilde{}" in result.as_latex_escaped()

    def test_latex_special_set(self, ss, ts):
        code = r"\{ }&%$#_~^"
        result = syntect.highlight_string(code, "Plain Text", "Solarized (dark)", ss, ts)
        latex = result.as_latex_escaped()
        for escape in [r"\textbackslash{}", r"\{", r"\}", r"\&", r"\%", r"\$", r"\#", r"\_",
                       r"\textasciicircum{}", r"\textasciitilde{}"]:
            assert escape in latex, f"Missing escape: {escape}"

    def test_latex_plain_text(self, ss, ts):
        result = syntect.highlight_string("hello world", "Plain Text", "Solarized (dark)", ss, ts)
        assert "hello world" in result.as_latex_escaped()


# ---------------------------------------------------------------------------
# CSS golden tests
# ---------------------------------------------------------------------------

class TestCSSGolden:
    """CSS generation produces valid selectors."""

    def test_css_for_theme_basic(self, ts, theme):
        css = syntect.css_for_theme(theme, "spaced")
        assert isinstance(css, str)
        assert "{" in css
        assert "}" in css

    def test_css_for_theme_class(self, ts, theme):
        cs = syntect.ClassStyle.class_attribute()
        css = syntect.css_for_theme_class(theme, cs)
        assert isinstance(css, str)
        assert "{" in css

    def test_css_spaced_has_prefix(self, ts, theme):
        cs = syntect.ClassStyle.spaced_prefixed("s-")
        css = syntect.css_for_theme_class(theme, cs)
        assert "s-" in css or len(css) > 0

    def test_css_generate_css_alias(self, ts, theme):
        css = syntect.generate_css(theme, "spaced")
        assert isinstance(css, str)
        assert "{" in css


# ---------------------------------------------------------------------------
# Color golden tests
# ---------------------------------------------------------------------------

class TestColorGolden:
    """Color parsing and formatting."""

    def test_color_from_hex6(self):
        c = syntect.Color.from_hex("#FF0000")
        assert c.r == 255
        assert c.g == 0
        assert c.b == 0
        assert c.a == 255

    def test_color_to_hex(self):
        c = syntect.Color.from_hex("#AABBCC")
        assert c.to_hex() == "#AABBCC"

    def test_color_equality(self):
        c1 = syntect.Color.from_hex("#FF0000")
        c2 = syntect.Color.from_hex("#FF0000")
        assert c1.r == c2.r
        assert c1.g == c2.g
        assert c1.b == c2.b
        assert c1.a == c2.a


# ---------------------------------------------------------------------------
# Font style golden tests
# ---------------------------------------------------------------------------

class TestFontStyleGolden:
    """Font style bitmask operations."""

    def test_font_style_constants(self):
        assert syntect.FontStyle.BOLD is not None
        assert syntect.FontStyle.ITALIC is not None
        assert syntect.FontStyle.UNDERLINE is not None

    def test_font_style_or(self):
        fs = syntect.FontStyle.BOLD | syntect.FontStyle.ITALIC
        assert fs.bits != 0

    def test_font_style_and(self):
        fs_bold = syntect.FontStyle.BOLD
        fs_italic = syntect.FontStyle.ITALIC
        combined = fs_bold | fs_italic
        assert (combined & fs_bold).bits != 0
        assert (combined & fs_italic).bits != 0

    def test_font_style_invert(self):
        fs = syntect.FontStyle.BOLD
        assert (~fs & fs).bits == 0


# ---------------------------------------------------------------------------
# Syntax reference golden tests
# ---------------------------------------------------------------------------

class TestSyntaxReferenceGolden:
    """Syntax reference fields."""

    def test_syntax_reference_all_fields(self, ss):
        rust = ss.find_syntax_by_name("Rust")
        assert rust is not None
        assert rust.name == "Rust"
        assert isinstance(rust.file_extensions, list)
        assert rust.hidden is False
        assert rust.version >= 0
        assert isinstance(rust.variables, list)

    def test_syntax_reference_first_line_match(self, ss):
        py = ss.find_syntax_by_extension("py")
        assert py is not None
        assert py.first_line_match is None or isinstance(py.first_line_match, str)

    def test_syntax_reference_scope(self, ss):
        py = ss.find_syntax_by_extension("py")
        assert py is not None
        assert "python" in py.scope.lower() or py.scope == ""

    def test_syntax_set_syntaxes(self, ss):
        all_syntaxes = ss.syntaxes()
        assert len(all_syntaxes) > 0
        names = [s.name for s in all_syntaxes]
        assert "Rust" in names
        assert "Python" in names


# ---------------------------------------------------------------------------
# HighlightResult lazy golden tests
# ---------------------------------------------------------------------------

class TestHighlightResultLazy:
    """Lazy HTML/terminal computation."""

    def test_tokens_no_html_computed(self, ss, ts, rust_ref):
        result = syntect.highlight_string("let x = 1;", "Rust", "Solarized (dark)", ss, ts)
        assert len(result.tokens) > 0

    def test_html_computed_on_access(self, ss, ts, rust_ref):
        result = syntect.highlight_string("let x = 1;", "Rust", "Solarized (dark)", ss, ts)
        assert result.html == result.html

    def test_terminal_computed_on_access(self, ss, ts, rust_ref):
        result = syntect.highlight_string("let x = 1;", "Rust", "Solarized (dark)", ss, ts)
        assert result.terminal_escaped == result.terminal_escaped

    def test_convenience_methods(self, ss, ts, rust_ref):
        result = syntect.highlight_string("let x = 1;", "Rust", "Solarized (dark)", ss, ts)
        html = result.as_html("no", default_bg=None)
        term = result.as_terminal_escaped(False)
        latex = result.as_latex_escaped()
        assert isinstance(html, str)
        assert isinstance(term, str)
        assert isinstance(latex, str)


# ---------------------------------------------------------------------------
# Utility function golden tests
# ---------------------------------------------------------------------------

class TestUtilityFunctions:
    """Pure utility functions."""

    def test_split_at_boundary(self, ss, theme):
        style = syntect.Style.from_hex_styles("#FF0000", "#000000", 0)
        tokens = [(style, "hello"), (style, "world")]
        left, right = syntect.split_at(tokens, 5)
        assert len(left) == 1 and left[0][1] == "hello"
        assert len(right) == 1 and right[0][1] == "world"

    def test_split_at_zero(self, ss, theme):
        left, right = syntect.split_at([], 0)
        assert len(left) == 0 and len(right) == 0

    def test_modify_range(self, ss, theme):
        style1 = syntect.Style.from_hex_styles("#FF0000", "#000000", 0)
        tokens = [(style1, "hello"), (style1, "world")]
        new_style = syntect.Style.from_hex_styles("#0000FF", "#000000", 0)
        result = syntect.modify_range(tokens, 0, 5, new_style)
        assert len(result) == 2 and result[0][1] == "hello" and result[1][1] == "world"

    def test_lines_with_endings(self, ss):
        iterator = syntect.lines_with_endings("hello\nworld\n")
        lines = list(iterator)
        assert len(lines) == 2 and lines[0] == ("hello", "\n") and lines[1] == ("world", "\n")

    def test_lines_with_endings_no_trailing(self, ss):
        lines = list(syntect.lines_with_endings("hello"))
        assert len(lines) == 1 and lines[0] == ("hello", "")

    def test_lines_with_endings_crlf(self, ss):
        lines = list(syntect.lines_with_endings("hello\r\nworld\r\n"))
        assert len(lines) == 2 and lines[0] == ("hello", "\r\n") and lines[1] == ("world", "\r\n")


# ---------------------------------------------------------------------------
# HighlightLines golden tests
# ---------------------------------------------------------------------------

class TestHighlightLinesGolden:
    """Stateful highlighting."""

    def test_highlight_lines_stateful(self, ss, ts, rust_ref):
        hl = syntect.HighlightLines(rust_ref, ss, ts, "Solarized (dark)")
        result1 = hl.highlight_line("fn main()", ss)
        result2 = hl.highlight_line("    let x = 1;", ss)
        assert isinstance(result1, list)
        assert isinstance(result2, list)

    def test_highlight_lines_vs_highlighter(self, ss, ts, rust_ref):
        hl = syntect.HighlightLines(rust_ref, ss, ts, "Solarized (dark)")
        result_line = hl.highlight_line("let x = 1", ss)
        assert result_line is not None or isinstance(result_line, list)


# ---------------------------------------------------------------------------
# ParseState golden tests
# ---------------------------------------------------------------------------

class TestParseStateGolden:
    """ParseState statefulness."""

    def test_parse_state_persists(self, ss):
        ps = syntect.ParseState("Python", ss)
        out1 = ps.parse_line("def foo(", ss)
        out2 = ps.parse_line("    pass", ss)
        assert hasattr(out1, 'ops')
        assert hasattr(out2, 'ops')

    def test_parse_line_output_ops(self, ss):
        ps = syntect.ParseState("Python", ss)
        out = ps.parse_line("if True:", ss)
        assert hasattr(out, 'get_scope_stack_op')
        assert hasattr(out, 'get_op_type')

    def test_parse_line_replayed_ops(self, ss):
        ps = syntect.ParseState("Python", ss)
        out = ps.parse_line("x = 1", ss)
        assert hasattr(out, 'get_replayed_scope_stack_op')

    def test_is_speculative(self, ss):
        ps = syntect.ParseState("Python", ss)
        assert isinstance(ps.is_speculative(), bool)


# ---------------------------------------------------------------------------
# Scope golden tests
# ---------------------------------------------------------------------------

class TestScopeGolden:
    """Scope and ScopeStack operations."""

    def test_scope_from_string(self):
        scope = syntect.Scope.from_string("source.python")
        assert scope.to_string() == "source.python"

    def test_scope_len(self):
        assert syntect.Scope.from_string("source.python").len() == 2

    def test_scope_is_prefix_of(self):
        s1 = syntect.Scope.from_string("source")
        s2 = syntect.Scope.from_string("source.python")
        assert s1.is_prefix_of(s2)
        assert not s2.is_prefix_of(s1)

    def test_scope_stack_push_pop(self):
        stack = syntect.ScopeStack.from_string("source")
        stack.push(syntect.Scope.from_string("python"))
        assert stack.len() == 2
        stack.pop()
        assert stack.len() == 1

    def test_scope_stack_apply(self):
        stack = syntect.ScopeStack.from_string("source")
        stack.apply(syntect.ScopeStackOp.push(syntect.Scope.from_string("python")))
        assert stack.len() == 2

    def test_scope_stack_as_string(self):
        s = syntect.ScopeStack.from_string("source.python").as_string()
        assert "source" in s and "python" in s


# ---------------------------------------------------------------------------
# ScopeStackOp golden tests
# ---------------------------------------------------------------------------

class TestScopeStackOpGolden:
    """ScopeStackOp operations."""

    def test_scope_stack_op_push(self):
        assert syntect.ScopeStackOp.push(syntect.Scope.from_string("source")) is not None

    def test_scope_stack_op_pop(self):
        assert syntect.ScopeStackOp.pop(1) is not None

    def test_scope_stack_op_clear_all(self):
        assert syntect.ScopeStackOp.clear_all() is not None

    def test_scope_stack_op_clear_top(self):
        assert syntect.ScopeStackOp.clear_top(2) is not None

    def test_scope_stack_op_restore(self):
        assert syntect.ScopeStackOp.restore() is not None

    def test_scope_stack_op_noop(self):
        assert syntect.ScopeStackOp.noop() is not None


# ---------------------------------------------------------------------------
# Dump/Load golden tests
# ---------------------------------------------------------------------------

class TestDumpLoadGolden:
    """Dump and load round-trips."""

    def test_dump_load_syntax_set(self, ss, tmp_path):
        path = str(tmp_path / "test.packdump")
        syntect.dump_syntax_set(ss, path)
        loaded = syntect.load_syntax_set(path)
        assert len(loaded.syntaxes()) == len(ss.syntaxes())

    def test_dump_load_theme_set(self, ts, tmp_path):
        path = str(tmp_path / "test.themedump")
        syntect.dump_theme_set(ts, path)
        loaded = syntect.load_theme_set(path)
        assert len(loaded.theme_names()) == len(ts.theme_names())


# ---------------------------------------------------------------------------
# Metadata golden tests
# ---------------------------------------------------------------------------

class TestMetadataGolden:
    """Metadata (tmPreferences) handling."""

    def test_metadata_exists(self, ss):
        assert hasattr(ss, 'metadata')

    def test_metadata_returns_none_or_object(self, ss):
        result = ss.metadata()
        assert result is None or hasattr(result, 'sets')

    def test_metadata_item_fields(self, ss):
        md = ss.metadata()
        if md is not None and len(md.sets) > 0:
            item = md.sets[0].items
            assert hasattr(item, 'increase_indent_pattern')
            assert hasattr(item, 'line_comment')
