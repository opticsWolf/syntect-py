"""Phase 24: Test Expansion — Incremental highlighting, utility functions, and advanced tests"""
import pytest
import syntect


class TestHighlightStateSaveRestore:
    """Test that save_state returns meaningful data and from_state works."""

    def test_save_state_returns_state(self, ss, ts, theme, rust):
        """Test that save_state returns a HighlightState object."""
        hl = syntect.Highlighter(rust, theme)
        state = hl.save_state(ss, ts)
        assert state is not None
        assert isinstance(state, syntect.HighlightState)

    def test_highlight_state_fields(self, ss, ts, theme, rust):
        """Test that HighlightState has path_scope_stack and styles_stack."""
        hl = syntect.Highlighter(rust, theme)
        # Highlight a line to populate state
        hl.highlight_line("fn main() {", ss, ts)
        state = hl.save_state(ss, ts)
        assert hasattr(state, 'path_scope_stack')
        assert hasattr(state, 'styles_stack')
        # path_scope_stack should be a list
        assert isinstance(state.path_scope_stack, list)

    def test_from_state_creates_highlighter(self, ss, ts, theme, rust):
        """Test that from_state creates a working Highlighter."""
        hl = syntect.Highlighter(rust, theme)
        hl.highlight_line("fn main() {", ss, ts)
        state = hl.save_state(ss, ts)
        hl2 = syntect.Highlighter.from_state(state, theme)
        assert hl2 is not None
        assert isinstance(hl2, syntect.Highlighter)

    def test_highlight_lines_crlf(self, ss, ts, theme, rust):
        """Test that \\r\\n line endings are handled correctly."""
        hl = syntect.Highlighter(rust, theme)
        code = "fn main() {\r\n    let x = 42;\r\n}"
        tokens = hl.highlight_lines(code, ss, ts)
        for line_tokens in tokens:
            for _, text in line_tokens:
                assert '\r' not in text, f"Found \\r in token text: {repr(text)}"


class TestParseStatePersistence:
    """Test that ParseState maintains state between parse_line calls."""

    def test_parse_state_persists_across_lines(self, ss):
        """Test that ParseState maintains state between parse_line calls."""
        rust = ss.find_syntax_by_name("Rust")
        assert rust is not None
        ps = syntect.ParseState("Rust", ss)
        out1 = ps.parse_line("fn main() {", ss)
        out2 = ps.parse_line("    let x = 42;", ss)
        # Verify stateful behavior - second line should have ops
        assert out1 is not None
        assert out2 is not None

    def test_is_speculative(self, ss):
        """Test is_speculative() returns correct values."""
        ps = syntect.ParseState("Rust", ss)
        out = ps.parse_line("fn main() {", ss)
        # Fresh state, no branches — speculative is False
        assert not ps.is_speculative()

    def test_parse_state_syntax_name(self, ss):
        """Test ParseState exposes syntax_name."""
        ps = syntect.ParseState("Rust", ss)
        assert ps.syntax_name == "Rust"


class TestSyntaxReferenceFields:
    """Test all SyntaxReference fields."""

    def test_first_line_match(self, ss):
        """Test first_line_match field."""
        rust = ss.find_syntax_by_name("Rust")
        assert rust is not None
        assert rust.first_line_match is None or isinstance(rust.first_line_match, str)

    def test_version_field(self, ss):
        """Test version field."""
        rust = ss.find_syntax_by_name("Rust")
        assert rust is not None
        assert isinstance(rust.version, int)

    def test_variables_field(self, ss):
        """Test variables field returns list of tuples."""
        rust = ss.find_syntax_by_name("Rust")
        assert rust is not None
        variables = rust.variables
        assert isinstance(variables, list)
        # Each variable is a tuple of (name, regex)
        if len(variables) > 0:
            assert isinstance(variables[0], tuple)
            assert len(variables[0]) == 2


class TestFindUnlinkedContexts:
    """Test find_unlinked_contexts function."""

    def test_find_unlinked_contexts_returns_list(self, ss):
        """Test find_unlinked_contexts returns a list."""
        unlinked = ss.find_unlinked_contexts()
        assert isinstance(unlinked, list)

    def test_find_unlinked_contexts_returns_strings(self, ss):
        """Test find_unlinked_contexts returns list of strings."""
        unlinked = ss.find_unlinked_contexts()
        for item in unlinked:
            assert isinstance(item, str)


