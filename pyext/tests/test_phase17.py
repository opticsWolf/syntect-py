"""Phase 17: util Module Bindings tests"""
import pytest
import syntect


class TestSplitAt:
    """Tests for split_at function."""

    def test_split_at_boundary(self):
        """Test splitting at exact token boundary."""
        style1 = syntect.Style.from_hex_styles('ff0000', '000000', 0)
        style2 = syntect.Style.from_hex_styles('00ff00', '000000', 0)
        tokens = [(style1, 'hello'), (style2, 'world')]
        left, right = syntect.split_at(tokens, 5)
        assert len(left) == 1
        assert left[0][1] == 'hello'
        assert len(right) == 1
        assert right[0][1] == 'world'

    def test_split_at_middle_of_token(self):
        """Test splitting in the middle of a token."""
        style1 = syntect.Style.from_hex_styles('ff0000', '000000', 0)
        style2 = syntect.Style.from_hex_styles('00ff00', '000000', 0)
        tokens = [(style1, 'hello'), (style2, 'world')]
        left, right = syntect.split_at(tokens, 3)
        assert len(left) == 1
        assert left[0][1] == 'hel'
        assert len(right) == 2
        assert right[0][1] == 'lo'
        assert right[1][1] == 'world'

    def test_split_at_zero(self):
        """Test splitting at position 0."""
        style1 = syntect.Style.from_hex_styles('ff0000', '000000', 0)
        tokens = [(style1, 'hello')]
        left, right = syntect.split_at(tokens, 0)
        assert len(left) == 0
        assert len(right) == 1
        assert right[0][1] == 'hello'

    def test_split_at_end(self):
        """Test splitting at the end of all tokens."""
        style1 = syntect.Style.from_hex_styles('ff0000', '000000', 0)
        tokens = [(style1, 'hello')]
        left, right = syntect.split_at(tokens, 5)
        assert len(left) == 1
        assert left[0][1] == 'hello'
        assert len(right) == 0

    def test_split_at_multi_token(self):
        """Test splitting across multiple tokens."""
        style1 = syntect.Style.from_hex_styles('ff0000', '000000', 0)
        style2 = syntect.Style.from_hex_styles('00ff00', '000000', 0)
        style3 = syntect.Style.from_hex_styles('0000ff', '000000', 0)
        tokens = [(style1, 'ab'), (style2, 'cd'), (style3, 'ef')]
        left, right = syntect.split_at(tokens, 4)
        assert len(left) == 2
        assert left[0][1] == 'ab'
        assert left[1][1] == 'cd'
        assert len(right) == 1
        assert right[0][1] == 'ef'


class TestModifyRange:
    """Tests for modify_range function."""

    def test_modify_range_full_token(self):
        """Test replacing style of a full token."""
        style1 = syntect.Style.from_hex_styles('ff0000', '000000', 0)
        style2 = syntect.Style.from_hex_styles('00ff00', '000000', 0)
        new_style = syntect.Style.from_hex_styles('0000ff', '000000', 0)
        tokens = [(style1, 'hello'), (style2, 'world')]
        modified = syntect.modify_range(tokens, 0, 5, new_style)
        # Full token 'hello' should be replaced, 'world' unchanged
        assert len(modified) == 2
        assert modified[0][1] == 'hello'
        assert modified[0][0].foreground.r == 0
        assert modified[0][0].foreground.g == 0
        assert modified[0][0].foreground.b == 255
        assert modified[1][1] == 'world'
        assert modified[1][0].foreground.g == 255

    def test_modify_range_partial_token(self):
        """Test replacing style in the middle of a token."""
        style1 = syntect.Style.from_hex_styles('ff0000', '000000', 0)
        new_style = syntect.Style.from_hex_styles('0000ff', '000000', 0)
        tokens = [(style1, 'hello')]
        modified = syntect.modify_range(tokens, 1, 4, new_style)
        assert len(modified) == 3
        assert modified[0][1] == 'h'
        assert modified[1][1] == 'ell'
        assert modified[2][1] == 'o'
        assert modified[1][0].foreground.r == 0
        assert modified[1][0].foreground.b == 255

    def test_modify_range_empty_range(self):
        """Test modifying a zero-length range (splits at position)."""
        style1 = syntect.Style.from_hex_styles('ff0000', '000000', 0)
        new_style = syntect.Style.from_hex_styles('0000ff', '000000', 0)
        tokens = [(style1, 'hello')]
        modified = syntect.modify_range(tokens, 2, 2, new_style)
        # Zero-length range splits at position 2, creating two tokens
        assert len(modified) == 2
        assert modified[0][1] == 'he'
        assert modified[1][1] == 'llo'


