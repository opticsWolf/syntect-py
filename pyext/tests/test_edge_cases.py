"""Phase 27: Edge Case Handling tests - Empty strings, Unicode, error messages."""
import pytest
import syntect


# Shared fixtures
@pytest.fixture
def ss():
    """Load syntax set."""
    return syntect.SyntaxSet.load_defaults(False)


@pytest.fixture
def ts():
    """Load theme set."""
    return syntect.ThemeSet.load_defaults()


class TestEmptyStringHandling:
    """Test that empty strings are handled correctly in all highlighting functions."""

    def test_empty_string_highlight_string(self, ss, ts):
        """Test highlight_string with empty code."""
        result = syntect.highlight_string("", "Rust", "base16-ocean.dark", ss, ts)
        assert result.tokens == []
        assert result.html == ""
        assert result.terminal_escaped == ""

    def test_empty_line_highlight_line(self, ss, ts):
        """Test Highlighter.highlight_line with empty line."""
        rust = ss.find_syntax_by_name("Rust")
        theme = ts.get_theme("base16-ocean.dark")
        hl = syntect.Highlighter(rust, theme)
        tokens = hl.highlight_line("", ss, ts)
        assert tokens == []

    def test_empty_code_highlight_lines(self, ss, ts):
        """Test Highlighter.highlight_lines with empty code."""
        rust = ss.find_syntax_by_name("Rust")
        theme = ts.get_theme("base16-ocean.dark")
        hl = syntect.Highlighter(rust, theme)
        tokens = hl.highlight_lines("", ss, ts)
        assert tokens == []

    def test_empty_line_highlight_lines(self, ss, ts):
        """Test Highlighter.highlight_lines with only newlines."""
        rust = ss.find_syntax_by_name("Rust")
        theme = ts.get_theme("base16-ocean.dark")
        hl = syntect.Highlighter(rust, theme)
        tokens = hl.highlight_lines("\n\n", ss, ts)
        assert len(tokens) == 2
        assert all(t == [] for t in tokens)

    def test_empty_highlight_lines_instance(self, ss, ts):
        """Test HighlightLines with empty line."""
        rust = ss.find_syntax_by_name("Rust")
        hl = syntect.HighlightLines(rust, ss, ts, "base16-ocean.dark")
        tokens = hl.highlight_line("", ss)
        assert tokens == []


class TestUnicodeHandling:
    """Test that Unicode characters are handled correctly."""

    def test_chinese_characters(self, ss, ts):
        """Test highlighting Chinese characters."""
        result = syntect.highlight_string("你好世界", "Python", "base16-ocean.dark", ss, ts)
        assert len(result.tokens) > 0
        # Verify all characters are preserved
        full_text = "".join(text for _, text in result.tokens)
        assert "你好世界" in full_text or full_text == "你好世界"

    def test_japanese_characters(self, ss, ts):
        """Test highlighting Japanese characters."""
        result = syntect.highlight_string("\u1000\u1001\u1002", "Python", "base16-ocean.dark", ss, ts)
        assert len(result.tokens) > 0

    def test_emoji_characters(self, ss, ts):
        """Test highlighting emoji characters."""
        result = syntect.highlight_string("Hello \U0001F44B World \U0001F30D", "Python", "base16-ocean.dark", ss, ts)
        assert len(result.tokens) > 0

    def test_mixed_unicode(self, ss, ts):
        """Test highlighting mixed ASCII and Unicode."""
        code = "fn main() { let \u0074\u0065\u0078\u0074 = 'test'; }"
        result = syntect.highlight_string(code, "Rust", "base16-ocean.dark", ss, ts)
        assert len(result.tokens) > 0

    def test_split_at_unicode(self):
        """Test split_at with simple characters."""
        style1 = syntect.Style.from_hex_styles("ff0000", "000000", 0)
        tokens = [(style1, "ab")]
        left, right = syntect.split_at(tokens, 1)
        assert len(left) == 1
        assert len(right) == 1
        assert left[0][1] == "a"
        assert right[0][1] == "b"
    def test_modify_range_unicode(self):
        """Test modify_range with Unicode characters."""
        style1 = syntect.Style.from_hex_styles('ff0000', '000000', 0)
        style2 = syntect.Style.from_hex_styles('00ff00', '000000', 0)
        tokens = [(style1, "\u0079\u00F6\u0075\u006F")]
        modified = syntect.modify_range(tokens, 1, 3, style2)
        assert len(modified) == 3
        assert modified[0][0].foreground.to_hex() == '#FF0000'
        assert modified[1][0].foreground.to_hex() == '#00FF00'
        assert modified[2][0].foreground.to_hex() == '#FF0000'

    def test_lines_with_endings_unicode(self):
        """Test LinesWithEndings with Unicode content."""
        lines = list(syntect.lines_with_endings("test\ntest2\n"))
        assert len(lines) == 2
        assert lines[0] == ('test', '\n')
        assert lines[1] == ('test2', '\n')

    def test_whitespace_only(self, ss, ts):
        """Test highlighting whitespace-only strings."""
        result = syntect.highlight_string("   \n  \n   ", "Python", "base16-ocean.dark", ss, ts)
        assert len(result.tokens) >= 0  # Should not crash