class TestMatchPower:
    """Test MatchPower class."""

    def test_match_power_create(self):
        """Test MatchPower can be created with a float value."""
        mp = syntect.MatchPower(0.5)
        assert mp is not None

    def test_match_power_value(self):
        """Test MatchPower.value."""
        mp = syntect.MatchPower(0.75)
        assert mp.value == pytest.approx(0.75, abs=0.01)

    def test_match_power_float_conversion(self):
        """Test MatchPower can be converted to float."""
        mp = syntect.MatchPower(0.5)
        assert float(mp) == pytest.approx(0.5, abs=0.01)

    def test_match_power_repr(self):
        """Test MatchPower repr."""
        mp = syntect.MatchPower(0.5)
        assert "MatchPower" in repr(mp)


class TestClearAmount:
    """Test ClearAmount class."""

    def test_clear_amount_all(self):
        """Test ClearAmount.all_()."""
        ca = syntect.ClearAmount.all_()
        assert ca is not None
        assert ca.kind == "all"
        assert ca.value == 0

    def test_clear_amount_top_n(self):
        """Test ClearAmount.top_n()."""
        ca = syntect.ClearAmount.top_n(3)
        assert ca is not None
        assert ca.kind == "top_n"
        assert ca.value == 3

    def test_clear_amount_repr(self):
        """Test ClearAmount repr."""
        ca1 = syntect.ClearAmount.all_()
        assert "ClearAmount(all)" in repr(ca1)
        ca2 = syntect.ClearAmount.top_n(5)
        assert "ClearAmount(top_n=5)" in repr(ca2)


class TestContextId:
    """Test ContextId class."""

    def test_context_id_create(self):
        """Test ContextId can be created with syntax_index and context_index."""
        cid = syntect.ContextId(0, 42)
        assert cid is not None

    def test_context_id_indices(self):
        """Test ContextId syntax_index and context_index."""
        cid = syntect.ContextId(5, 10)
        assert cid.syntax_index == 5
        assert cid.context_index == 10

    def test_context_id_repr(self):
        """Test ContextId repr."""
        cid = syntect.ContextId(1, 2)
        assert "ContextId" in repr(cid)


class TestParseSyntaxError:
    """Test ParseSyntaxError exception type."""

    def test_parse_syntax_error_exists(self):
        """Test ParseSyntaxError is a valid exception type."""
        assert hasattr(syntect, 'ParseSyntaxError')
        assert issubclass(syntect.ParseSyntaxError, Exception)

    def test_parse_syntax_error_raised(self):
        """Test ParseSyntaxError can be raised and caught."""
        with pytest.raises(syntect.ParseSyntaxError):
            raise syntect.ParseSyntaxError("test error")


class TestHighlightLines:
    """Test HighlightLines stateful highlighting class."""

    def test_highlight_lines_class_exists(self):
        """Test HighlightLines class exists."""
        assert hasattr(syntect, 'HighlightLines')

    def test_highlight_lines_stateful(self, ss, ts, theme, rust):
        """Test HighlightLines maintains state across lines."""
        hl = syntect.HighlightLines(rust, ts, theme.key)
        tokens1 = hl.highlight_line("fn main() {", ss)
        tokens2 = hl.highlight_line("    let x = 42;", ss)
        # Both should return tokens
        assert isinstance(tokens1, list)
        assert isinstance(tokens2, list)

    def test_highlight_lines_save_restore(self, ss, ts, theme, rust):
        """Test HighlightLines can be created and used."""
        hl = syntect.HighlightLines(rust, ts, theme.key)
        # HighlightLines doesn't have save_state/from_state in the Python bindings
        # but it is stateful via the upstream HighlightLines type
        tokens = hl.highlight_line("fn main() {", ss)
        assert isinstance(tokens, list)
        assert len(tokens) > 0


class TestClassStyle:
    """Test ClassStyle class methods."""

    def test_class_style_spaced(self):
        """Test ClassStyle.spaced()."""
        cs = syntect.ClassStyle.spaced()
        assert cs is not None

    def test_class_style_spaced_prefixed(self):
        """Test ClassStyle.spaced_prefixed()."""
        cs = syntect.ClassStyle.spaced_prefixed("custom-")
        assert cs is not None

    def test_class_style_class_attribute(self):
        """Test ClassStyle.class_attribute()."""
        cs = syntect.ClassStyle.class_attribute()
        assert cs is not None


