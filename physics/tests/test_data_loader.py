"""
Read-only unit tests for pure helper functions in physics/src/data_loader.py.

Scope rules (per AGENTS.md and project separation policy):
- Only the three pure, dependency-free helper functions are imported:
  normalize_space, parse_float, and stringify_range.
- No HTTP requests, no HEPData network calls, no file I/O, no pandas.
- This test file intentionally avoids importing the main() function or any
  function that calls requests.get, pd.DataFrame, or argparse.
- Scientific conclusions and data-availability verdicts must come from
  research/robert/ files, not from test output.
"""

import sys
from pathlib import Path

import pytest

# Add physics/src to the path so we can import the helpers without
# restructuring the production layout.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_loader import normalize_space, parse_float, stringify_range


class TestNormalizeSpace:
    def test_strips_leading_trailing(self):
        assert normalize_space("  hello  ") == "hello"

    def test_collapses_internal_whitespace(self):
        assert normalize_space("a  b\t  c") == "a b c"

    def test_non_string_input(self):
        assert normalize_space(42) == "42"

    def test_empty_string(self):
        assert normalize_space("") == ""

    def test_none_becomes_none_string(self):
        # The function calls str(value), so None -> "None".
        assert normalize_space(None) == "None"


class TestParseFloat:
    def test_plain_integer_string(self):
        assert parse_float("3") == pytest.approx(3.0)

    def test_decimal_string(self):
        assert parse_float("1.5") == pytest.approx(1.5)

    def test_negative_string(self):
        assert parse_float("-0.75") == pytest.approx(-0.75)

    def test_none_returns_none(self):
        assert parse_float(None) is None

    def test_empty_string_returns_none(self):
        assert parse_float("") is None

    def test_string_with_commas(self):
        # The production code strips commas for numbers like "1,234.5".
        assert parse_float("1,234.5") == pytest.approx(1234.5)

    def test_non_numeric_returns_none(self):
        assert parse_float("not-a-number") is None

    def test_float_passthrough(self):
        assert parse_float(2.718) == pytest.approx(2.718)

    def test_integer_passthrough(self):
        assert parse_float(7) == pytest.approx(7.0)


class TestStringifyRange:
    def test_integer_bounds(self):
        assert stringify_range(21.0, 30.0) == "21-30"

    def test_float_bounds(self):
        # Non-integer floats should not be rendered as integers.
        result = stringify_range(0.5, 1.5)
        assert result == "0.5-1.5"

    def test_none_low_returns_none(self):
        assert stringify_range(None, 30.0) is None

    def test_none_high_returns_none(self):
        assert stringify_range(21.0, None) is None

    def test_both_none_returns_none(self):
        assert stringify_range(None, None) is None

    @pytest.mark.parametrize("low,high,expected", [
        (21.0, 30.0, "21-30"),
        (101.0, 125.0, "101-125"),
        (126.0, 150.0, "126-150"),
    ])
    def test_manuscript_multiplicity_bins(self, low, high, expected):
        """Spot-check the ten manuscript multiplicity bins (21-30 … 126-150)."""
        assert stringify_range(low, high) == expected
