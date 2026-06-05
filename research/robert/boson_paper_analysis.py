import numpy as np
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("PART 1: DERIVATION VERIFICATION")
print("=" * 80)

print("\nPhase space: d3p = p*dp*d(phi)*dpz (Jacobian = p)")
print("Delta function: delta(p^2-m^2) -> 1/(2*sqrt(p^2+m^2)) after p0 integration")
print("pz integration: integral exp(beta*U*pz) from -sqrt(p^2-pT^2) to +sqrt(p^2-pT^2)")
print("  = 2*sinh(beta*U*sqrt(p^2-pT^2)) / (beta*U)")
print()
print("Combined: p * 1/(2*sqrt(p^2+m^2)) * 2*sinh/(beta*U) = p*sinh/(sqrt(p^2+m^2)*beta*U)")
print()
print("CORRECT unnormalized PDF: f(p) = p/sqrt(p^2+m^2) * sinh(beta*U*sqrt(p^2-pT^2)*cos(theta_cut)) / (beta*U) * exp(-beta*sqrt(p^2+m^2)*sqrt(1+U^2))")

# The manuscript text shows "p*sqrt(p^2+m^2)" which is likely an OCR error
# or a typo in the formula. The correct derivation gives p/sqrt(p^2+m^2).
