import sympy as sp

# Variables
pT, mT, pz, y, y_boost, T = sp.symbols('p_T m_T p_z y y_{boost} T', real=True, positive=True)
eta_cut = sp.symbols('eta_{cut}', real=True, positive=True)

# Lab frame energy: E = mT * cosh(y)
# Boosted thermal exponent: - (mT * cosh(y - y_boost)) / T
integrand = sp.exp(- (mT * sp.cosh(y - y_boost)) / T)

print("Integrand:")
sp.pprint(integrand)

# We want to integrate from -eta_cut to eta_cut (approximate y ~ eta for high pT)
# Sympy might not be able to do this analytically, but let's try a Taylor expansion or indefinite integral
try:
    # Let's try indefinite integral
    indef = sp.integrate(integrand, y)
    print("Indefinite integral:")
    sp.pprint(indef)
except Exception as e:
    print("Cannot integrate exactly.")

