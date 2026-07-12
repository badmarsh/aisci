import sympy as sp

def prove_singularity():
    pT, mT, eta, T_kin, U = sp.symbols('pT mT eta T_kin U', real=True)
    gamma = sp.sqrt(1 + U**2)
    
    # Exponent for moving component
    exponent = (gamma * mT * sp.cosh(eta) - U * pT * sp.sinh(eta)) / T_kin
    
    # We ignore the Jacobian dy/deta for the shape of the derivative because it's even in eta
    # jacobian = p_total / (mT * cosh(eta)) which is even in eta
    # Let's just look at the term being integrated:
    # Juttner integrand (simplified to show the U dependence)
    integrand = sp.exp(-exponent)
    
    # Derivative w.r.t U
    d_integrand_dU = sp.diff(integrand, U)
    
    # Evaluate at U = 0
    d_dU_at_0 = d_integrand_dU.subs(U, 0)
    
    print("Derivative of integrand at U=0:")
    print(d_dU_at_0)
    
    # Note that the remaining terms depend on sinh(eta), which is odd
    # The integration limits are -eta_max to +eta_max, so the integral is 0.

if __name__ == '__main__':
    prove_singularity()
