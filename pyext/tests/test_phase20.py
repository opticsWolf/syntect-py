"""Phase 20: parsing Module Bindings tests"""
import pytest
import syntect


class TestMatchPower:
    """Tests for MatchPower class."""

    def test_create_match_power(self):
        """Test creating a MatchPower."""
        mp = syntect.MatchPower(0.5)
        assert mp.value == 0.5
        assert repr(mp) == "MatchPower(0.5000)"

    def test_match_power_float(self):
        """Test MatchPower can be converted to float."""
        mp = syntect.MatchPower(0.75)
        assert float(mp) == 0.75

    def test_match_power_negative(self):
        """Test MatchPower with negative value."""
        mp = syntect.MatchPower(-1.0)
        assert mp.value == -1.0


class TestClearAmount:
    """Tests for ClearAmount class."""

    def test_clear_all(self):
        """Test ClearAmount.all_()."""
        ca = syntect.ClearAmount.all_()
        assert ca.kind == "all"
        assert ca.value == 0
        assert "all" in repr(ca)

    def test_clear_top_n(self):
        """Test ClearAmount.top_n()."""
        ca = syntect.ClearAmount.top_n(3)
        assert ca.kind == "top_n"
        assert ca.value == 3
        assert "top_n=3" in repr(ca)


class TestContextId:
    """Tests for ContextId class."""

    def test_create_context_id(self):
        """Test creating a ContextId."""
        cid = syntect.ContextId(0, 5)
        assert cid.syntax_index == 0
        assert cid.context_index == 5
        assert "syntax=0" in repr(cid)
        assert "context=5" in repr(cid)

    def test_context_id_equality(self):
        """Test ContextId equality."""
        cid1 = syntect.ContextId(0, 5)
        cid2 = syntect.ContextId(0, 5)
        cid3 = syntect.ContextId(1, 5)
        assert cid1 == cid2
        assert cid1 != cid3


class TestFindUnlinkedContexts:
    """Tests for find_unlinked_contexts function."""

    def test_find_unlinked_contexts(self):
        """Test finding unlinked contexts in built-in syntaxes."""
        ss = syntect.SyntaxSet.load_defaults(False)
        unlinked = ss.find_unlinked_contexts()
        # Should find some unlinked contexts in built-in syntaxes
        assert isinstance(unlinked, list)
        # HTML (ASP) has known unlinked references
        assert any("text.html.asp" in u for u in unlinked)

    def test_find_unlinked_contexts_empty(self):
        """Test find_unlinked_contexts on empty syntax set."""
        ss = syntect.SyntaxSet()
        unlinked = ss.find_unlinked_contexts()
        assert unlinked == []


class TestParseSyntaxError:
    """Tests for ParseSyntaxError exception type."""

    def test_parse_syntax_error_exists(self):
        """Test that ParseSyntaxError exception type exists."""
        assert hasattr(syntect, 'ParseSyntaxError')
        assert issubclass(syntect.ParseSyntaxError, Exception)

    def test_parse_syntax_error_raise(self):
        """Test raising ParseSyntaxError."""
        with pytest.raises(syntect.ParseSyntaxError):
            raise syntect.ParseSyntaxError("Test error")


@pytest.fixture
def ss():
    """Load syntax set."""
    return syntect.SyntaxSet.load_defaults(False)


@pytest.fixture
def ts():
    """Load theme set."""
    return syntect.ThemeSet.load_defaults()
