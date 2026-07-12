import numpy as np
import pytest

from tsallis_physics_validation import (
    tsallis_distribution,
    bgbw_distribution,
    apply_kinematic_boundaries,
    safe_fit_range_filter,
    validate_velocity_parameterization,
    fit_tsallis_to_data,
)


class TestTsallisDistribution:
    def test_zeros_when_T_nonpositive(self):
        pT = np.linspace(0.5, 5.0, 10)
        out = tsallis_distribution(pT, T=0.0, q=1.1)
        assert out.shape == pT.shape
        assert np.all(out == 0.0)
        out_neg = tsallis_distribution(pT, T=-0.2, q=1.1)
        assert np.all(out_neg == 0.0)

    def test_zeros_when_q_le_one(self):
        pT = np.linspace(0.5, 5.0, 10)
        assert np.all(tsallis_distribution(pT, T=0.16, q=1.0) == 0.0)
        assert np.all(tsallis_distribution(pT, T=0.16, q=0.9) == 0.0)

    def test_positive_and_finite_for_valid_params(self):
        pT = np.linspace(0.3, 8.0, 25)
        out = tsallis_distribution(pT, T=0.16, q=1.1)
        assert np.all(out > 0.0)
        assert np.all(np.isfinite(out))

    def test_falling_spectrum_decreases_with_pT(self):
        # Away from pT=0 the spectrum must fall monotonically (power-law tail).
        pT = np.linspace(0.5, 10.0, 50)
        out = tsallis_distribution(pT, T=0.16, q=1.1)
        assert np.all(np.diff(out) < 0.0)

    def test_shape_and_vectorization(self):
        pT = np.array([0.5, 1.0, 2.0, 4.0])
        out = tsallis_distribution(pT, T=0.16, q=1.1)
        assert out.shape == pT.shape
        # Vectorized result must match element-wise scalar evaluation.
        for i, p in enumerate(pT):
            single = tsallis_distribution(np.array([p]), T=0.16, q=1.1)[0]
            assert out[i] == pytest.approx(single, rel=1e-12)

    def test_larger_q_gives_harder_tail(self):
        # Larger q -> more power-law-like -> relatively more high-pT yield.
        pT = np.array([1.0, 8.0])
        soft = tsallis_distribution(pT, T=0.16, q=1.05)
        hard = tsallis_distribution(pT, T=0.16, q=1.3)
        ratio_soft = soft[1] / soft[0]
        ratio_hard = hard[1] / hard[0]
        assert ratio_hard > ratio_soft


class TestBGBWDistribution:
    def test_zeros_when_beta_max_ge_one(self):
        # beta_max = beta_avg * (n+2)/2; choose params that push beta_max >= 1.
        pT = np.array([0.5, 1.0, 2.0])
        out = bgbw_distribution(pT, T=0.16, beta_avg=0.95, n=1.0, m0=0.13957)
        assert out.shape == pT.shape
        assert np.all(out == 0.0)

    def test_positive_for_physical_params(self):
        pT = np.array([0.5, 1.0, 2.0])
        out = bgbw_distribution(pT, T=0.16, beta_avg=0.4, n=1.0, m0=0.13957)
        assert out.shape == pT.shape
        assert np.all(out > 0.0)
        assert np.all(np.isfinite(out))

    def test_boundary_beta_max_exactly_one(self):
        # beta_avg=0.5, n=2 -> beta_max = 0.5*4/2 = 1.0 -> zeros.
        pT = np.array([0.5, 1.0])
        out = bgbw_distribution(pT, T=0.16, beta_avg=0.5, n=2.0, m0=0.13957)
        assert np.all(out == 0.0)


class TestKinematicBoundaries:
    def test_zero_when_p_le_cut(self):
        assert apply_kinematic_boundaries(1.0, pT_cut=1.0, theta_cut=0.3) == 0.0
        assert apply_kinematic_boundaries(0.5, pT_cut=1.0, theta_cut=0.3) == 0.0

    def test_hand_computed_min_constraint(self):
        # p=5, pT_cut=3 -> sqrt(25-9)=4 ; theta_cut=pi/3 -> 5*cos(60deg)=2.5
        # min(4, 2.5) = 2.5
        val = apply_kinematic_boundaries(5.0, pT_cut=3.0, theta_cut=np.pi / 3.0)
        assert val == pytest.approx(2.5, rel=1e-12)

    def test_picks_sqrt_when_smaller(self):
        # p=5, pT_cut=4 -> sqrt(25-16)=3 ; theta_cut small -> 5*cos(~0) ~ 5
        # min(3, ~5) = 3
        val = apply_kinematic_boundaries(5.0, pT_cut=4.0, theta_cut=0.0)
        assert val == pytest.approx(3.0, rel=1e-12)

    def test_returns_more_restrictive(self):
        p, pT_cut, theta = 6.0, 2.0, np.pi / 6.0
        c1 = np.sqrt(p**2 - pT_cut**2)
        c2 = p * np.cos(theta)
        val = apply_kinematic_boundaries(p, pT_cut, theta)
        assert val == pytest.approx(min(c1, c2), rel=1e-12)


