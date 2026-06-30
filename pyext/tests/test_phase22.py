"""Phase 22: Highlighting Module Bindings tests"""
import pytest
import syntect


class TestScoredStyle:
    """Tests for ScoredStyle class."""

    def test_create_scored_style(self):
        """Test creating a ScoredStyle."""
        ss = syntect.ScoredStyle(
            255, 0, 0, 255, 0.5,
            0, 0, 0, 255, 0.5,
            0, 0.0
        )
        assert ss.foreground_r == 255
        assert ss.foreground_g == 0
        assert ss.foreground_b == 0
        assert ss.foreground_a == 255
        assert ss.foreground_score == 0.5
        assert ss.background_r == 0
        assert ss.background_score == 0.5
        assert ss.font_style == 0
        assert ss.font_style_score == 0.0

    def test_scored_style_repr(self):
        """Test ScoredStyle repr."""
        ss = syntect.ScoredStyle(255, 128, 64, 255, 1.0, 0, 0, 0, 255, 0.0, 1, 0.5)
        assert "ScoredStyle" in repr(ss)
        assert "#ff8040" in repr(ss) or "ff8040" in repr(ss).lower()


class TestScopeRangeIterator:
    """Tests for ScopeRangeIterator class."""

    def test_iterate_basic(self):
        """Test iterating over scope ranges."""
        ops = [
            (0, "Push(source)"),
            (2, "Push(keyword)"),
            (5, "Pop(1)"),
        ]
        line = "fn main"
        iterator = syntect.ScopeRangeIterator(ops, line)
        results = list(iterator)
        assert len(results) == 3
        assert results[0] == (0, 2, "source")
        assert results[1] == (2, 5, "keyword")

    def test_iterate_end_of_line(self):
        """Test iteration reaches end of line."""
        ops = [
            (0, "Push(source)"),
            (5, "Pop(1)"),
        ]
        line = "hello"
        iterator = syntect.ScopeRangeIterator(ops, line)
        results = list(iterator)
        # Should iterate until ops exhausted, last range extends to end of line
        assert len(results) == 2
        assert results[-1][1] == 5  # extends to end of line

    def test_iterate_empty(self):
        """Test iteration with no ops."""
        iterator = syntect.ScopeRangeIterator([], "hello")
        results = list(iterator)
        assert results == []

    def test_iterate_protocol(self):
        """Test that iterator supports Python iteration protocol."""
        ops = [(0, "Push(test)")]
        line = "abc"
        iterator = syntect.ScopeRangeIterator(ops, line)
        # Should be iterable
        count = 0
        for start, end, scope in iterator:
            count += 1
        assert count == 1


@pytest.fixture
def ss():
    """Load syntax set."""
    return syntect.SyntaxSet.load_defaults(False)


@pytest.fixture
def ts():
    """Load theme set."""
    return syntect.ThemeSet.load_defaults()
