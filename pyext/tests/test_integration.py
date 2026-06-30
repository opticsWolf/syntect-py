"""Integration tests for syntect-py."""
import pytest
import syntect
import tempfile
import os


class TestIntegration:
    """Integration tests that verify end-to-end functionality."""

    @pytest.fixture
    def ss(self):
        return syntect.SyntaxSet.load_defaults(True)

    @pytest.fixture
    def ts(self):
        return syntect.ThemeSet.load_defaults()

    @pytest.fixture
    def theme(self, ts):
        return ts.get_theme('base16-ocean.dark')

    @pytest.fixture
    def rust(self, ss):
        return ss.find_syntax_by_name('Rust')

    def test_highlight_string_full_pipeline(self, ss, ts, theme, rust):
        """Test the full highlight_string pipeline."""
        code = 'fn main() {}'
        result = syntect.highlight_string(code, 'Rust', 'base16-ocean.dark', ss, ts)
        
        assert len(result.tokens) > 0
        assert len(result.html) > 0
        assert '<pre' in result.html
        assert chr(0x1b) in result.terminal_escaped

    def test_highlight_file(self, ss, ts, theme, rust):
        """Test highlighting a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
            f.write('fn main() {\n    let x = 42;\n}\n')
            temp_path = f.name
        
        try:
            hl = syntect.Highlighter(rust, theme)
            tokens = hl.highlight_file(temp_path, ss, ts)
            assert len(tokens) >= 3  # at least 3 lines (may have trailing empty line)
        finally:
            os.unlink(temp_path)

    def test_css_generation(self, theme):
        """Test CSS generation with different styles."""
        for style in ['spaced', 'spaced_prefixed', 'class_attribute']:
            css = syntect.css_for_theme(theme, style)
            assert len(css) > 0
            assert 'color:' in css

    def test_generate_css_alias(self, theme):
        """Test the generate_css alias."""
        css = syntect.generate_css(theme, 'spaced')
        assert len(css) > 0

    def test_create_html_file_alias(self, ss, ts, theme, rust):
        """Test the create_html_file alias."""
        html = syntect.create_html_file('fn main() {}', rust, theme, ss, ts)
        assert len(html) > 0
        assert '<pre' in html

    def test_dump_roundtrip_syntax(self, ss):
        """Test SyntaxSet dump/load roundtrip."""
        with tempfile.NamedTemporaryFile(suffix='.packdump', delete=False) as f:
            dump_path = f.name
        
        try:
            ss.to_dump(dump_path)
            ss2 = syntect.SyntaxSet.from_dump(dump_path)
            assert len(ss2.syntaxes()) == len(ss.syntaxes())
        finally:
            os.unlink(dump_path)

    def test_dump_roundtrip_theme(self, ts):
        """Test ThemeSet dump/load roundtrip."""
        with tempfile.NamedTemporaryFile(suffix='.themedump', delete=False) as f:
            dump_path = f.name
        
        try:
            ts.to_dump(dump_path)
            ts2 = syntect.ThemeSet.from_dump(dump_path)
            assert len(ts2.theme_names()) == len(ts.theme_names())
        finally:
            os.unlink(dump_path)

    def test_theme_item_style(self, theme):
        """Test ThemeItem.style returns StyleModifier."""
        item = theme.scopes[0]
        style = item.style
        assert isinstance(style, syntect.StyleModifier)
        assert style.foreground is not None or style.background is not None

    def test_theme_settings_colors(self, theme):
        """Test ThemeSettings returns Color objects."""
        settings = theme.settings
        assert settings.foreground is not None
        assert settings.background is not None
        assert isinstance(settings.foreground, syntect.Color)
        assert isinstance(settings.background, syntect.Color)

    def test_parse_line_output(self, ss):
        """Test ParseLineOutput with ScopeStackOp objects."""
        parse_state = syntect.ParseState('Rust', ss)
        output = parse_state.parse_line('fn main() {', ss)
        
        assert len(output.ops) > 0
        assert len(output.warnings) >= 0
        
        # Test get_scope_stack_op
        if len(output.ops) > 0:
            op = output.get_scope_stack_op(0)
            assert op is not None
            op_type = output.get_op_type(0)
            assert op_type in ['Push', 'Pop', 'Clear', 'Restore', 'Noop']

    def test_all_output_formats(self, ss, ts, theme, rust):
        """Test all output formats produce valid output."""
        code = 'fn main() {}'
        
        # Get tokens
        hl = syntect.Highlighter(rust, theme)
        tokens = hl.highlight_line(code, ss, ts)
        assert len(tokens) > 0
        
        # Terminal
        escaped = syntect.as_terminal_escaped(tokens, True)
        assert chr(0x1b) in escaped
        
        # HTML
        html = syntect.as_html(tokens, 'if_different', None)
        assert '<span' in html
        
        # LaTeX
        latex = syntect.as_latex_escaped(tokens)
        assert '\\textcolor' in latex

    def test_file_extension_detection(self, ss):
        """Test syntax detection from file extensions."""
        with tempfile.NamedTemporaryFile(suffix='.rs', delete=False, mode='w') as f:
            f.write('test')
            rs_path = f.name
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write('test')
            py_path = f.name
        
        try:
            rust = ss.find_syntax_for_file(rs_path)
            python = ss.find_syntax_for_file(py_path)
            assert rust is not None
            assert python is not None
            assert rust.name == 'Rust'
            assert python.name == 'Python'
        finally:
            os.unlink(rs_path)
            os.unlink(py_path)

    def test_style_equality(self):
        """Test Style equality."""
        s1 = syntect.Style.from_hex_styles('#FF0000', '#000000', 0)
        s2 = syntect.Style.from_hex_styles('#FF0000', '#000000', 0)
        s3 = syntect.Style.from_hex_styles('#00FF00', '#000000', 0)
        
        assert s1 == s2
        assert s1 != s3

    def test_font_style_bitwise(self):
        """Test FontStyle bitwise operations."""
        bold = syntect.FontStyle.BOLD
        italic = syntect.FontStyle.ITALIC
        
        combined = bold | italic
        assert combined.bits == 5
        
        intersection = bold & italic
        assert intersection.bits == 0
        
        xor = bold ^ italic
        assert xor.bits == 5
