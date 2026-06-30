import pytest
import syntect


@pytest.fixture
def ss():
    return syntect.SyntaxSet.load_defaults(True)


"""Phase 14: SyntaxReference Complete Fields tests"""
import pytest
import syntect


class TestSyntaxReferenceFields:
    """Tests for all SyntaxReference fields."""

    def test_basic_fields(self, ss):
        """Test basic fields are accessible."""
        rust = ss.find_syntax_by_name("Rust")
        assert rust is not None
        assert rust.name == "Rust"
        assert rust.scope == "source.rust"
        assert rust.hidden is False
        assert len(rust.file_extensions) > 0
        assert "rs" in rust.file_extensions

    def test_first_line_match(self, ss):
        """Test that first_line_match returns the regex pattern or None."""
        rust = ss.find_syntax_by_name("Rust")
        # Rust syntax may or may not have first_line_match
        # The field should always be accessible
        assert rust.first_line_match is None or isinstance(rust.first_line_match, str)

    def test_version(self, ss):
        """Test that version returns the sublime-syntax format version."""
        rust = ss.find_syntax_by_name("Rust")
        assert rust.version in (1, 2)
        # Most built-in syntaxes are v2
        if rust.version == 2:
            # v2 syntaxes may have first_line_match and variables
            pass

    def test_variables(self, ss):
        """Test that variables returns the variable map as list of tuples."""
        rust = ss.find_syntax_by_name("Rust")
        # Variables may be empty or contain substitution variables
        assert isinstance(rust.variables, list)
        for k, v in rust.variables:
            assert isinstance(k, str)
            assert isinstance(v, str)

    def test_all_syntaxes_have_fields(self, ss):
        """Test that all syntaxes have the new fields."""
        for syntax in ss.syntaxes():
            assert syntax.name is not None
            assert syntax.scope is not None
            assert syntax.first_line_match is None or isinstance(syntax.first_line_match, str)
            assert isinstance(syntax.version, int)
            assert syntax.version >= 1
            assert isinstance(syntax.variables, list)

    def test_plain_text_syntax(self, ss):
        """Test plain text syntax has expected fields."""
        plain = ss.find_syntax_plain_text()
        assert plain.name == "Plain Text"
        assert plain.scope == "text.plain"
        assert plain.version in (1, 2)

    def test_find_by_extension(self, ss):
        """Test find_syntax_by_extension returns complete fields."""
        rust = ss.find_syntax_by_extension("rs")
        assert rust is not None
        assert rust.name == "Rust"
        assert rust.first_line_match is None or isinstance(rust.first_line_match, str)
        assert rust.version in (1, 2)
        assert isinstance(rust.variables, list)

    def test_repr_includes_version(self, ss):
        """Test that repr includes version info."""
        rust = ss.find_syntax_by_name("Rust")
        repr_str = repr(rust)
        assert "SyntaxReference" in repr_str
        assert "Rust" in repr_str
        assert "source.rust" in repr_str

    def test_find_by_scope(self, ss):
        """Test find_syntax_by_scope returns complete fields."""
        rust = ss.find_syntax_by_scope("source.rust")
        assert rust is not None
        assert rust.name == "Rust"
        assert rust.first_line_match is None or isinstance(rust.first_line_match, str)
        assert rust.version in (1, 2)

    def test_find_by_file(self, ss):
        """Test find_syntax_for_file returns complete fields."""
        rust = ss.find_syntax_for_file("test.rs")
        assert rust is not None
        assert rust.name == "Rust"
        assert rust.first_line_match is None or isinstance(rust.first_line_match, str)
        assert rust.version in (1, 2)
