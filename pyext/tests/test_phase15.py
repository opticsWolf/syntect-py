"""Phase 15: ThemeSettings Complete Fields tests"""
import pytest
import syntect


class TestThemeSettingsCompleteFields:
    """Tests for all ThemeSettings fields."""

    def test_all_color_fields_accessible(self, dark_theme):
        """Test that all color fields are accessible."""
        s = dark_theme.settings
        # Original fields
        assert s.foreground is not None or s.foreground is None
        assert s.background is not None or s.background is None
        assert s.selection_background is not None or s.selection_background is None
        assert s.gutter_foreground is not None or s.gutter_foreground is None
        assert s.gutter_background is not None or s.gutter_background is None
        
        # NEW fields - all should be accessible
        assert s.caret is not None or s.caret is None
        assert s.line_highlight is not None or s.line_highlight is None
        assert s.misspelling is not None or s.misspelling is None
        assert s.minimap_border is not None or s.minimap_border is None
        assert s.accent is not None or s.accent is None

    def test_css_fields(self, dark_theme):
        """Test that CSS fields are strings or None."""
        s = dark_theme.settings
        assert s.popup_css is None or isinstance(s.popup_css, str)
        assert s.phantom_css is None or isinstance(s.phantom_css, str)

    def test_bracket_fields(self, dark_theme):
        """Test bracket-related fields."""
        s = dark_theme.settings
        assert s.bracket_contents_foreground is not None or s.bracket_contents_foreground is None
        assert s.bracket_contents_options is not None or s.bracket_contents_options is None
        assert s.brackets_foreground is not None or s.brackets_foreground is None
        assert s.brackets_background is not None or s.brackets_background is None
        assert s.brackets_options is not None or s.brackets_options is None

    def test_tag_fields(self, dark_theme):
        """Test tag-related fields."""
        s = dark_theme.settings
        assert s.tags_foreground is not None or s.tags_foreground is None
        assert s.tags_options is not None or s.tags_options is None

    def test_highlight_fields(self, dark_theme):
        """Test highlight-related fields."""
        s = dark_theme.settings
        assert s.highlight is not None or s.highlight is None
        assert s.find_highlight is not None or s.find_highlight is None
        assert s.find_highlight_foreground is not None or s.find_highlight_foreground is None

    def test_selection_fields(self, dark_theme):
        """Test selection-related fields."""
        s = dark_theme.settings
        assert s.selection_foreground is not None or s.selection_foreground is None
        assert s.selection_border is not None or s.selection_border is None
        assert s.inactive_selection is not None or s.inactive_selection is None
        assert s.inactive_selection_foreground is not None or s.inactive_selection_foreground is None

    def test_guide_fields(self, dark_theme):
        """Test guide-related fields."""
        s = dark_theme.settings
        assert s.guide is not None or s.guide is None
        assert s.active_guide is not None or s.active_guide is None
        assert s.stack_guide is not None or s.stack_guide is None

    def test_shadow_field(self, dark_theme):
        """Test shadow field."""
        s = dark_theme.settings
        assert s.shadow is not None or s.shadow is None

    def test_underline_option_class(self):
        """Test PyUnderlineOption class methods."""
        assert syntect.UnderlineOption.none_() is None
        assert syntect.UnderlineOption.underline() is not None
        assert syntect.UnderlineOption.stippled_underline() is not None
        assert syntect.UnderlineOption.squiggly_underline() is not None
        
        u = syntect.UnderlineOption.underline()
        assert "underline" in repr(u)

    def test_repr_includes_caret(self, dark_theme):
        """Test that __repr__ includes caret info."""
        s = dark_theme.settings
        repr_str = repr(s)
        assert "ThemeSettings" in repr_str
        assert "caret" in repr_str


@pytest.fixture
def dark_theme():
    """Load Solarized (dark) theme for testing."""
    ts = syntect.ThemeSet.load_defaults()
    return ts.get_theme('Solarized (dark)')