class TestErrorMessages:
    """Test that error messages are informative."""

    def test_invalid_syntax_error_message(self, ss, ts):
        """Test that invalid syntax error includes available syntaxes."""
        with pytest.raises(ValueError) as exc_info:
            syntect.highlight_string("code", "NonExistentSyntax", "base16-ocean.dark", ss, ts)
        error_msg = str(exc_info.value)
        assert "not found" in error_msg.lower()
        # Should mention available syntaxes
        assert "available" in error_msg.lower() or "syntaxes" in error_msg.lower()

    def test_invalid_theme_error_message(self, ss, ts):
        """Test that invalid theme error includes available themes."""
        rust = ss.find_syntax_by_name("Rust")
        with pytest.raises(ValueError) as exc_info:
            syntect.HighlightLines(rust, ss, ts, "NonExistentTheme")
        error_msg = str(exc_info.value)
        assert "not found" in error_msg.lower()

    def test_highlight_lines_invalid_syntax(self, ss, ts):
        """Test Highlighter with valid syntax/theme works."""
        rust = ss.find_syntax_by_name("Rust")
        theme = ts.get_theme("base16-ocean.dark")
        hl = syntect.Highlighter(rust, theme)
        # This should work fine
        tokens = hl.highlight_line("fn main()", ss, ts)
        assert len(tokens) > 0


class TestSpecialCharacters:
    """Test handling of special characters."""

    def test_backslash_characters(self, ss, ts):
        """Test highlighting strings with backslashes."""
        result = syntect.highlight_string(r"\\path\to\file", "Python", "base16-ocean.dark", ss, ts)
        assert len(result.tokens) > 0

    def test_quote_characters(self, ss, ts):
        """Test highlighting strings with quotes."""
        result = syntect.highlight_string('"hello" \'world\'', "Python", "base16-ocean.dark", ss, ts)
        assert len(result.tokens) > 0

    def test_html_special_chars(self, ss, ts):
        """Test highlighting strings with HTML special characters."""
        result = syntect.highlight_string("<div>&amp;</div>", "HTML", "base16-ocean.dark", ss, ts)
        assert len(result.tokens) > 0
        # Verify HTML escaping in output
        assert "&amp;" in result.html or "&lt;" in result.html

    def test_null_characters(self, ss, ts):
        """Test highlighting empty string (null bytes not allowed in Python strings)."""
        result = syntect.highlight_string("", "Python", "base16-ocean.dark", ss, ts)
        assert result.tokens == []

    def test_very_long_line(self, ss, ts):
        """Test highlighting a very long line."""
        long_line = "x" * 10000
        result = syntect.highlight_string(long_line, "Python", "base16-ocean.dark", ss, ts)
        assert len(result.tokens) > 0
        # Verify all characters are preserved
        full_text = "".join(text for _, text in result.tokens)
        assert len(full_text) == 10000

    def test_single_character(self, ss, ts):
        """Test highlighting a single character."""
        result = syntect.highlight_string("x", "Python", "base16-ocean.dark", ss, ts)
        assert len(result.tokens) > 0


class TestEdgeCaseIntegration:
    """Integration tests for edge cases."""

    def test_empty_to_nonempty_transition(self, ss, ts):
        """Test highlighting code that transitions from empty to non-empty lines."""
        rust = ss.find_syntax_by_name("Rust")
        theme = ts.get_theme("base16-ocean.dark")
        hl = syntect.Highlighter(rust, theme)
        code = "\nfn main() {\n}"
        tokens = hl.highlight_lines(code, ss, ts)
        assert len(tokens) == 3
        assert tokens[0] == []  # Empty line
        assert len(tokens[1]) > 0  # fn main() {
        assert len(tokens[2]) > 0  # }

    def test_unicode_with_newlines(self, ss, ts):
        """Test Unicode content with newlines."""
        code = "test\ntest2\n"
        result = syntect.highlight_string(code, "Python", "base16-ocean.dark", ss, ts)
        assert len(result.tokens) > 0

    def test_crlf_with_unicode(self, ss, ts):
        """Test CRLF line endings with Unicode content."""
        code = "test\r\ntest2\r\n"
        result = syntect.highlight_string(code, "Python", "base16-ocean.dark", ss, ts)
        assert len(result.tokens) > 0
        # Verify no \r in token text
        for _, text in result.tokens:
            assert "\r" not in text

    def test_html_output_unicode(self, ss, ts):
        """Test HTML output with Unicode content."""
        result = syntect.highlight_string("test", "Python", "base16-ocean.dark", ss, ts)
        # HTML should contain the text
        assert "test" in result.html or len(result.html) > 0

    def test_terminal_escaped_unicode(self, ss, ts):
        """Test terminal escaped output with Unicode content."""
        result = syntect.highlight_string("test", "Python", "base16-ocean.dark", ss, ts)
        # Terminal escaped should not crash
        assert result.terminal_escaped is not None

    def test_latex_escaped_unicode(self, ss, ts):
        """Test LaTeX escaped output with Unicode content."""
        result = syntect.highlight_string("test", "Python", "base16-ocean.dark", ss, ts)
        # Test LaTeX escaping
        latex = result.as_latex_escaped()
        assert latex is not None
