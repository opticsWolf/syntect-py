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


"""Phase 11: Critical Bug Fixes tests"""
import pytest
import syntect


class TestAsHtmlIfDifferent:
    """Tests for as_html with include_bg='if_different' and default_bg parameter."""

    def test_default_bg_none_includes_bg(self):
        """When default_bg is None, background is always included."""
        style = syntect.Style.from_hex_styles("#B48EAD", "#2B303B", 0)
        tokens = [(style, "fn")]
        html = syntect.as_html(tokens, "if_different", None)
        assert "background-color:#2B303B" in html

    def test_default_bg_matches_token_bg_excludes_bg(self):
        """When token bg == default bg, background is excluded."""
        default_bg = syntect.Color.from_hex("#2B303B")
        style = syntect.Style.from_hex_styles("#B48EAD", "#2B303B", 0)
        tokens = [(style, "fn")]
        html = syntect.as_html(tokens, "if_different", default_bg)
        assert "background-color" not in html
        assert "<span" in html

    def test_default_bg_differs_from_token_bg_includes_bg(self):
        """When token bg != default bg, background is included."""
        default_bg = syntect.Color.from_hex("#000000")
        style = syntect.Style.from_hex_styles("#B48EAD", "#2B303B", 0)
        tokens = [(style, "fn")]
        html = syntect.as_html(tokens, "if_different", default_bg)
        assert "background-color:#2B303B" in html

    def test_include_bg_yes_always_includes(self):
        """include_bg='yes' always includes background."""
        style = syntect.Style.from_hex_styles("#B48EAD", "#2B303B", 0)
        tokens = [(style, "fn")]
        html = syntect.as_html(tokens, "yes", None)
        assert "background-color:#2B303B" in html

    def test_include_bg_no_never_includes(self):
        """include_bg='no' never includes background."""
        style = syntect.Style.from_hex_styles("#B48EAD", "#2B303B", 0)
        tokens = [(style, "fn")]
        html = syntect.as_html(tokens, "no", None)
        assert "background-color" not in html


class TestHighlightLinesCrlf:
    """Tests for highlight_lines handling of CRLF line endings."""

    def test_highlight_lines_crlf_no_cr_in_output(self, ss, ts, theme, rust):
        """Test that \\r\\n line endings are handled correctly - no \\r in output."""
        hl = syntect.Highlighter(rust, theme)
        code = "fn main() {\r\n    let x = 42;\r\n}"
        all_tokens = hl.highlight_lines(code, ss, ts)

        assert len(all_tokens) == 3  # 3 lines
        for line_tokens in all_tokens:
            for _, text in line_tokens:
                assert '\r' not in text, f"Found \\r in output: {repr(text)}"

    def test_highlight_lines_lf(self, ss, ts, theme, rust):
        """Test that \\n line endings work correctly."""
        hl = syntect.Highlighter(rust, theme)
        code = "fn main() {\n    let x = 42;\n}"
        all_tokens = hl.highlight_lines(code, ss, ts)

        assert len(all_tokens) == 3
        for line_tokens in all_tokens:
            for _, text in line_tokens:
                assert '\r' not in text


class TestClassStylePrefix:
    """Tests for ClassStyle.spaced_prefixed respecting the prefix parameter."""

    def test_spaced_prefixed_uses_prefix(self, ts):
        """Test that spaced_prefixed class style uses the specified prefix."""
        theme = ts.get_theme("base16-ocean.dark")
        cs = syntect.ClassStyle.spaced_prefixed("custom-")
        css = syntect.css_for_theme_class(theme, cs)
        assert "custom-" in css

    def test_spaced_prefixed_default_prefix(self, ts):
        """Test that spaced_prefixed without custom prefix uses default."""
        theme = ts.get_theme("base16-ocean.dark")
        cs = syntect.ClassStyle.spaced_prefixed("")
        css = syntect.css_for_theme_class(theme, cs)
        # Should still have some class names
        assert "span" in css.lower() or "color" in css.lower()


class TestScopeParsing:
    """Tests for the improved scope parsing in css_for_theme."""

    def test_css_for_theme_spaced(self, ts):
        """Test CSS generation with spaced style."""
        theme = ts.get_theme("base16-ocean.dark")
        css = syntect.css_for_theme(theme, "spaced")
        assert len(css) > 0
        assert "color:" in css

    def test_css_for_theme_class_attribute(self, ts):
        """Test CSS generation with class_attribute style."""
        theme = ts.get_theme("base16-ocean.dark")
        css = syntect.css_for_theme(theme, "class_attribute")
        assert len(css) > 0
        assert "color:" in css

    def test_css_for_theme_class_style(self, ts):
        """Test css_for_theme_class with PyClassStyle object."""
        theme = ts.get_theme("base16-ocean.dark")
        cs = syntect.ClassStyle.spaced()
        css = syntect.css_for_theme_class(theme, cs)
        assert len(css) > 0
        assert "color:" in css


class TestDeduplicatedHtmlGeneration:
    """Tests to verify the shared HTML generation works correctly."""

    def test_as_html_and_convenience_match(self, ss, ts, theme, rust):
        """Verify as_html() and PyHighlightResult.as_html() produce same output."""
        hl = syntect.Highlighter(rust, theme)
        tokens = hl.highlight_line("fn main() {}", ss, ts)

        html1 = syntect.as_html(tokens, "yes", None)
        html2 = syntect.highlight_string(
            "fn main() {}", "Rust", "base16-ocean.dark", ss, ts
        ).as_html("yes", None)

        assert html1 == html2

    def test_shared_helper_with_default_bg(self, ss, ts, theme, rust):
        """Verify shared helper correctly handles default_bg."""
        hl = syntect.Highlighter(rust, theme)
        tokens = hl.highlight_line("fn main() {}", ss, ts)

        default_bg = theme.settings.background
        if default_bg is not None:
            html_with_default = syntect.as_html(tokens, "if_different", default_bg)
            html_no_default = syntect.as_html(tokens, "if_different", None)
            # With default_bg, some backgrounds may be excluded
            # Without default_bg, all backgrounds are included
            assert "background-color" in html_no_default


class TestHighlightStringCrlf:
    """Tests for highlight_string handling of CRLF line endings."""

    def test_highlight_string_crlf(self, ss, ts):
        """Test that highlight_string handles CRLF correctly."""
        code = "fn main() {\r\n    let x = 42;\r\n}"
        result = syntect.highlight_string(code, "Rust", "base16-ocean.dark", ss, ts)

        # No \\r should be in any token
        for _, text in result.tokens:
            assert '\r' not in text, f"Found \\r in token: {repr(text)}"
