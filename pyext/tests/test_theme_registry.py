"""Tests for the global theme registry (get_theme, get_theme_set)."""
import os

import syntect


# ---------------------------------------------------------------------------
# get_theme
# ---------------------------------------------------------------------------

class TestGetTheme:
    """syntect.get_theme(name) accesses the global bundle."""

    def test_tmtheme_get_theme(self):
        theme = syntect.get_theme("Monokai Extended")
        assert theme is not None
        assert theme.name == "Monokai Extended"
        assert theme.settings.foreground is not None
        assert theme.settings.background is not None

    def test_json_vscode_get_theme(self):
        theme = syntect.get_theme("Andromeda-color-theme")
        assert theme is not None
        assert theme.name == "Andromeda"
        assert theme.settings.foreground is not None

    def test_tmtheme_with_spaces_in_name(self):
        theme = syntect.get_theme("Solarized (dark)")
        assert theme is not None
        assert theme.name == "Solarized (dark)"

    def test_nonexistent_theme_returns_none(self):
        theme = syntect.get_theme("DoesNotExist")
        assert theme is None

    def test_all_bundled_themes_accessible(self):
        """Every theme in list_themes() must be retrievable."""
        all_names = syntect.list_themes()
        for name in all_names:
            theme = syntect.get_theme(name)
            assert theme is not None, f"get_theme({name!r}) returned None"


# ---------------------------------------------------------------------------
# get_theme_set
# ---------------------------------------------------------------------------

class TestGetThemeSet:
    """syntect.get_theme_set() returns a ThemeSet with all bundled themes."""

    def test_returns_theme_set(self):
        ts = syntect.get_theme_set()
        assert isinstance(ts, syntect.ThemeSet)

    def test_contains_all_bundled_themes(self):
        ts = syntect.get_theme_set()
        bundled_names = syntect.list_themes()
        ts_names = ts.theme_names()
        for name in bundled_names:
            assert name in ts_names, f"{name!r} missing from ThemeSet"
        assert len(ts_names) >= len(bundled_names)

    def test_highlight_line_works_with_bundled_theme(self):
        ts = syntect.get_theme_set()
        ss = syntect.SyntaxSet.load_defaults(False)
        rust = ss.find_syntax_by_name("Rust")
        assert rust is not None

        theme = syntect.get_theme("Monokai Extended")
        hl = syntect.Highlighter(rust, theme)
        result = hl.highlight_line("fn main() {}", ss, ts)
        assert len(result) > 0

    def test_highlight_line_works_with_json_theme(self):
        ts = syntect.get_theme_set()
        ss = syntect.SyntaxSet.load_defaults(False)
        rust = ss.find_syntax_by_name("Rust")
        assert rust is not None

        theme = syntect.get_theme("Panda")
        hl = syntect.Highlighter(rust, theme)
        result = hl.highlight_line("fn main() {}", ss, ts)
        assert len(result) > 0

    def test_highlight_line_works_with_spaced_name(self):
        ts = syntect.get_theme_set()
        ss = syntect.SyntaxSet.load_defaults(False)
        rust = ss.find_syntax_by_name("Rust")
        assert rust is not None

        theme = syntect.get_theme("Solarized (dark)")
        hl = syntect.Highlighter(rust, theme)
        result = hl.highlight_line("fn main() {}", ss, ts)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# Theme format detection
# ---------------------------------------------------------------------------

class TestThemeFormatDetection:
    """is_vscode_theme / is_plist_theme detect format from content."""

    def test_tmtheme_is_plist(self):
        theme_dir = os.path.dirname(syntect.__file__) + "/themes"
        tmtheme_files = [
            f for f in os.listdir(theme_dir) if f.endswith(".tmTheme")
        ][:5]
        for f in tmtheme_files:
            path = os.path.join(theme_dir, f)
            with open(path, "r") as fh:
                content = fh.read()
            assert syntect.is_plist_theme(content), f"{f} should be plist"
            assert not syntect.is_vscode_theme(content), f"{f} should not be vscode"

    def test_json_is_vscode(self):
        theme_dir = os.path.dirname(syntect.__file__) + "/themes"
        json_files = [
            f for f in os.listdir(theme_dir) if f.endswith(".json")
        ][:5]
        for f in json_files:
            path = os.path.join(theme_dir, f)
            with open(path, "r") as fh:
                content = fh.read()
            assert syntect.is_vscode_theme(content), f"{f} should be vscode"
            assert not syntect.is_plist_theme(content), f"{f} should not be plist"


# ---------------------------------------------------------------------------
# parse_vscode_theme round-trip
# ---------------------------------------------------------------------------

class TestParseVscodeTheme:
    """parse_vscode_theme produces usable Theme objects."""

    def test_parse_vscode_json(self):
        theme_dir = os.path.dirname(syntect.__file__) + "/themes"
        json_file = os.path.join(theme_dir, "Andromeda-color-theme.json")
        with open(json_file, "r") as fh:
            content = fh.read()
        theme = syntect.parse_vscode_theme(content)
        assert theme is not None
        assert theme.name == "Andromeda"
        assert theme.settings.foreground is not None

    def test_parse_tmtheme_via_theme_set(self):
        """Load .tmTheme content via ThemeSet.load_theme_from_reader."""
        theme_dir = os.path.dirname(syntect.__file__) + "/themes"
        tmtheme_file = os.path.join(theme_dir, "Monokai Extended.tmTheme")
        with open(tmtheme_file, "r") as fh:
            content = fh.read()
        assert syntect.is_plist_theme(content)
        theme = syntect.ThemeSet.load_theme_from_reader(content)
        assert theme is not None
        assert theme.name == "Monokai Extended"