class TestSafeFitRangeFilter:
    def test_drops_below_threshold(self):
        pT = np.array([0.1, 0.3, 0.59, 0.6, 0.61, 1.0, 5.0])
        cs = np.array([10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 1.0])
        f_pT, f_cs = safe_fit_range_filter(pT, cs)
        assert np.all(f_pT >= 0.6)
        # 0.59 dropped, 0.6 kept (>= boundary).
        assert 0.59 not in f_pT
        assert 0.6 in f_pT
        np.testing.assert_array_equal(f_pT, np.array([0.6, 0.61, 1.0, 5.0]))

    def test_aligned_arrays_and_length(self):
        pT = np.array([0.2, 0.7, 1.5, 0.4, 3.0])
        cs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        f_pT, f_cs = safe_fit_range_filter(pT, cs)
        mask = pT >= 0.6
        assert len(f_pT) == int(np.sum(mask))
        assert len(f_pT) == len(f_cs)
        # cross-section values stay paired with their pT.
        np.testing.assert_array_equal(f_cs, cs[mask])
        np.testing.assert_array_equal(f_pT, pT[mask])


class TestVelocityParameterization:
    def test_zero_at_zero(self):
        v = validate_velocity_parameterization(np.array([0.0]))
        assert v[0] == pytest.approx(0.0, abs=1e-15)

    def test_subluminal_for_all_finite(self):
        U = np.linspace(-50.0, 50.0, 201)
        v = validate_velocity_parameterization(U)
        assert np.all(np.abs(v) < 1.0)
        assert np.all(np.isfinite(v))

    def test_monotonic_increasing(self):
        U = np.linspace(-10.0, 10.0, 100)
        v = validate_velocity_parameterization(U)
        assert np.all(np.diff(v) > 0.0)

    def test_asymptote_to_one(self):
        v_large = validate_velocity_parameterization(np.array([1e6]))[0]
        assert v_large == pytest.approx(1.0, abs=1e-6)
        assert v_large < 1.0

    def test_known_value_U1(self):
        # U=1 -> v = 1/sqrt(2)
        v = validate_velocity_parameterization(np.array([1.0]))[0]
        assert v == pytest.approx(1.0 / np.sqrt(2.0), rel=1e-12)

    def test_odd_symmetry(self):
        U = np.array([0.3, 1.7, 4.2])
        v_pos = validate_velocity_parameterization(U)
        v_neg = validate_velocity_parameterization(-U)
        np.testing.assert_allclose(v_neg, -v_pos, rtol=1e-12)


class TestFitTsallisToData:
    def test_recovers_parameters_from_clean_data(self):
        np.random.seed(12345)
        T_true, q_true = 0.18, 1.12
        pT = np.linspace(0.6, 6.0, 60)
        cs = tsallis_distribution(pT, T_true, q_true)
        popt, pcov = fit_tsallis_to_data(pT, cs)
        assert popt.shape == (2,)
        assert pcov.shape == (2, 2)
        T_fit, q_fit = popt
        # Loose tolerance: clean data should recover the generating params.
        assert T_fit == pytest.approx(T_true, rel=0.2)
        assert q_fit == pytest.approx(q_true, rel=0.2)

    def test_returns_two_params_and_cov_on_noisy_data(self):
        np.random.seed(7)
        pT = np.linspace(0.6, 6.0, 40)
        cs = tsallis_distribution(pT, 0.16, 1.1)
        noise = np.random.normal(0, 0.02 * cs, len(cs))
        cs_noisy = np.maximum(cs + noise, 1e-12)
        popt, pcov = fit_tsallis_to_data(pT, cs_noisy)
        assert popt.shape == (2,)
        assert pcov.shape == (2, 2)
        assert np.all(np.isfinite(popt))
