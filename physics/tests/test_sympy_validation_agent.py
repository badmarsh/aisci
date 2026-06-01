"""
Tests for physics/src/sympy_validation_agent.py (SymPyPhysicsValidator).

Scope rules:
- These exercise the parsing / sanity-check behaviour of the validator only.
- No network, no file I/O, no HEPData. Pure symbolic math via sympy.
- LaTeX parsing depends on antlr4 (an optional dep); those paths are guarded
  with pytest.importorskip so the file still collects/passes when it's absent.
- Return shapes were read from the source before asserting; we do NOT assume
  unit tracking exists (the dimensional check is explicitly a placeholder).
"""

import pytest

sp = pytest.importorskip("sympy")

from sympy_validation_agent import SymPyPhysicsValidator


@pytest.fixture
def validator():
    return SymPyPhysicsValidator()


# ---------------------------------------------------------------------------
# parse_expression
# ---------------------------------------------------------------------------

class TestParseExpression:
    def test_parses_simple_text_expression(self, validator):
        expr = validator.parse_expression("p_T**2 + m**2")
        assert expr is not None
        assert isinstance(expr, sp.Basic)
        # Two distinct symbols should appear.
        names = {str(s) for s in expr.free_symbols}
        assert "p_T" in names
        assert "m" in names

    def test_parsed_text_expression_evaluates_correctly(self, validator):
        # x**2 + 3 with x=2 -> 7  (analytic, exact)
        expr = validator.parse_expression("x**2 + 3")
        assert expr is not None
        x = sp.Symbol("x")
        assert expr.subs(x, 2) == 7

    def test_local_dict_symbols_are_positive(self, validator):
        # local_dict maps m to a positive symbol; sqrt(m**2) should simplify to m.
        expr = validator.parse_expression("sqrt(m**2)")
        assert expr is not None
        assert sp.simplify(expr - validator.m) == 0

    def test_broken_input_returns_none(self, validator):
        assert validator.parse_expression("p_T ** + )(") is None

    def test_another_broken_input_returns_none(self, validator):
        assert validator.parse_expression("3 +* / 2") is None

    def test_latex_input_guarded_by_antlr(self, validator):
        # parse_latex requires antlr4; skip cleanly if the optional dep is absent.
        pytest.importorskip("antlr4")
        expr = validator.parse_expression(r"\frac{p_T}{m}")
        assert expr is not None
        assert isinstance(expr, sp.Basic)


# ---------------------------------------------------------------------------
# placeholder_dimensional_check
# ---------------------------------------------------------------------------

class TestPlaceholderDimensionalCheck:
    def test_finite_simplifiable_expression_is_true(self, validator):
        expr = sp.sympify("E**2 - p**2*c**2")
        assert validator.placeholder_dimensional_check(expr) is True

    def test_simple_polynomial_is_true(self, validator):
        assert validator.placeholder_dimensional_check(sp.sympify("x + y")) is True

    def test_zoo_returns_false(self, validator):
        # 1/0 -> complex infinity (zoo) in sympy.
        zoo_expr = 1 / sp.Integer(0)
        assert zoo_expr == sp.zoo
        assert validator.placeholder_dimensional_check(zoo_expr) is False

    def test_nan_returns_false(self, validator):
        assert validator.placeholder_dimensional_check(sp.nan) is False

    def test_expression_containing_zoo_term_returns_false(self, validator):
        x = sp.Symbol("x")
        expr = x + sp.zoo
        assert validator.placeholder_dimensional_check(expr) is False


# ---------------------------------------------------------------------------
# check_kinematic_boundaries
# ---------------------------------------------------------------------------

class TestCheckKinematicBoundaries:
    def test_returns_dict(self, validator):
        result = validator.check_kinematic_boundaries(sp.sympify("E**2 - p**2"))
        assert isinstance(result, dict)

    def test_no_beta_symbol_gives_empty_dict(self, validator):
        # No symbol whose name starts with 'β' -> no checks recorded.
        result = validator.check_kinematic_boundaries(sp.sympify("E**2 - p**2*c**2"))
        assert result == {}

    def test_beta_symbol_records_velocity_check(self, validator):
        # validator.beta is Symbol('β'); its presence adds a 'beta_β_lt_c' key.
        expr = validator.beta + validator.p
        result = validator.check_kinematic_boundaries(expr)
        key = f"beta_{validator.beta}_lt_c"
        assert key in result
        assert result[key] is True
        # Every recorded value is a bool.
        assert all(isinstance(v, bool) for v in result.values())