class TestLinesWithEndings:
    """Tests for lines_with_endings function."""

    def test_basic_lines(self):
        """Test basic line splitting with newlines."""
        result = list(syntect.lines_with_endings('hello\nworld\n'))
        assert len(result) == 2
        assert result[0] == ('hello', '\n')
        assert result[1] == ('world', '\n')

    def test_last_line_no_newline(self):
        """Test that last line without newline still returns."""
        result = list(syntect.lines_with_endings('hello\nworld'))
        assert len(result) == 2
        assert result[0] == ('hello', '\n')
        assert result[1] == ('world', '')

    def test_crlf_endings(self):
        """Test CRLF line endings."""
        result = list(syntect.lines_with_endings('a\r\nb\r\nc'))
        assert len(result) == 3
        assert result[0] == ('a', '\r\n')
        assert result[1] == ('b', '\r\n')
        assert result[2] == ('c', '')

    def test_single_line_no_newline(self):
        """Test single line with no newline."""
        result = list(syntect.lines_with_endings('hello'))
        assert len(result) == 1
        assert result[0] == ('hello', '')

    def test_empty_string(self):
        """Test empty string."""
        result = list(syntect.lines_with_endings(''))
        assert len(result) == 0

    def test_only_newlines(self):
        """Test string with only newlines."""
        result = list(syntect.lines_with_endings('\n\n'))
        assert len(result) == 2
        assert result[0] == ('', '\n')
        assert result[1] == ('', '\n')

    def test_iterator_protocol(self):
        """Test that LinesWithEndings supports iteration protocol."""
        lines = syntect.lines_with_endings('a\nb\nc\n')
        # Should be iterable
        count = 0
        for line, ending in lines:
            count += 1
        assert count == 3


class TestIntegration:
    """Integration tests for util functions."""

    def test_split_and_modify(self):
        """Test combining split_at and modify_range."""
        style1 = syntect.Style.from_hex_styles('ff0000', '000000', 0)
        style2 = syntect.Style.from_hex_styles('00ff00', '000000', 0)
        tokens = [(style1, 'hello'), (style2, 'world')]

        # Split in middle
        left, right = syntect.split_at(tokens, 3)
        assert left[0][1] == 'hel'
        assert right[0][1] == 'lo'

        # Modify range in left
        new_style = syntect.Style.from_hex_styles('0000ff', '000000', 0)
        modified_left = syntect.modify_range(left, 0, 3, new_style)
        assert modified_left[0][1] == 'hel'
        assert modified_left[0][0].foreground.b == 255

    def test_lines_with_endings_integration(self):
        """Test lines_with_endings with actual highlighting."""
        ss = syntect.SyntaxSet.load_defaults(False)
        ts = syntect.ThemeSet.load_defaults()
        theme = ts.get_theme("Solarized (dark)")
        hl = syntect.Highlighter(ss.find_syntax_by_name("Rust"), theme)

        # Use lines_with_endings to iterate
        code = "fn main() {\n    let x = 1;\n}"
        for line, ending in syntect.lines_with_endings(code):
            tokens = hl.highlight_line(line, ss, ts)
            # Should not raise
            assert isinstance(tokens, list)
