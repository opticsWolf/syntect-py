"""Phase 19: easy Module Bindings tests - HighlightLines"""
import pytest
import syntect


class TestHighlightLines:
    """Tests for HighlightLines class."""

    def test_create_highlight_lines(self, ss, ts):
        """Test creating a HighlightLines instance."""
        rust = ss.find_syntax_by_name("Rust")
        hl = syntect.HighlightLines(rust, ss, ts, "Solarized (dark)")
        assert hl is not None
        assert "HighlightLines" in repr(hl)

    def test_highlight_line(self, ss, ts):
        """Test highlighting a single line."""
        rust = ss.find_syntax_by_name("Rust")
        hl = syntect.HighlightLines(rust, ss, ts, "Solarized (dark)")
        tokens = hl.highlight_line("fn main()", ss)
        assert len(tokens) > 0
        for style, text in tokens:
            assert hasattr(style, 'foreground')
            assert hasattr(style, 'background')
            assert hasattr(style, 'font_style')

    def test_highlight_multiple_lines(self, ss, ts):
        """Test highlighting multiple lines with stateful highlighting."""
        rust = ss.find_syntax_by_name("Rust")
        hl = syntect.HighlightLines(rust, ss, ts, "Solarized (dark)")
        code = "fn main() {\n    let x = 1;\n}"
        for line in code.split("\n"):
            tokens = hl.highlight_line(line, ss)
            assert isinstance(tokens, list)

    def test_highlight_lines_stateful(self, ss, ts):
        """Test that HighlightLines maintains state across calls."""
        rust = ss.find_syntax_by_name("Rust")
        hl = syntect.HighlightLines(rust, ss, ts, "Solarized (dark)")

        # First line
        tokens1 = hl.highlight_line("fn main() {", ss)
        assert len(tokens1) > 0

        # Second line - state should be maintained
        tokens2 = hl.highlight_line("    let x = 1;", ss)
        assert len(tokens2) > 0

    def test_highlight_lines_vs_highlighter(self, ss, ts):
        """Test that HighlightLines produces same output as Highlighter."""
        rust = ss.find_syntax_by_name("Rust")
        theme = ts.get_theme("Solarized (dark)")
        hl_lines = syntect.HighlightLines(rust, ss, ts, "Solarized (dark)")
        hl = syntect.Highlighter(rust, theme)

        line = "fn main()"
        tokens_lines = hl_lines.highlight_line(line, ss)
        tokens_hl = hl.highlight_line(line, ss, ts)

        assert len(tokens_lines) == len(tokens_hl)
        for (s1, t1), (s2, t2) in zip(tokens_lines, tokens_hl):
            assert s1.foreground.r == s2.foreground.r
            assert s1.foreground.g == s2.foreground.g
            assert s1.foreground.b == s2.foreground.b
            assert t1 == t2

    def test_highlight_lines_error_handling(self, ss, ts):
        """Test error handling for non-existent theme."""
        rust = ss.find_syntax_by_name("Rust")
        with pytest.raises(ValueError):
            syntect.HighlightLines(rust, ss, ts, "NonExistentTheme")


@pytest.fixture
def ss():
    """Load syntax set."""
    return syntect.SyntaxSet.load_defaults(False)


@pytest.fixture
def ts():
    """Load theme set."""
    return syntect.ThemeSet.load_defaults()
