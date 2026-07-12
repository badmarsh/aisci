"""
Read-only unit tests for additional PURE helpers in libs/physics-core/src/data_loader.py.

Scope rules (per AGENTS.md and project separation policy):
- Only pure, dependency-free helpers are exercised here:
  parse_interval_token, symmetrize_error, classify_table,
  manuscript_bin_labels, extract_distribution_bin_ranges.
- No HTTP requests, no HEPData network calls, no file I/O, no pandas usage.
- normalize_space / parse_float / stringify_range are already covered in
  test_data_loader.py and are NOT re-tested here.

Note: importing data_loader pulls in pandas/requests at module import time,
but none of the functions under test touch the network or disk.
"""

import sys
from pathlib import Path

import pytest

# Add libs/physics-core/src to the path so we can import the helpers without
# restructuring the production layout.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_loader import (
    MANUSCRIPT_MULTIPLICITY_BINS,
    classify_table,
    extract_distribution_bin_ranges,
    manuscript_bin_labels,
    parse_interval_token,
    symmetrize_error,
)


class TestParseIntervalToken:
    @pytest.mark.parametrize("text,expected", [
        ("21-30", (21.0, 30.0)),
        ("101-125", (101.0, 125.0)),
        ("0.5-1.5", (0.5, 1.5)),
    ])
    def test_basic_intervals(self, text, expected):
        assert parse_interval_token(text) == expected

    def test_surrounding_and_internal_whitespace(self):
        # normalize_space collapses whitespace before the regex runs.
        assert parse_interval_token("  21  -  30 ") == (21.0, 30.0)

    def test_double_dash_separator_collapsed(self):
        # The "--" -> "-" replacement lets a double-dash separator parse.
        assert parse_interval_token("21--30") == (21.0, 30.0)

    def test_negative_low_bound(self):
        assert parse_interval_token("-5 - 3") == (-5.0, 3.0)

    def test_both_bounds_negative(self):
        # "-5.5 - -2.5": the space-separated negative high bound still matches.
        assert parse_interval_token("-5.5 - -2.5") == (-5.5, -2.5)

    @pytest.mark.parametrize("text", [
        "abc",          # no digits at all
        "5",            # single number, no range
        "1-2-3",        # three-token chain does not fullmatch
        "",             # empty
        "21 to 30",     # wrong separator
    ])
    def test_unparseable_returns_none_pair(self, text):
        assert parse_interval_token(text) == (None, None)

    def test_return_type_is_tuple_of_two(self):
        result = parse_interval_token("1-2")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_low_can_exceed_high_no_ordering_enforced(self):
        # The helper parses verbatim; it does not reorder bounds.
        assert parse_interval_token("30-21") == (30.0, 21.0)


class TestSymmetrizeError:
    def test_symerror_returns_value_for_all_three(self):
        label, minus, plus, sym = symmetrize_error({"label": "stat", "symerror": "0.5"})
        assert label == "stat"
        assert minus == pytest.approx(0.5)
        assert plus == pytest.approx(0.5)
        assert sym == pytest.approx(0.5)

    def test_symerror_label_is_normalized(self):
        label, *_ = symmetrize_error({"label": "  stat  error ", "symerror": "1"})
        assert label == "stat error"

    def test_missing_label_defaults_to_unknown(self):
        label, *_ = symmetrize_error({"symerror": "1.0"})
        assert label == "unknown"

    def test_asymerror_takes_absolute_values(self):
        # plus=+0.2, minus=-0.4 -> abs values, sym is the max of the two.
        label, minus, plus, sym = symmetrize_error(
            {"label": "sys", "asymerror": {"plus": "0.2", "minus": "-0.4"}}
        )
        assert label == "sys"
        assert minus == pytest.approx(0.4)
        assert plus == pytest.approx(0.2)
        assert sym == pytest.approx(0.4)

    def test_asymerror_symmetric_is_max_of_magnitudes(self):
        _, minus, plus, sym = symmetrize_error(
            {"asymerror": {"plus": "0.9", "minus": "-0.1"}}
        )
        assert minus == pytest.approx(0.1)
        assert plus == pytest.approx(0.9)
        assert sym == pytest.approx(0.9)

    def test_asymerror_plus_only(self):
        _, minus, plus, sym = symmetrize_error({"asymerror": {"plus": "0.3"}})
        assert minus is None
        assert plus == pytest.approx(0.3)
        # With minus missing, the symmetric value falls back to the only magnitude.
        assert sym == pytest.approx(0.3)

    def test_asymerror_minus_only(self):
        _, minus, plus, sym = symmetrize_error({"asymerror": {"minus": "-0.7"}})
        assert minus == pytest.approx(0.7)
        assert plus is None
        assert sym == pytest.approx(0.7)

    def test_asymerror_empty_returns_all_none(self):
        label, minus, plus, sym = symmetrize_error({"asymerror": {}})
        assert label == "unknown"
        assert minus is None and plus is None and sym is None

    def test_no_error_keys_returns_all_none(self):
        # Neither symerror nor asymerror present -> asym defaults to {}.
        _, minus, plus, sym = symmetrize_error({"label": "x"})
        assert minus is None and plus is None and sym is None

    def test_return_shape_is_four_tuple(self):
        result = symmetrize_error({"symerror": "1"})
        assert isinstance(result, tuple)
        assert len(result) == 4


