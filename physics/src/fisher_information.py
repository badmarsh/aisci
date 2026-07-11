#!/usr/bin/env python3
import sympy as sp

# Define symbols
pt, A, T, U = sp.symbols('p_T A T U', positive=True)

# The integrand or the rough shape of the distribution at y=0
# f ~ A * exp(-pT * sqrt(1+U^2) / T) * cosh(U * pT / T)
# In the limit of small U, this is A * exp(-pT/T)
# We will use the exact form for eta=0: E = pT, pz = 0
# U^mu p_mu = E * gamma - pz * gamma * v
# At eta=0, pz=0, so U^mu p_mu = pT * gamma = pT * sqrt(1+U^2)
f = A * sp.exp(-pt * sp.sqrt(1 + U**2) / T)

print("Symbolic Proof of Degeneracy (Over-parameterization):")
print(f"Model function at eta=0: f(pT) = {f}")

# First derivatives (Gradient)
df_dA = sp.diff(f, A)
df_dT = sp.diff(f, T)
df_dU = sp.diff(f, U)

print("\nGradients (Jacobian of the model):")
print(f"df/dA = {df_dA}")
print(f"df/dT = {df_dT}")
print(f"df/dU = {df_dU}")

# Check the limit as U -> 0
limit_df_dU = sp.limit(df_dU, U, 0)
print(f"\nLimit of df/dU as U -> 0: {limit_df_dU}")

# Second derivative wrt U
d2f_dU2 = sp.diff(df_dU, U)
limit_d2f_dU2 = sp.limit(d2f_dU2, U, 0)
print(f"Limit of d²f/dU² as U -> 0: {limit_d2f_dU2}")

print("\nCONCLUSION:")
print("Because df/dU = 0 at U = 0, the first-order response of the model to U vanishes.")
print("This means the Fisher Information Matrix determinant approaches 0 as U -> 0.")
print("For components with small velocities (U << 1), the parameter U is degenerate")
print("with T, leading to the massive uncertainties (like ±0.84) observed in the fit.")
