#!/usr/bin/env python3
import sympy as sp
import json

# Define variables
pt, phi, pz = sp.symbols('p_T phi p_z', real=True, positive=True)

# Define transformation from cylindrical (pT, phi, pz) to Cartesian (px, py, pz)
px = pt * sp.cos(phi)
py = pt * sp.sin(phi)
# pz = pz

# Compute the Jacobian matrix elements
J = sp.Matrix([
    [sp.diff(px, pt), sp.diff(px, phi), sp.diff(px, pz)],
    [sp.diff(py, pt), sp.diff(py, phi), sp.diff(py, pz)],
    [sp.diff(pz, pt), sp.diff(pz, phi), sp.diff(pz, pz)]
])

# Compute determinant
det_J = sp.simplify(J.det())

print("Jacobian Proof:")
print(f"J matrix: {J}")
print(f"Determinant: {det_J}")

if det_J == pt:
    print("SUCCESS: The Jacobian is exactly p_T (which the paper denotes as 'p' in Section 2).")
    print("The volume element d³p = p_T dp_T dφ dp_z is mathematically correct.")
else:
    print("FAILED: The Jacobian does not match.")
