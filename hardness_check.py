import numpy as np

# Let's check the behavior of the Robert model formula for large p
# f(p) ~ exp(-beta * E * gamma) * sinh(beta * gamma * U * p)
# where gamma = sqrt(1+U^2).
# For large p, E ~ p.
# sinh(x) ~ exp(x)/2 for large x.
# So f(p) ~ exp(-beta * gamma * p) * exp(beta * gamma * U * p) = exp(-beta * gamma * p * (1 - U))
# Wait! gamma * (1 - U) = 1 / (gamma * (1 + U)) = sqrt((1-U)/(1+U)).
# If U -> 1, then gamma * (1 - U) -> 0!
# So the effective temperature T_eff = T / (gamma * (1 - U)) = T * sqrt((1+U)/(1-U)).
# This is the Relativistic Doppler Shift!
# If U is very large (U -> 1 in units of c), T_eff can be extremely large!
# This explains how the longitudinal boost hardens the spectrum: the *forward-moving* part of the fireball is Doppler shifted to very high energies.

U_vals = [0.1, 0.5, 0.9, 0.99]
T = 0.14
print("Effective Temperatures (Doppler Shifted) for Forward Particles:")
for U in U_vals:
    gamma = np.sqrt(1 + U**2) # Wait, U is beta * gamma.
    # If U is p_z/m = gamma * beta.
    # Then sqrt(1+U^2) = sqrt(1 + gamma^2 beta^2) = gamma.
    # So gamma = sqrt(1+U^2).
    # And U = beta * gamma.
    # The exponent is -beta * gamma * E + beta * U * p.
    # For large p, E ~ p. Exponent ~ -beta_T * p * (gamma - U).
    # gamma - U = sqrt(1+U^2) - U.
    # If U is very large, sqrt(1+U^2) - U ~ U*(1 + 1/(2U^2)) - U = 1/(2U).
    # So T_eff = T / (gamma - U) ~ T * 2U.
    T_eff = T / (np.sqrt(1 + U**2) - U)
    print(f"U = {U:4.2f} -> T_eff = {T_eff:.3f} GeV")