class TestClassifyTable:
    def test_pt_spectrum(self):
        headers = [{"name": "PT(P=3)"}, {"name": "DPT(P=3)"}]
        assert classify_table(headers) == "pt_spectrum"

    def test_multiplicity_distribution(self):
        headers = [{"name": "N(P=3)"}, {"name": "DNEV/DN(P=3)"}]
        assert classify_table(headers) == "multiplicity_distribution"

    def test_mean_pt_vs_multiplicity(self):
        headers = [{"name": "N(P=3)"}, {"name": "MEAN(NAME=PT(P=3))"}]
        assert classify_table(headers) == "mean_pt_vs_multiplicity"

    def test_pseudorapidity_distribution(self):
        headers = [{"name": "ETARAP(P=3)"}, {"name": "DETARAP(P=3)"}]
        assert classify_table(headers) == "pseudorapidity_distribution"

    def test_unrecognized_headers(self):
        assert classify_table([{"name": "foo"}, {"name": "bar"}]) == "other"

    def test_empty_headers(self):
        assert classify_table([]) == "other"

    def test_multiplicity_requires_n_in_first_column(self):
        # DNEV/DN(P=3) is present but N(P=3) is not the first header -> "other".
        headers = [{"name": "X"}, {"name": "DNEV/DN(P=3)"}, {"name": "N(P=3)"}]
        assert classify_table(headers) == "other"

    def test_pt_spectrum_multi_column_layout(self):
        # PT(P=3) as first header with additional columns (the real HEPData
        # multi-column multiplicity-bin layout) classifies as pt_spectrum even
        # without a DPT(P=3) column. This path was added when multi-column
        # support was introduced in data_loader.classify_table (lines 147-148).
        headers = [{"name": "PT(P=3)"}, {"name": "YIELD"}]
        assert classify_table(headers) == "pt_spectrum"

    def test_pt_spectrum_single_column_no_dpt_is_other(self):
        # A single-column table with only PT(P=3) and no second column is "other"
        # because there are no dependent-variable columns to extract yields from.
        headers = [{"name": "PT(P=3)"}]
        assert classify_table(headers) == "other"

    def test_missing_name_key_defaults_to_empty(self):
        # Headers without a "name" key normalize to "" and fall through to "other".
        assert classify_table([{}, {}]) == "other"


class TestManuscriptBinLabels:
    def test_length_matches_constant(self):
        labels = manuscript_bin_labels()
        assert len(labels) == 10
        assert len(labels) == len(MANUSCRIPT_MULTIPLICITY_BINS)

    def test_known_endpoints(self):
        labels = manuscript_bin_labels()
        assert labels[0] == "21-30"
        assert labels[-1] == "126-150"

    def test_contains_specific_bins(self):
        labels = manuscript_bin_labels()
        assert "101-125" in labels
        assert "51-60" in labels

    def test_labels_match_constant_tuples(self):
        labels = manuscript_bin_labels()
        expected = [f"{low}-{high}" for low, high in MANUSCRIPT_MULTIPLICITY_BINS]
        assert labels == expected

    def test_all_labels_roundtrip_through_parse(self):
        # Every emitted label should parse back to its integer endpoints.
        for (low, high), label in zip(MANUSCRIPT_MULTIPLICITY_BINS, manuscript_bin_labels()):
            assert parse_interval_token(label) == (float(low), float(high))


class TestExtractDistributionBinRanges:
    def test_basic_extraction(self):
        table_json = {
            "values": [
                {"x": [{"low": "21", "high": "30"}]},
                {"x": [{"low": "31", "high": "40"}]},
            ]
        }
        assert extract_distribution_bin_ranges(table_json) == ["21-30", "31-40"]

    def test_rows_missing_bounds_are_skipped(self):
        # An x-cell without low/high produces no label and is dropped.
        table_json = {
            "values": [
                {"x": [{"low": "21", "high": "30"}]},
                {"x": [{}]},
                {"x": [{"low": "41", "high": "50"}]},
            ]
        }
        assert extract_distribution_bin_ranges(table_json) == ["21-30", "41-50"]

    def test_missing_x_cell_handled(self):
        # A value with no "x" key falls back to [{}] and is skipped.
        table_json = {"values": [{}, {"x": [{"low": "61", "high": "70"}]}]}
        assert extract_distribution_bin_ranges(table_json) == ["61-70"]

    def test_empty_values(self):
        assert extract_distribution_bin_ranges({"values": []}) == []

    def test_missing_values_key(self):
        assert extract_distribution_bin_ranges({}) == []

    def test_float_bounds_render_via_stringify(self):
        table_json = {"values": [{"x": [{"low": "0.5", "high": "1.5"}]}]}
        assert extract_distribution_bin_ranges(table_json) == ["0.5-1.5"]

    def test_order_is_preserved(self):
        table_json = {
            "values": [
                {"x": [{"low": "126", "high": "150"}]},
                {"x": [{"low": "21", "high": "30"}]},
            ]
        }
        # No sorting: rows come out in input order.
        assert extract_distribution_bin_ranges(table_json) == ["126-150", "21-30"]
