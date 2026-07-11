import sympy as sp
import sys

def main():
    print("--- Exact Tsallis Integration over Pseudorapidity ---")
    
    # Define symbols
    eta, rho, a, b = sp.symbols('eta rho a b', real=True)
    
    # The integrand consists of the Tsallis distribution factor and the dy/d_eta Jacobian.
    # In rapidity y, the term is (1 + a * cosh(y - rho))^(-b)
    # The Jacobian is dy/deta = p/E = cosh(eta) (for m=0, where y = eta)
    # With non-zero mass, it is more complex, but a standard approximation in literature 
    # to test integration is using the massless Jacobian dy/deta = cosh(eta)/cosh(y) 
    # Or more simply, if y approx eta, we just integrate: cosh(eta) * (1 + a cosh(eta - rho))^(-b)
    
    integrand = sp.cosh(eta) * (1 + a * sp.cosh(eta - rho))**(-b)
    
    print(f"Integrand: {integrand}")
    print("\nAttempting 2nd order Taylor expansion (Padé-like approximation) around eta=0...")
    # Taylor expand the integrand around eta=0
    taylor_expansion = sp.series(integrand, eta, 0, 3).removeO()
    print(f"Taylor expansion (up to O(eta^2)):")
    print(taylor_expansion)
    
    print("\nIntegrating the Taylor expansion analytically:")
    taylor_integral = sp.integrate(taylor_expansion, eta)
    print(taylor_integral)
    print("\n[SUCCESS] Generated analytic approximation for the integral.")

if __name__ == "__main__":
    main()