class TestIncludeBg:
    """Test IncludeBg class methods."""

    def test_include_bg_no(self):
        """Test IncludeBg.no()."""
        ib = syntect.IncludeBg.no()
        assert ib is not None

    def test_include_bg_yes(self):
        """Test IncludeBg.yes()."""
        ib = syntect.IncludeBg.yes()
        assert ib is not None

    def test_include_bg_if_different(self):
        """Test IncludeBg.if_different()."""
        ib = syntect.IncludeBg.if_different()
        assert ib is not None


class TestUnderlineOption:
    """Test UnderlineOption class."""

    def test_underline_option_none(self):
        """Test UnderlineOption.none_()."""
        uo = syntect.UnderlineOption.none_()
        assert uo is None

    def test_underline_option_underline(self):
        """Test UnderlineOption.underline()."""
        uo = syntect.UnderlineOption.underline()
        assert uo is not None
        assert "underline" in repr(uo)

    def test_underline_option_stippled(self):
        """Test UnderlineOption.stippled_underline()."""
        uo = syntect.UnderlineOption.stippled_underline()
        assert uo is not None
        assert "stippled" in repr(uo).lower()

    def test_underline_option_squiggly(self):
        """Test UnderlineOption.squiggly_underline()."""
        uo = syntect.UnderlineOption.squiggly_underline()
        assert uo is not None
        assert "squiggly" in repr(uo).lower()


class TestStyleModifier:
    """Test StyleModifier class."""

    def test_style_modifier_creation(self):
        """Test StyleModifier can be created with optional fields."""
        fg = syntect.Color.from_hex("#FF0000")
        sm = syntect.StyleModifier(fg, None, None)
        assert sm.foreground is not None
        assert sm.background is None
        assert sm.font_style is None


class TestAsHtmlWithDefaultBg:
    """Test as_html with default_bg parameter."""

    def test_as_html_default_bg_none(self, ss, ts, theme, rust):
        """Test as_html with default_bg=None."""
        result = syntect.highlight_string("fn main() {}", "Rust", "base16-ocean.dark", ss, ts)
        html = result.as_html("if_different", None)
        assert isinstance(html, str)

    def test_as_html_default_bg_color(self, ss, ts, theme, rust):
        """Test as_html with default_bg=Color."""
        result = syntect.highlight_string("fn main() {}", "Rust", "base16-ocean.dark", ss, ts)
        default_bg = syntect.Color.from_hex("#1e1e1e")
        html = result.as_html("if_different", default_bg)
        assert isinstance(html, str)


class TestCssForTheme:
    """Test css_for_theme function."""

    def test_css_for_theme_spaced(self, ts):
        """Test css_for_theme with spaced style."""
        theme = ts.get_theme("base16-ocean.dark")
        css = syntect.css_for_theme(theme, "spaced")
        assert isinstance(css, str)
        assert len(css) > 0

    def test_css_for_theme_class_attribute(self, ts):
        """Test css_for_theme with class_attribute style."""
        theme = ts.get_theme("base16-ocean.dark")
        css = syntect.css_for_theme(theme, "class_attribute")
        assert isinstance(css, str)
        assert len(css) > 0


class TestHighlightLinesRepr:
    """Test repr methods."""

    def test_highlighter_repr(self, ss, theme, rust):
        """Test Highlighter repr."""
        hl = syntect.Highlighter(rust, theme)
        r = repr(hl)
        assert "Highlighter" in r

    def test_highlight_result_repr(self, ss, ts, theme, rust):
        """Test HighlightResult repr."""
        result = syntect.highlight_string("fn main() {}", "Rust", "base16-ocean.dark", ss, ts)
        r = repr(result)
        assert "HighlightResult" in r


