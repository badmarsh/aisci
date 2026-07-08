import math

import numpy as np
import pandas as pd
import pytest

from fitting_pipeline import (
    safe_exp,
    vectorize_scalar_model,
    build_initial_grid,
    manuscript_fit_spec,
    bose_fit_spec,
    tsallis_fit_spec,
    blast_wave_fit_spec,
    infer_group_columns,
    FitSpec,
    DEFAULT_MANUSCRIPT_BOUNDS,
    DEFAULT_TSALLIS_BOUNDS,
    DEFAULT_BLAST_WAVE_BOUNDS,
)


class TestSafeExpBoundary:
    def test_exact_upper_boundary_passes_through(self):
        # 700.0 is NOT > 700.0, so it passes through unchanged.
        assert safe_exp(700.0) == math.exp(700.0)

    def test_exact_lower_boundary_passes_through(self):
        # -700.0 is NOT < -700.0, so it passes through unchanged.
        assert safe_exp(-700.0) == math.exp(-700.0)

    def test_just_inside_upper_passes_through(self):
        assert safe_exp(699.9999) == math.exp(699.9999)

    def test_just_outside_upper_clamps(self):
        # Anything strictly above 700 clamps to exp(700).
        assert safe_exp(700.0001) == math.exp(700.0)
        assert safe_exp(1e6) == math.exp(700.0)

    def test_just_inside_lower_passes_through(self):
        assert safe_exp(-699.9999) == math.exp(-699.9999)

    def test_just_outside_lower_clamps(self):
        assert safe_exp(-700.0001) == math.exp(-700.0)
        assert safe_exp(-1e6) == math.exp(-700.0)

    def test_zero_is_one(self):
        assert safe_exp(0.0) == pytest.approx(1.0)


class TestVectorizeScalarModel:
    def test_with_eta_max_matches_scalar_per_point(self):
        # scalar_fn signature: (pt, a, b, eta_max, mass_gev)
        def scalar_fn(pt, a, b, eta_max, mass_gev):
            return a * pt + b * eta_max + mass_gev

        chunks = [("a", "b")]
        model = vectorize_scalar_model(scalar_fn, chunks, eta_max=2.0, mass_gev=0.5)
        pt = np.array([0.3, 1.0, 2.5, 4.0])
        a, b = 1.5, 0.7
        out = model(pt, a, b)
        assert isinstance(out, np.ndarray)
        assert out.shape == pt.shape
        expected = np.array([scalar_fn(float(p), a, b, 2.0, 0.5) for p in pt])
        np.testing.assert_allclose(out, expected)

    def test_without_eta_max_omits_eta_argument(self):
        # eta_max=None => scalar called as (pt, *chunk, mass_gev)
        def scalar_fn(pt, a, b, mass_gev):
            return a * pt * pt + b - mass_gev

        chunks = [("a", "b")]
        model = vectorize_scalar_model(scalar_fn, chunks, eta_max=None, mass_gev=0.25)
        pt = np.array([0.5, 1.5, 3.0])
        a, b = 2.0, -0.4
        out = model(pt, a, b)
        assert isinstance(out, np.ndarray)
        expected = np.array([scalar_fn(float(p), a, b, 0.25) for p in pt])
        np.testing.assert_allclose(out, expected)

    def test_multiple_chunks_sum_components(self):
        # Two components should sum elementwise.
        def scalar_fn(pt, a, eta_max, mass_gev):
            return a * pt

        chunks = [("a",), ("a",)]
        model = vectorize_scalar_model(scalar_fn, chunks, eta_max=1.0, mass_gev=0.0)
        pt = np.array([1.0, 2.0, 5.0])
        # params flattened across chunks: first chunk a=3, second chunk a=4
        out = model(pt, 3.0, 4.0)
        # total = 3*pt + 4*pt = 7*pt
        np.testing.assert_allclose(out, 7.0 * pt)
        assert out.shape == pt.shape

    def test_accepts_list_input_returns_array(self):
        def scalar_fn(pt, a, eta_max, mass_gev):
            return a + pt

        model = vectorize_scalar_model(scalar_fn, [("a",)], eta_max=1.0, mass_gev=0.0)
        out = model([1.0, 2.0], 10.0)
        assert isinstance(out, np.ndarray)
        np.testing.assert_allclose(out, np.array([11.0, 12.0]))


