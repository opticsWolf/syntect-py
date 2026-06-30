import pytest
import syntect


@pytest.fixture
def ss():
    return syntect.SyntaxSet.load_defaults(True)


@pytest.fixture
def ts():
    return syntect.ThemeSet.load_defaults()


@pytest.fixture
def theme(ts):
    return ts.get_theme('base16-ocean.dark')


@pytest.fixture
def rust(ss):
    return ss.find_syntax_by_name('Rust')


"""Phase 12: HighlightState Real Implementation tests"""
import pytest
import syntect


class TestHighlightStateReal:
    """Tests for the real HighlightState implementation."""

    def test_save_state_returns_non_empty_path(self, ss, ts, theme, rust):
        """Test that save_state returns a state with non-empty path_scope_string."""
        hl = syntect.Highlighter(rust, theme)
        state = hl.save_state(ss, ts)
        
        assert state is not None
        path = state.path_scope_string
        assert path is not None
        assert len(path) > 0
        assert "source.rust" in path

    def test_save_state_returns_styles(self, ss, ts, theme, rust):
        """Test that save_state returns a state with styles."""
        hl = syntect.Highlighter(rust, theme)
        state = hl.save_state(ss, ts)
        
        assert state is not None
        assert state.styles_count >= 1  # At least the default style

    def test_highlight_state_repr(self, ss, ts, theme, rust):
        """Test that HighlightState repr shows meaningful data."""
        hl = syntect.Highlighter(rust, theme)
        state = hl.save_state(ss, ts)
        
        repr_str = repr(state)
        assert "HighlightState" in repr_str
        assert "source.rust" in repr_str

    def test_highlight_state_path_scope_stack(self, ss, ts, theme, rust):
        """Test that path_scope_stack returns a list of Scope objects."""
        hl = syntect.Highlighter(rust, theme)
        state = hl.save_state(ss, ts)
        
        stack = state.path_scope_stack
        assert isinstance(stack, list)
        assert len(stack) >= 1
        # Each item should be a Scope
        for scope in stack:
            assert hasattr(scope, 'to_string')
            assert hasattr(scope, 'len')

    def test_highlight_state_styles_stack(self, ss, ts, theme, rust):
        """Test that styles_stack returns a list of Style objects."""
        hl = syntect.Highlighter(rust, theme)
        state = hl.save_state(ss, ts)
        
        styles = state.styles_stack
        assert isinstance(styles, list)
        assert len(styles) >= 1
        # Each item should have foreground, background, font_style
        for style in styles:
            assert hasattr(style, 'foreground')
            assert hasattr(style, 'background')
            assert hasattr(style, 'font_style')

    def test_highlight_state_default_constructor(self):
        """Test that HighlightState can be constructed with default constructor."""
        state = syntect.HighlightState()
        assert state.path_scope_string == ""
        assert state.styles_count == 0

    def test_from_state_creates_highlighter(self, ss, ts, theme, rust):
        """Test that from_state creates a highlighter with the theme."""
        hl = syntect.Highlighter(rust, theme)
        state = hl.save_state(ss, ts)
        
        hl2 = syntect.Highlighter.from_state(state, theme)
        assert hl2 is not None
        # The highlighter should have the theme name
        assert "theme" in repr(hl2)


class TestHighlightStateWithHighlighting:
    """Tests that verify HighlightState works with actual highlighting."""

    def test_state_after_highlight_line(self, ss, ts, theme, rust):
        """Test that state reflects the highlighting context."""
        hl = syntect.Highlighter(rust, theme)
        
        # Highlight a line that opens a block
        tokens = hl.highlight_line("fn main() {", ss, ts)
        
        # Save state after highlighting
        state = hl.save_state(ss, ts)
        
        # The path should contain source.rust
        assert "source.rust" in state.path_scope_string
        assert state.styles_count >= 1

    def test_state_after_multiple_lines(self, ss, ts, theme, rust):
        """Test that state can be saved after multiple highlight_line calls."""
        hl = syntect.Highlighter(rust, theme)
        
        # Highlight multiple lines
        hl.highlight_line("fn main() {", ss, ts)
        hl.highlight_line("    let x = 42;", ss, ts)
        hl.highlight_line("}", ss, ts)
        
        # Save state
        state = hl.save_state(ss, ts)
        
        assert state is not None
        assert len(state.path_scope_string) > 0