# ---------------------------------------------------------------------------
# validate_velocity_parameterization
# ---------------------------------------------------------------------------

class TestValidateVelocityParameterization:
    def test_returns_expected_keys(self, validator):
        expr = sp.sympify("U/sqrt(1 + U**2)")
        result = validator.validate_velocity_parameterization(expr)
        assert isinstance(result, dict)
        assert set(["valid", "max_velocity", "asymptotic_behavior"]).issubset(result)

    def test_subluminal_parameterization_is_valid(self, validator):
        # v = U/sqrt(1+U^2) -> v < 1 for all finite U; at U=1000 ~ 0.9999995.
        expr = sp.sympify("U/sqrt(1 + U**2)")
        result = validator.validate_velocity_parameterization(expr)
        assert result["valid"] is True
        assert result["max_velocity"] < 1.0
        assert result["max_velocity"] == pytest.approx(0.999999500000375, rel=1e-9)

    def test_superluminal_parameterization_flagged_invalid(self, validator):
        # v = U is unbounded; at U=1000 it is 1000 > 1 -> invalid.
        expr = sp.sympify("U")
        result = validator.validate_velocity_parameterization(expr)
        assert result["valid"] is False
        assert result["max_velocity"] == pytest.approx(1000.0)

    def test_expression_without_U_leaves_max_velocity_none(self, validator):
        # No symbol named 'U' -> the U-branch is skipped, defaults retained.
        expr = sp.sympify("p_T/T")
        result = validator.validate_velocity_parameterization(expr)
        assert result["valid"] is True
        assert result["max_velocity"] is None
        assert result["asymptotic_behavior"] is None


# ---------------------------------------------------------------------------
# validate_equation
# ---------------------------------------------------------------------------

class TestValidateEquation:
    EXPECTED_KEYS = {
        "original_equation",
        "parsed_expression",
        "placeholder_dimensional_check",
        "kinematic_valid",
        "velocity_valid",
        "overall_validity",
        "warnings",
    }

    def test_valid_equation_returns_documented_keys(self, validator):
        result = validator.validate_equation("E**2 - p**2*c**2 - m**2*c**4")
        assert self.EXPECTED_KEYS.issubset(result)
        assert result["original_equation"] == "E**2 - p**2*c**2 - m**2*c**4"
        assert result["parsed_expression"] is not None
        assert result["placeholder_dimensional_check"] is True
        assert result["velocity_valid"] is True
        assert result["overall_validity"] is True
        assert result["warnings"] == []
        assert isinstance(result["kinematic_valid"], dict)

    def test_overall_validity_is_conjunction(self, validator):
        # overall = dim_check AND velocity_valid; for a clean equation -> True.
        result = validator.validate_equation("p_T**2 + m**2")
        assert result["overall_validity"] == (
            result["placeholder_dimensional_check"] and result["velocity_valid"]
        )

    def test_unparseable_equation_marks_failure(self, validator):
        result = validator.validate_equation("p_T ** + )(")
        assert result["parsed_expression"] is None
        assert result["placeholder_dimensional_check"] is False
        assert result["velocity_valid"] is False
        assert result["overall_validity"] is False
        assert "Failed to parse equation" in result["warnings"]
        assert result["error"] == "Failed to parse equation"

    def test_velocity_equation_branch_runs(self, validator):
        # The string contains both 'v' and 'u' (case-insensitive) which routes
        # validate_equation through the velocity-parameterisation branch. Here
        # the parsed expression still carries an extra free symbol ('v'), so the
        # velocity check cannot resolve the > 1 comparison at U=1000 and reports
        # the case as not-valid. We assert this documented branch behaviour.
        result = validator.validate_equation("v - U/sqrt(1 + U**2)")
        assert result["parsed_expression"] is not None
        # Dimensional placeholder still passes (finite, simplifiable).
        assert result["placeholder_dimensional_check"] is True
        # Velocity branch could not prove subluminality -> flagged invalid,
        # which in turn drags overall_validity to False.
        assert result["velocity_valid"] is False
        assert result["overall_validity"] is False
        assert "Equation yields unphysical velocities >= c" in result["warnings"]

    def test_velocity_branch_skipped_for_non_velocity_equation(self, validator):
        # No 'v' substring -> velocity branch skipped, velocity_valid defaults True.
        result = validator.validate_equation("p_T**2 + m**2")
        assert result["velocity_valid"] is True