class TestBuildInitialGrid:
    def test_arity_and_count_single_component(self):
        y = np.array([1.0, 5.0, 3.0])
        temps = (0.1, 0.2)
        thirds = (0.5, 0.7, 0.9)
        grid = build_initial_grid(1, ("norm", "temperature", "U"), y, temps, thirds)
        assert isinstance(grid, list)
        assert len(grid) == len(temps) * len(thirds)
        # arity = component_count * number of params = 1 * 3
        for candidate in grid:
            assert isinstance(candidate, tuple)
            assert len(candidate) == 3

    def test_arity_two_components(self):
        y = np.array([10.0, 2.0])
        grid = build_initial_grid(
            2, ("norm", "temperature", "q"), y, (0.1,), (1.05, 1.1)
        )
        assert len(grid) == 1 * 2
        for candidate in grid:
            assert len(candidate) == 2 * 3

    def test_norm_scales_with_max_y_and_component_scales(self):
        # Single temp/third guess so we inspect one candidate deterministically.
        y = np.array([4.0, 8.0, 1.0])  # max = 8.0
        grid = build_initial_grid(
            2, ("norm", "temperature", "U"), y, (0.2,), (0.5,)
        )
        assert len(grid) == 1
        candidate = grid[0]
        # order: comp0(norm,temp,U), comp1(norm,temp,U)
        norm0, temp0, u0, norm1, temp1, u1 = candidate
        # norm uses component_scales for 2 comps = (0.7, 0.3) * max_y
        assert norm0 == pytest.approx(8.0 * 0.7)
        assert norm1 == pytest.approx(8.0 * 0.3)
        # temperature scales by (1 + 0.12*idx)
        assert temp0 == pytest.approx(0.2 * 1.0)
        assert temp1 == pytest.approx(0.2 * (1.0 + 0.12))
        # third param (U) scales by (1 + 0.10*idx)
        assert u0 == pytest.approx(0.5 * 1.0)
        assert u1 == pytest.approx(0.5 * (1.0 + 0.10))

    def test_handles_nan_in_y(self):
        y = np.array([np.nan, 2.0, np.nan])  # nanmax = 2.0
        grid = build_initial_grid(1, ("norm",), y, (0.1,), (0.5,))
        assert grid[0][0] == pytest.approx(2.0)

    def test_norm_floor_when_y_nonpositive(self):
        y = np.array([0.0, 0.0])  # max 0 -> floored to 1e-9
        grid = build_initial_grid(1, ("norm",), y, (0.1,), (0.5,))
        assert grid[0][0] == pytest.approx(1e-9)


