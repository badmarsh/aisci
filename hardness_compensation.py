import math
from scipy.integrate import quad

def eta_integral(integrand, eta_min, eta_max):
    result, _ = quad(integrand, eta_min, eta_max, limit=200)
    return result

def safe_exp(value: float) -> float:
    if value > 700.0: return math.exp(700.0)
    if value < -700.0: return math.exp(-700.0)
    return math.exp(value)

def manuscript_component_scalar(pt, norm, temperature, U, eta_max, mass_gev=0.13957):
    mt = math.sqrt(mass_gev * mass_gev + pt * pt)
    gamma = math.sqrt(1.0 + U * U)
    def integrand(eta: float) -> float:
        exponent = (gamma * mt * math.cosh(eta) - U * pt * math.sinh(eta)) / temperature
        p_total = math.sqrt(pt * pt * math.cosh(eta) ** 2 + mass_gev ** 2 * math.sinh(eta) ** 2)
        jacobian = p_total / (mt * math.cosh(eta))
        return jacobian * math.cosh(eta) * mt * safe_exp(-exponent)
    return norm * pt * eta_integral(integrand, -eta_max, eta_max)

eta_cut = 0.8

print("Checking Spectrum Hardness Equivalency:")
y1_static = manuscript_component_scalar(0.5, 1.0, 0.15, 0.0, eta_cut)
y2_static = manuscript_component_scalar(5.0, 1.0, 0.15, 0.0, eta_cut)
hard_static = y2_static / y1_static
print(f"Static (T=0.15 GeV, U=0.0): Hardness = {hard_static:.2e}")

y1_boosted = manuscript_component_scalar(0.5, 1.0, 0.85, 3.0, eta_cut)
y2_boosted = manuscript_component_scalar(5.0, 1.0, 0.85, 3.0, eta_cut)
hard_boosted = y2_boosted / y1_boosted
print(f"Boosted (T=0.85 GeV, U=3.0): Hardness = {hard_boosted:.2e}")

