"""Phase 18: html Module Bindings tests"""
import pytest
import syntect


class TestClassedHTMLGenerator:
    """Tests for ClassedHTMLGenerator class."""

    def test_create_generator(self, ss, rust, theme):
        """Test creating a ClassedHTMLGenerator."""
        cs = syntect.ClassStyle.spaced_prefixed("syn-")
        gen = syntect.ClassedHTMLGenerator(rust, ss, cs)
        assert gen is not None
        assert "ClassedHTMLGenerator" in repr(gen)

    def test_parse_html_for_line(self, ss, rust, theme):
        """Test parsing HTML for a line of code."""
        cs = syntect.ClassStyle.spaced_prefixed("syn-")
        gen = syntect.ClassedHTMLGenerator(rust, ss, cs)
        gen.parse_html_for_line_which_includes_newline("fn main() {")
        html = gen.finalize()
        assert "syn-keyword" in html or "syn-function" in html

    def test_parse_multiple_lines(self, ss, rust, theme):
        """Test parsing multiple lines."""
        cs = syntect.ClassStyle.spaced_prefixed("syn-")
        gen = syntect.ClassedHTMLGenerator(rust, ss, cs)
        code = "fn main() {\n    let x = 1;\n}"
        for line in code.split("\n"):
            gen.parse_html_for_line_which_includes_newline(line)
        html = gen.finalize()
        assert len(html) > 100  # Should have substantial HTML output

    def test_classed_vs_inline_html(self, ss, rust, theme, hl, ts):
        """Test that classed HTML is different from inline HTML."""
        cs = syntect.ClassStyle.spaced_prefixed("syn-")
        gen = syntect.ClassedHTMLGenerator(rust, ss, cs)
        gen.parse_html_for_line_which_includes_newline("fn main()")
        classed_html = gen.finalize()

        tokens = hl.highlight_line("fn main()", ss, ts)
        inline_html = syntect.styled_line_to_highlighted_html(tokens, "no")

        assert "class=" in classed_html
        assert "style=" in inline_html


class TestTokensToClassedSpans:
    """Tests for tokens_to_classed_spans function."""

    def test_basic_conversion(self, ss, rust, theme, hl, ts):
        """Test converting tokens to classed spans."""
        cs = syntect.ClassStyle.spaced_prefixed("syn-")
        tokens = hl.highlight_line("fn main()", ss, ts)
        html = syntect.tokens_to_classed_spans(tokens, cs)
        assert "class=" in html
        assert len(html) > 0

    def test_different_class_styles(self, ss, rust, theme, hl, ts):
        """Test with different class styles."""
        tokens = hl.highlight_line("fn main()", ss, ts)
        
        # Spaced style
        cs_spaced = syntect.ClassStyle.spaced()
        html_spaced = syntect.tokens_to_classed_spans(tokens, cs_spaced)
        assert "class=" in html_spaced
        
        # Spaced prefixed style
        cs_prefix = syntect.ClassStyle.spaced_prefixed("my-")
        html_prefix = syntect.tokens_to_classed_spans(tokens, cs_prefix)
        assert "my-" in html_prefix


class TestLineTokensToClassedSpans:
    """Tests for line_tokens_to_classed_spans_py function."""

    def test_basic_conversion(self, ss, rust, theme):
        """Test converting line and ops to classed spans."""
        cs = syntect.ClassStyle.spaced_prefixed("syn-")
        ops = [(0, "Push"), (5, "Push"), (8, "Pop")]
        html, delta = syntect.line_tokens_to_classed_spans_py("fn main()", ops, cs)
        assert "class=" in html
        assert isinstance(delta, int)

    def test_span_delta_tracking(self, ss, rust, theme):
        """Test that span delta correctly tracks open/close spans."""
        cs = syntect.ClassStyle.spaced_prefixed("syn-")
        # Push two scopes, pop one
        ops = [(0, "Push"), (3, "Push"), (6, "Pop")]
        html, delta = syntect.line_tokens_to_classed_spans_py("abc def ghi", ops, cs)
        # Should have net +1 open spans
        assert delta == 1


class TestStyledLineToHighlightedHtml:
    """Tests for styled_line_to_highlighted_html function."""

    def test_basic_conversion(self, ss, rust, theme, hl, ts):
        """Test converting styled tokens to inline HTML."""
        tokens = hl.highlight_line("fn main()", ss, ts)
        html = syntect.styled_line_to_highlighted_html(tokens, "no")
        assert "<span" in html
        assert "style=" in html

    def test_with_background(self, ss, rust, theme, hl, ts):
        """Test with background color included."""
        tokens = hl.highlight_line("fn main()", ss, ts)
        html = syntect.styled_line_to_highlighted_html(tokens, "yes")
        assert "background-color" in html

    def test_if_different(self, ss, rust, theme, hl, ts):
        """Test with if_different background policy."""
        tokens = hl.highlight_line("fn main()", ss, ts)
        html = syntect.styled_line_to_highlighted_html(tokens, "if_different")
        assert "<span" in html


@pytest.fixture
def ss():
    """Load syntax set."""
    return syntect.SyntaxSet.load_defaults(False)


@pytest.fixture
def rust(ss):
    """Find Rust syntax."""
    return ss.find_syntax_by_name("Rust")


@pytest.fixture
def theme_set():
    """Load theme set."""
    return syntect.ThemeSet.load_defaults()


@pytest.fixture
def theme(theme_set):
    """Get Solarized dark theme."""
    return theme_set.get_theme("Solarized (dark)")


@pytest.fixture
def hl(rust, theme):
    """Create highlighter."""
    return syntect.Highlighter(rust, theme)


@pytest.fixture
def ts(theme_set):
    """Alias for theme_set."""
    return theme_set