class TestFitSpecs:
    def _assert_bounds_keys_match_names(self, spec: FitSpec):
        assert set(spec.parameter_bounds.keys()) == set(spec.parameter_names)

    def test_manuscript_fit_spec(self):
        spec = manuscript_fit_spec(component_count=2, eta_max=2.5, mass_gev=0.13957)
        assert isinstance(spec, FitSpec)
        assert spec.model_name == "manuscript_juttner"
        assert spec.component_count == 2
        assert spec.parameter_names == [
            "norm_1", "temperature_1", "U_1",
            "norm_2", "temperature_2", "U_2",
        ]
        self._assert_bounds_keys_match_names(spec)
        assert spec.parameter_bounds["norm_1"] == (1e-12, None)  # AIS-61: was (0.0, None)
        assert spec.parameter_bounds["temperature_1"] == DEFAULT_MANUSCRIPT_BOUNDS["temperature"]
        assert spec.parameter_bounds["U_2"] == DEFAULT_MANUSCRIPT_BOUNDS["U"]
        assert spec.fixed_metadata == {"eta_max": 2.5, "mass_gev": 0.13957}

    def test_bose_fit_spec(self):
        spec = bose_fit_spec(component_count=1, eta_max=2.0, mass_gev=0.14)
        assert spec.model_name == "exact_bose_einstein"
        assert spec.parameter_names == ["norm_1", "temperature_1", "U_1"]
        self._assert_bounds_keys_match_names(spec)
        assert spec.parameter_bounds["norm_1"] == (1e-12, None)  # AIS-61: was (0.0, None)
        assert spec.parameter_bounds["temperature_1"] == DEFAULT_MANUSCRIPT_BOUNDS["temperature"]
        assert spec.parameter_bounds["U_1"] == DEFAULT_MANUSCRIPT_BOUNDS["U"]

    def test_tsallis_fit_spec(self):
        spec = tsallis_fit_spec(component_count=2, eta_max=2.5, mass_gev=0.14)
        assert spec.model_name == "tsallis"
        assert spec.parameter_names == [
            "norm_1", "temperature_1", "q_1",
            "norm_2", "temperature_2", "q_2",
        ]
        self._assert_bounds_keys_match_names(spec)
        assert spec.parameter_bounds["norm_2"] == (1e-12, None)  # AIS-61: was (0.0, None)
        assert spec.parameter_bounds["temperature_1"] == DEFAULT_TSALLIS_BOUNDS["temperature"]
        assert spec.parameter_bounds["q_1"] == DEFAULT_TSALLIS_BOUNDS["q"]

    def test_blast_wave_fit_spec(self):
        spec = blast_wave_fit_spec(component_count=1, mass_gev=0.14)
        assert spec.model_name == "blast_wave"
        assert spec.parameter_names == ["norm_1", "temperature_1", "beta_s_1", "n_1"]
        self._assert_bounds_keys_match_names(spec)
        assert spec.parameter_bounds["norm_1"] == (1e-12, None)  # AIS-61: was (0.0, None)
        assert spec.parameter_bounds["temperature_1"] == DEFAULT_BLAST_WAVE_BOUNDS["temperature"]
        assert spec.parameter_bounds["beta_s_1"] == DEFAULT_BLAST_WAVE_BOUNDS["beta_s"]
        assert spec.parameter_bounds["n_1"] == DEFAULT_BLAST_WAVE_BOUNDS["n"]
        # blast wave fixed_metadata carries only mass (no eta_max).
        assert spec.fixed_metadata == {"mass_gev": 0.14}

    def test_parameter_names_arity_scales_with_components(self):
        for cc in (1, 2, 3):
            spec = manuscript_fit_spec(cc, eta_max=2.0, mass_gev=0.14)
            assert len(spec.parameter_names) == cc * 3
            bw = blast_wave_fit_spec(cc, mass_gev=0.14)
            assert len(bw.parameter_names) == cc * 4


class TestInferGroupColumns:
    def test_prefers_manuscript_bin_first(self):
        df = pd.DataFrame(
            {
                "manuscript_bin": ["a", "b"],
                "source_table": ["t1", "t2"],
                "eta_range": ["-2.5-2.5", "-2.5-2.5"],
            }
        )
        assert infer_group_columns(df) == ["manuscript_bin"]

    def test_falls_back_to_source_table(self):
        df = pd.DataFrame(
            {
                "source_table": ["t1", "t2"],
                "eta_range": ["-2.5-2.5", "-2.5-2.5"],
            }
        )
        assert infer_group_columns(df) == ["source_table"]

    def test_falls_back_to_eta_range(self):
        df = pd.DataFrame({"eta_range": ["0-2.5", "0-2.5"]})
        assert infer_group_columns(df) == ["eta_range"]

    def test_returns_empty_when_no_grouping_columns(self):
        df = pd.DataFrame({"pt_center_gev": [1.0, 2.0], "yield_value": [3.0, 4.0]})
        assert infer_group_columns(df) == []

    def test_all_nan_column_is_skipped(self):
        # manuscript_bin present but entirely NaN -> skipped; fall through.
        df = pd.DataFrame(
            {
                "manuscript_bin": [np.nan, np.nan],
                "source_table": ["t1", "t2"],
            }
        )
        assert infer_group_columns(df) == ["source_table"]

    def test_partially_populated_column_is_used(self):
        df = pd.DataFrame({"manuscript_bin": [np.nan, "b"]})
        assert infer_group_columns(df) == ["manuscript_bin"]
