import os
import sys
import jax
import jax.numpy as jnp
import numpy as np
import pandas as pd
from scipy.optimize import minimize

sys.path.append(os.getcwd())
from physics.src.bgbw_jax_autodiff import bgbw_likelihood

def pysr_model(params, pt_data):
    """
    The unified PySR discovered phenomenological model:
    y = A * exp(-alpha * p_T) / (p_T^{3/2} + C * p_T * exp(-alpha * p_T) + D * exp(-alpha * p_T))
    params: [A, alpha, C, D]
    """
    A, alpha, C, D = params
    term = jnp.exp(-alpha * pt_data)
    return (A * term) / (pt_data**1.5 + C * pt_data * term + D * term)

def pysr_chi2(params, pt_data, yield_data, error_data):
    pred = pysr_model(params, pt_data)
    return jnp.sum(((pred - yield_data) / error_data) ** 2)

# JIT and grad
pysr_chi2_jit = jax.jit(pysr_chi2)
pysr_grad = jax.jit(jax.grad(pysr_chi2))

def fit_bin(df, bin_name, mass_gev=0.13957):
    df_bin = df[(df['multiplicity_selection'] == bin_name) & (df['source_table'] == 'Table 1')]
    pt_data = jnp.array(df_bin['pt_center_gev'].values, dtype=jnp.float64)
    yield_data = jnp.array(df_bin['yield_value'].values, dtype=jnp.float64)
    error_data = jnp.array(df_bin['stat_error'].values, dtype=jnp.float64)
    
    # 1. Fit BGBW
    def bgbw_wrap(p):
        return np.array(bgbw_likelihood(jnp.array(p), pt_data, yield_data, error_data, mass_gev))
    bgbw_grad_fn = jax.grad(bgbw_likelihood)
    def bgbw_grad_wrap(p):
        return np.array(bgbw_grad_fn(jnp.array(p), pt_data, yield_data, error_data, mass_gev))
        
    bounds_bgbw = [(1.0, 100000.0), (0.01, 0.3), (0.1, 0.99), (0.1, 5.0)]
    init_bgbw = [1000.0, 0.10, 0.8, 1.0]
    res_bgbw = minimize(bgbw_wrap, init_bgbw, jac=bgbw_grad_wrap, method='L-BFGS-B', bounds=bounds_bgbw)
    chi2_bgbw = res_bgbw.fun
    
    # 2. Fit PySR Model
    def pysr_wrap(p):
        return np.array(pysr_chi2_jit(jnp.array(p), pt_data, yield_data, error_data))
    def pysr_grad_wrap(p):
        return np.array(pysr_grad(jnp.array(p), pt_data, yield_data, error_data))
    
    # Run a multi-start or just provide decent bounds. The formula is very robust.
    bounds_pysr = [(0.0, 10000.0), (0.01, 10.0), (-100.0, 100.0), (0.001, 10.0)]
    init_pysr = [1.33, 0.66, -0.93, 0.34] # Mix of low/high bin PySR outputs
    res_pysr = minimize(pysr_wrap, init_pysr, jac=pysr_grad_wrap, method='L-BFGS-B', bounds=bounds_pysr)
    chi2_pysr = res_pysr.fun
    
    ndf = len(pt_data) - 4
    
    return chi2_bgbw, chi2_pysr, ndf, res_pysr.x

def main():
    data_path = "libs/physics-core/data/fit_input.csv"
    df = pd.read_csv(data_path)
    bins = df[df['source_table'] == 'Table 1']['multiplicity_selection'].unique()
    
    results = []
    print(f"{'Bin':<15} | {'BGBW χ²/ndf':<15} | {'PySR χ²/ndf':<15} | {'Winner':<10}")
    print("-" * 65)
    
    for bin_name in bins:
        chi2_bgbw, chi2_pysr, ndf, pysr_p = fit_bin(df, bin_name)
        bgbw_norm = chi2_bgbw / ndf
        pysr_norm = chi2_pysr / ndf
        winner = "PySR" if pysr_norm < bgbw_norm else "BGBW"
        
        print(f"{bin_name:<15} | {bgbw_norm:<15.2f} | {pysr_norm:<15.2f} | {winner:<10}")
        results.append({
            "bin": bin_name,
            "chi2_ndf_bgbw": bgbw_norm,
            "chi2_ndf_pysr": pysr_norm,
            "pysr_A": pysr_p[0],
            "pysr_alpha": pysr_p[1],
            "pysr_C": pysr_p[2],
            "pysr_D": pysr_p[3]
        })
        
    df_res = pd.DataFrame(results)
    df_res.to_csv("research/robert/runs/2026-07-09-symbolic-regression/pysr_validation.csv", index=False)
    print("\nValidation complete. PySR phenomenological model tested across all bins.")

if __name__ == "__main__":
    main()
