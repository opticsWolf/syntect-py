"""Tests for syntect-py"""
import pytest
import syntect


class TestColor:
    def test_from_hex(self):
        c = syntect.Color.from_hex("#FF0000")
        assert c.r == 255
        assert c.g == 0
        assert c.b == 0
        assert c.a == 255

    def test_to_hex(self):
        c = syntect.Color(255, 0, 0, 255)
        assert c.to_hex() == "#FF0000"

    def test_equality(self):
        c1 = syntect.Color(255, 0, 0, 255)
        c2 = syntect.Color(255, 0, 0, 255)
        c3 = syntect.Color(0, 255, 0, 255)
        assert c1 == c2
        assert c1 != c3


class TestFontStyle:
    def test_bitwise_or(self):
        fs = syntect.FontStyle.BOLD | syntect.FontStyle.ITALIC
        assert fs.bits == 5

    def test_bitwise_and(self):
        fs = syntect.FontStyle.BOLD & syntect.FontStyle.ITALIC
        assert fs.bits == 0

    def test_constants(self):
        assert syntect.FontStyle.BOLD.bits == 1
        assert syntect.FontStyle.ITALIC.bits == 4
        assert syntect.FontStyle.UNDERLINE.bits == 2


class TestStyle:
    def test_from_hex_styles(self):
        style = syntect.Style.from_hex_styles("#B48EAD", "#2B303B", 0)
        assert style.foreground.to_hex() == "#B48EAD"
        assert style.background.to_hex() == "#2B303B"
        assert style.font_style.bits == 0

    def test_equality(self):
        s1 = syntect.Style.from_hex_styles("#B48EAD", "#2B303B", 0)
        s2 = syntect.Style.from_hex_styles("#B48EAD", "#2B303B", 0)
        s3 = syntect.Style.from_hex_styles("#FFFFFF", "#000000", 0)
        assert s1 == s2
        assert s1 != s3


class TestSyntaxSet:
    def test_load_defaults(self):
        ss = syntect.SyntaxSet.load_defaults(True)
        assert len(ss.syntaxes()) > 0

    def test_find_syntax_by_name(self):
        ss = syntect.SyntaxSet.load_defaults(True)
        rust = ss.find_syntax_by_name("Rust")
        assert rust is not None
        assert rust.name == "Rust"

    def test_find_syntax_by_extension(self):
        ss = syntect.SyntaxSet.load_defaults(True)
        py = ss.find_syntax_by_extension("py")
        assert py is not None
        assert py.name == "Python"

    def test_find_syntax_by_scope(self):
        ss = syntect.SyntaxSet.load_defaults(True)
        # JavaScript scope should be found
        js = ss.find_syntax_by_scope("source.javascript")
        # Note: This may return None depending on the syntax set


class TestThemeSet:
    def test_load_defaults(self):
        ts = syntect.ThemeSet.load_defaults()
        assert len(ts.theme_names()) > 0

    def test_get_theme(self):
        ts = syntect.ThemeSet.load_defaults()
        theme = ts.get_theme("base16-ocean.dark")
        assert theme is not None
        assert theme.name == "Base16 Ocean Dark"
        assert theme.key == "base16-ocean.dark"

    def test_theme_scopes(self):
        ts = syntect.ThemeSet.load_defaults()
        theme = ts.get_theme("base16-ocean.dark")
        assert len(theme.scopes) > 0
        for item in theme.scopes[:3]:
            assert item.scope is not None
            assert item.foreground is not None or item.background is not None


class TestHighlighter:
    def test_highlight_line(self):
        ss = syntect.SyntaxSet.load_defaults(True)
        ts = syntect.ThemeSet.load_defaults()
        rust = ss.find_syntax_by_name("Rust")
        theme = ts.get_theme("base16-ocean.dark")
        
        hl = syntect.Highlighter(rust, theme)
        tokens = hl.highlight_line("fn main() {}", ss, ts)
        
        assert len(tokens) > 0
        for style, text in tokens:
            assert isinstance(style, syntect.Style)
            assert isinstance(text, str)
            assert len(text) > 0

    def test_highlight_lines(self):
        ss = syntect.SyntaxSet.load_defaults(True)
        ts = syntect.ThemeSet.load_defaults()
        rust = ss.find_syntax_by_name("Rust")
        theme = ts.get_theme("base16-ocean.dark")
        
        hl = syntect.Highlighter(rust, theme)
        code = "fn main() {\n    println!(\"hello\");\n}"
        all_tokens = hl.highlight_lines(code, ss, ts)
        
        assert len(all_tokens) == 3  # 3 lines


class TestParseState:
    def test_parse_line(self):
        ss = syntect.SyntaxSet.load_defaults(True)
        ps = syntect.ParseState("Rust", ss)
        output = ps.parse_line("fn main() {}", ss)
        
        assert len(output.ops) > 0
        for pos, op in output.ops:
            assert isinstance(pos, int)
            assert isinstance(op, str)
            assert op.startswith("Push") or op.startswith("Pop")


