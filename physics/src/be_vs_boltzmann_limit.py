#!/usr/bin/env python3
import sympy as sp
import numpy as np

# Define symbols
x = sp.symbols('x', positive=True) # x = E/T

# Distributions
f_BE = 1 / (sp.exp(x) - 1)
f_Boltz = sp.exp(-x)

# Fractional error
error = (f_Boltz - f_BE) / f_BE
error_simplified = sp.simplify(error)

print("Symbolic Proof of Bose-Einstein vs Boltzmann Limit:")
print(f"BE Distribution: {f_BE}")
print(f"Boltzmann Approximation: {f_Boltz}")
print(f"Fractional Error (Boltz - BE)/BE: {error_simplified}")
print("This means the Boltzmann approximation underestimates the true yield by exactly exp(-E/T).")

# Evaluate for actual parameters from the manuscript
# Mass of pion ~ 139.5 MeV
m_pi = 139.5
# Lowest pT ~ 100 MeV
pT_min = 100.0
E_min = np.sqrt(m_pi**2 + pT_min**2)

print(f"\nMinimum energy for pions: E_min = {E_min:.1f} MeV")

# Let's check a typical low-T system (e.g. kT1 ~ 130 MeV)
T_low = 130.0
x_low = E_min / T_low
err_low = -np.exp(-x_low)
print(f"\nAt T = {T_low} MeV:")
print(f"E/T = {x_low:.3f}")
print(f"Fractional Error = {err_low*100:.1f}%")

# Let's check the high-T system (kT3 ~ 1000 MeV for high multiplicity)
T_high = 1000.0
x_high = E_min / T_high
err_high = -np.exp(-x_high)
print(f"\nAt T = {T_high} MeV (High Multiplicity Static System):")
print(f"E/T = {x_high:.3f}")
print(f"Fractional Error = {err_high*100:.1f}%")

print("\nCONCLUSION: The Boltzmann approximation is valid for low temperatures (< 200 MeV),")
print("but it catastrophically fails (-80% error) for the high-temperature components (kT3 ~ 1000 MeV)")
print("at low pT. The manuscript MUST use the full Bose-Einstein distribution for a physically")
print("meaningful fit of the hot systems.")
