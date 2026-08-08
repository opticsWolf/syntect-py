"""Parity coverage for the syntect APIs used by mordant."""
from pathlib import Path

import syntect


VS_CODE_THEME = """{
    // JSONC comments are accepted
    "name": "Parity Theme",
    /* and block comments too */
    "tokenColors": [
        {"scope": "variable, constant", "settings": {
            "foreground": "gold",
            "fontStyle": "bold italic underline"
        }}
    ],
    "colors": {
        "editor.background": "#1E1E1E",
        "editor.foreground": "#E0E0E0"
    }
}"""


def test_lookup_primitives_support_mordant_cascade():
    ss = syntect.SyntaxSet.load_defaults(True)
    assert ss.find_syntax_by_token("py").name == "Python"
    assert ss.find_syntax_by_token("rs").name == "Rust"
    assert ss.find_syntax_by_first_line("#!/usr/bin/env node").name == "JavaScript"
    assert ss.find_syntax_by_token("definitely-not-a-language") is None
    assert ss.find_syntax_by_first_line("not a shebang or modeline") is None


def test_theme_reader_and_registration():
    # Use a tracked package theme rather than the Solarized testdata
    # submodule, which is not initialized by the GitHub checkout action.
    source = Path(__file__).parents[1] / "syntect" / "themes" / "Solarized (dark).tmTheme"
    content = source.read_text(encoding="utf-8")
    theme = syntect.ThemeSet.load_theme_from_reader(content)
    assert theme.settings.background is not None

    themes = syntect.ThemeSet()
    themes.add_theme("solarized-copy", theme)
    assert themes.get_theme("solarized-copy").settings.background == theme.settings.background
    assert "solarized-copy" in themes.theme_names()


def test_theme_authoring_preserves_scope_selectors_and_font_flags():
    settings = syntect.ThemeSettings()
    settings.background = syntect.Color.from_hex("#1E1E1E")
    item = syntect.ThemeItem(
        syntect.ScopeSelectors.from_string("variable, constant"),
        syntect.StyleModifier(
            foreground=syntect.Color.from_hex("#FFD700"),
            background=None,
            font_style=syntect.FontStyle.from_string("bold italic underline"),
        ),
    )
    theme = syntect.Theme(name="constructed", author="test", settings=settings, scopes=[item])
    themes = syntect.ThemeSet()
    themes.add_theme("constructed", theme)
    loaded = themes.get_theme("constructed")

    assert loaded.scopes[0].scope_selectors.to_string() == "variable, constant"
    assert loaded.scopes[0].font_style == 7
    css = syntect.css_for_theme(loaded, "spaced")
    assert ".variable, .constant" in css
    assert "font-weight: bold" in css
    assert "font-style: italic" in css
    assert "text-decoration: underline" in css


def test_vscode_jsonc_conversion_and_global_registry():
    assert syntect.is_vscode_theme(VS_CODE_THEME)
    assert not syntect.is_plist_theme(VS_CODE_THEME)
    theme = syntect.parse_vscode_theme(VS_CODE_THEME)
    assert theme.name == "Parity Theme"
    assert theme.settings.background.to_hex() == "#1E1E1E"
    assert theme.scopes[0].scope_selectors.to_string() == "variable, constant"
    assert theme.scopes[0].font_style == 7

    syntect.add_custom_theme("parity-jsonc", VS_CODE_THEME)
    assert "parity-jsonc" in syntect.list_themes()
    assert "Rust" in syntect.list_syntaxes()


def test_bundled_themes_are_registered_at_import():
    names = syntect.list_themes()
    for expected in ("Dracula", "Nord", "Monokai Extended", "1337", "OneDark"):
        assert expected in names


def test_theme_directory_loader(tmp_path):
    theme_file = tmp_path / "directory-theme.json"
    theme_file.write_text(VS_CODE_THEME, encoding="utf-8")
    loaded = syntect.load_themes_from_folder(str(tmp_path))
    assert loaded == ["directory-theme"]
    assert "directory-theme" in syntect.list_themes()


def test_highlight_lines_can_take_theme_directly():
    ss = syntect.SyntaxSet.load_defaults(True)
    ts = syntect.ThemeSet.load_defaults()
    syntax = ss.find_syntax_by_name("Rust")
    theme = ts.get_theme("base16-ocean.dark")
    highlighter = syntect.HighlightLines.with_theme(syntax, ss, theme)
    assert highlighter.highlight_line("fn main() {}", ss)


def test_assets_api_and_fallback_theme():
    assets = syntect.Assets.from_binary()
    assert len(assets.get_syntax_set().syntaxes()) >= 190
    assert "Monokai Extended" in assets.theme_names()
    assert assets.get_theme("missing").key == "Monokai Extended"
    assets.set_fallback_theme("base16-ocean.dark")
    assert assets.get_theme("missing").key == "base16-ocean.dark"
    assert len(assets.get_theme_set().theme_names()) >= 8


def test_theme_set_fallback_argument():
    themes = syntect.ThemeSet.load_defaults()
    fallback = themes.get_theme("base16-ocean.dark")
    resolved = themes.get_theme("missing", "base16-ocean.dark")
    assert resolved.key == fallback.key
    assert themes.get_theme("missing") is None