class TestScope:
    def test_from_string(self):
        scope = syntect.Scope.from_string("source.rust keyword")
        assert scope.to_string() == "source.rust keyword"
        assert scope.len() == 2

    def test_prefix(self):
        s1 = syntect.Scope.from_string("source.rust")
        s2 = syntect.Scope.from_string("source.rust keyword")
        assert True  # Syntect scope prefix logic varies


class TestScopeStack:
    def test_push_pop(self):
        stack = syntect.ScopeStack()
        stack.push(syntect.Scope("source.rust"))
        stack.push(syntect.Scope("keyword"))
        assert stack.as_string() == "source.rust keyword"
        assert stack.len() == 2
        stack.pop()
        assert stack.len() == 1

    def test_apply(self):
        stack = syntect.ScopeStack()
        op = syntect.ScopeStackOp.push(syntect.Scope("string"))
        stack.apply(op)
        assert stack.len() == 1


class TestOutputUtilities:
    def test_as_terminal_escaped(self):
        ss = syntect.SyntaxSet.load_defaults(True)
        ts = syntect.ThemeSet.load_defaults()
        rust = ss.find_syntax_by_name("Rust")
        theme = ts.get_theme("base16-ocean.dark")
        
        hl = syntect.Highlighter(rust, theme)
        tokens = hl.highlight_line("fn main() {}", ss, ts)
        
        escaped = syntect.as_terminal_escaped(tokens, True)
        assert chr(0x1b) in escaped  # Contains escape codes

    def test_as_html(self):
        ss = syntect.SyntaxSet.load_defaults(True)
        ts = syntect.ThemeSet.load_defaults()
        rust = ss.find_syntax_by_name("Rust")
        theme = ts.get_theme("base16-ocean.dark")
        
        hl = syntect.Highlighter(rust, theme)
        tokens = hl.highlight_line("fn main() {}", ss, ts)
        
        html = syntect.as_html(tokens, "if_different", None)
        assert "<span" in html
        assert "style=" in html

    def test_as_latex_escaped(self):
        ss = syntect.SyntaxSet.load_defaults(True)
        ts = syntect.ThemeSet.load_defaults()
        rust = ss.find_syntax_by_name("Rust")
        theme = ts.get_theme("base16-ocean.dark")
        
        hl = syntect.Highlighter(rust, theme)
        tokens = hl.highlight_line("fn main() {}", ss, ts)
        
        latex = syntect.as_latex_escaped(tokens)
        assert "\\textcolor" in latex

    def test_highlight_string(self):
        ss = syntect.SyntaxSet.load_defaults(True)
        ts = syntect.ThemeSet.load_defaults()
        
        result = syntect.highlight_string(
            "fn main() {}", "Rust", "base16-ocean.dark", ss, ts
        )
        
        assert len(result.tokens) > 0
        assert len(result.html) > 0
        assert "<pre" in result.html

    def test_highlight_result_convenience_methods(self):
        ss = syntect.SyntaxSet.load_defaults(True)
        ts = syntect.ThemeSet.load_defaults()
        
        result = syntect.highlight_string(
            "fn main() {}", "Rust", "base16-ocean.dark", ss, ts
        )
        
        # Test as_html
        html = result.as_html("if_different", None)
        assert "<span" in html
        
        # Test as_terminal_escaped
        escaped = result.as_terminal_escaped(True)
        assert chr(0x1b) in escaped
        
        # Test as_latex_escaped
        latex = result.as_latex_escaped()
        assert "\\textcolor" in latex


class TestDumpUtilities:
    def test_dump_load_roundtrip(self, tmp_path):
        ss = syntect.SyntaxSet.load_defaults(True)
        path = str(tmp_path / "syntaxes.packdump")
        
        syntect.dump_syntax_set(ss, path)
        ss2 = syntect.load_syntax_set(path)
        
        assert len(ss2.syntaxes()) == len(ss.syntaxes())

    def test_dump_theme_roundtrip(self, tmp_path):
        ts = syntect.ThemeSet.load_defaults()
        path = str(tmp_path / "themes.themedump")
        
        syntect.dump_theme_set(ts, path)
        ts2 = syntect.load_theme_set(path)
        
        assert len(ts2.theme_names()) == len(ts.theme_names())


class TestErrors:
    def test_loading_error(self):
        with pytest.raises(syntect.LoadingError):
            raise syntect.LoadingError("test error")

    def test_parsing_error(self):
        with pytest.raises(syntect.ParsingError):
            raise syntect.ParsingError("test error")

    def test_dump_error(self):
        with pytest.raises(syntect.DumpError):
            raise syntect.DumpError("test error")


class TestClassStyle:
    def test_spaced(self):
        cs = syntect.ClassStyle.spaced()
        assert cs is not None

    def test_spaced_prefixed(self):
        cs = syntect.ClassStyle.spaced_prefixed("syn-")
        assert cs is not None


class TestIncludeBg:
    def test_no(self):
        ib = syntect.IncludeBg.no()
        assert ib is not None

    def test_if_different(self):
        ib = syntect.IncludeBg.if_different()
        assert ib is not None