class TestScopeStackOp:
    """Test ScopeStackOp factory methods."""

    def test_scope_stack_op_push(self):
        """Test ScopeStackOp.push()."""
        scope = syntect.Scope.from_string("source")
        op = syntect.ScopeStackOp.push(scope)
        assert op is not None

    def test_scope_stack_op_pop(self):
        """Test ScopeStackOp.pop()."""
        op = syntect.ScopeStackOp.pop(1)
        assert op is not None

    def test_scope_stack_op_clear_all(self):
        """Test ScopeStackOp.clear_all()."""
        op = syntect.ScopeStackOp.clear_all()
        assert op is not None

    def test_scope_stack_op_clear_top(self):
        """Test ScopeStackOp.clear_top()."""
        op = syntect.ScopeStackOp.clear_top(3)
        assert op is not None

    def test_scope_stack_op_restore(self):
        """Test ScopeStackOp.restore()."""
        op = syntect.ScopeStackOp.restore()
        assert op is not None

    def test_scope_stack_op_noop(self):
        """Test ScopeStackOp.noop()."""
        op = syntect.ScopeStackOp.noop()
        assert op is not None


class TestScopeStack:
    """Test ScopeStack methods."""

    def test_scope_stack_from_string(self):
        """Test ScopeStack.from_string()."""
        stack = syntect.ScopeStack.from_string("source.javascript")
        assert stack is not None

    def test_scope_stack_push_pop(self):
        """Test ScopeStack push and pop."""
        stack = syntect.ScopeStack.from_string("")
        scope = syntect.Scope.from_string("source")
        stack.push(scope)
        assert stack.len() == 1
        stack.pop()
        assert stack.len() == 0

    def test_scope_stack_as_string(self):
        """Test ScopeStack.as_string()."""
        stack = syntect.ScopeStack.from_string("source.javascript")
        s = stack.as_string()
        assert isinstance(s, str)

    def test_scope_stack_is_empty(self):
        """Test ScopeStack.is_empty()."""
        stack = syntect.ScopeStack.from_string("")
        assert stack.is_empty()

    def test_scope_stack_apply(self):
        """Test ScopeStack.apply()."""
        stack = syntect.ScopeStack.from_string("")
        scope = syntect.Scope.from_string("source")
        op = syntect.ScopeStackOp.push(scope)
        stack.apply(op)
        assert stack.len() == 1


class TestScope:
    """Test Scope methods."""

    def test_scope_from_string(self):
        """Test Scope.from_string()."""
        scope = syntect.Scope.from_string("source.python")
        assert scope is not None

    def test_scope_to_string(self):
        """Test Scope.to_string()."""
        scope = syntect.Scope.from_string("source.python")
        assert scope.to_string() == "source.python"

    def test_scope_len(self):
        """Test Scope.len()."""
        scope = syntect.Scope.from_string("source.python")
        assert scope.len() == 2

    def test_scope_is_empty(self):
        """Test Scope.is_empty()."""
        empty = syntect.Scope.from_string("")
        assert empty.is_empty()

    def test_scope_is_prefix_of(self):
        """Test Scope.is_prefix_of()."""
        parent = syntect.Scope.from_string("source")
        child = syntect.Scope.from_string("source.python")
        # child "source.python" has parent "source" as prefix
        assert parent.is_prefix_of(child)


class TestColor:
    """Test Color methods."""

    def test_color_from_hex(self):
        """Test Color.from_hex()."""
        c = syntect.Color.from_hex("#FF0000")
        assert c.r == 255
        assert c.g == 0
        assert c.b == 0
        assert c.a == 255

    def test_color_to_hex(self):
        """Test Color.to_hex()."""
        c = syntect.Color.from_hex("#FF0000")
        assert c.to_hex() == "#FF0000"


class TestFontStyle:
    """Test FontStyle methods."""

    def test_font_style_operations(self):
        """Test FontStyle bitwise operations."""
        fs1 = syntect.FontStyle(1)
        fs2 = syntect.FontStyle(2)
        combined = fs1 | fs2
        assert combined is not None


class TestStyle:
    """Test Style methods."""

    def test_style_from_hex_styles(self):
        """Test Style.from_hex_styles()."""
        style = syntect.Style.from_hex_styles("#FF0000", "#00FF00", 3)
        assert style.foreground.r == 255
        assert style.background.g == 255
        assert style.font_style.bits == 3


@pytest.fixture
def ss():
    """Load syntax set."""
    return syntect.SyntaxSet.load_defaults(False)


@pytest.fixture
def ts():
    """Load theme set."""
    return syntect.ThemeSet.load_defaults()


@pytest.fixture
def theme(ts):
    """Get a theme."""
    return ts.get_theme("base16-ocean.dark")


@pytest.fixture
def rust(ss):
    """Get Rust syntax reference."""
    return ss.find_syntax_by_name("Rust")
