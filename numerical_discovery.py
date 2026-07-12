import numpy as np
import scipy.integrate as integrate
import pandas as pd

# Constants
m = 0.13957 # pion mass (GeV)
T = 0.14    # temperature (GeV)
eta_cut = 0.8 # ALICE central barrel pseudo-rapidity acceptance

# Function to compute dN/dpT dy for a thermal source
def integrand(y, pt, y_boost, T, m):
    mT = np.sqrt(pt**2 + m**2)
    E_prime = mT * np.cosh(y - y_boost)
    # The thermal distribution is ~ exp(-E'/T)
    # However, phase space volume element is d3p/E = pt dpt dy dphi
    # We are computing dN/dpt. So we multiply by pt.
    return pt * np.exp(-E_prime / T)

# Function to integrate over detector acceptance
def compute_spectrum(pt_array, y_boost, T, m, eta_cut):
    spectrum = []
    for pt in pt_array:
        # We integrate y from -eta_cut to eta_cut (approximating y ~ eta for high pT)
        val, _ = integrate.quad(integrand, -eta_cut, eta_cut, args=(pt, y_boost, T, m))
        spectrum.append(val)
    return np.array(spectrum)

# Array of transverse momenta
pt_array = np.linspace(0.5, 5.0, 10)

# Evaluate for static system (y_boost = 0) and highly boosted system (y_boost = 3)
spec_static = compute_spectrum(pt_array, y_boost=0.0, T=T, m=m, eta_cut=eta_cut)
spec_boosted = compute_spectrum(pt_array, y_boost=3.0, T=T, m=m, eta_cut=eta_cut)

# Also compute the theoretical invariant spectrum (integral from -infty to infty)
# This is proportional to 2 * pt * K1(mT/T) -- wait, for exp(-E/T) it's K0(mT/T)
# Actually, the full integral of exp(-mT*cosh(y-yb)/T) is 2*K0(mT/T)
import scipy.special as sp
def invariant_spectrum(pt_array, T, m):
    spectrum = []
    for pt in pt_array:
        mT = np.sqrt(pt**2 + m**2)
        spectrum.append(pt * 2 * sp.kn(0, mT/T))
    return np.array(spectrum)

spec_invariant = invariant_spectrum(pt_array, T=T, m=m)

# Let's compare the slopes (effective temperatures)
df = pd.DataFrame({
    'pT (GeV)': pt_array,
    'Static (finite eta)': spec_static,
    'Boosted (finite eta)': spec_boosted,
    'Invariant (infinite eta)': spec_invariant
})

print(df.to_string())

# Calculate ratio of Yield(pT=5) / Yield(pT=0.5) to measure hardness
hardness_static = spec_static[-1] / spec_static[0]
hardness_boosted = spec_boosted[-1] / spec_boosted[0]
hardness_inv = spec_invariant[-1] / spec_invariant[0]

print("\n--- Spectrum Hardness (Yield at pT=5 / Yield at pT=0.5) ---")
print(f"Invariant (infinite acceptance): {hardness_inv:.2e}")
print(f"Static (finite acceptance):      {hardness_static:.2e}")
print(f"Boosted (finite acceptance):     {hardness_boosted:.2e}")

