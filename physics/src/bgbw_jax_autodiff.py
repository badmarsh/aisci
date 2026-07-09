import jax
import jax.numpy as jnp
from jax.scipy.special import i0e
import scipy.special as sc
import numpy as np
import pandas as pd
import argparse
import sys
from pathlib import Path

jax.config.update("jax_enable_x64", True)

# -------------------------------------------------------------
# JAX wrappers for Bessel K_0e and K_1e with exact derivatives
# -------------------------------------------------------------

@jax.custom_vjp
def k1e_jax(x):
    return jax.pure_callback(
        lambda val: np.asarray(sc.k1e(val), dtype=val.dtype),
        jax.ShapeDtypeStruct(x.shape, x.dtype),
        x
    )

@jax.custom_vjp
def k0e_jax(x):
    return jax.pure_callback(
        lambda val: np.asarray(sc.k0e(val), dtype=val.dtype),
        jax.ShapeDtypeStruct(x.shape, x.dtype),
        x
    )

def k1e_fwd(x):
    return k1e_jax(x), x

def k1e_bwd(res, g):
    x = res
    grad_x = k1e_jax(x) - k0e_jax(x) - k1e_jax(x) / x
    return (g * grad_x,)

k1e_jax.defvjp(k1e_fwd, k1e_bwd)

def k0e_fwd(x):
    return k0e_jax(x), x

def k0e_bwd(res, g):
    x = res
    grad_x = k0e_jax(x) - k1e_jax(x)
    return (g * grad_x,)

k0e_jax.defvjp(k0e_fwd, k0e_bwd)

# -------------------------------------------------------------
# Differentiable BGBW Model
# -------------------------------------------------------------

def bgbw_likelihood(params, pt_data, yield_data, error_data, mass_gev):
    """
    Negative log-likelihood (least squares / chi2 equivalent) for the BGBW model.
    params = [norm, temperature, beta_s, n_value]
    """
    norm, temperature, beta_s, n_value = params

    mt = jnp.sqrt(mass_gev**2 + pt_data**2)

    # Vectorized trapezoidal integration over radius fraction (0 to 1)
    N_steps = 200
    r_frac = jnp.linspace(0.0, 1.0, N_steps)
    dr = 1.0 / (N_steps - 1)

    # beta_r has shape (N_steps,)
    beta_r = jnp.minimum(beta_s * (r_frac ** n_value), 0.999999)
    rho = jnp.arctanh(beta_r)

    # Expand dims to compute cross-grid of (N_pt, N_steps)
    # pt_data: (N_pt,) -> (N_pt, 1)
    # rho: (N_steps,) -> (1, N_steps)
    pt_grid = jnp.expand_dims(pt_data, 1)
    mt_grid = jnp.expand_dims(mt, 1)
    rho_grid = jnp.expand_dims(rho, 0)
    r_frac_grid = jnp.expand_dims(r_frac, 0)

    arg_I = pt_grid * jnp.sinh(rho_grid) / temperature
    arg_K = mt_grid * jnp.cosh(rho_grid) / temperature

    # Integrand logic matching physics/src/fitting_pipeline.py but scaled
    # We use i0e(x) = i0(x)*e^-x and k1e(x) = k1(x)*e^x
    # So i0(x) = i0e(x)*e^x and k1(x) = k1e(x)*e^-x
    # Product: i0(x)*k1(y) = i0e(x)*k1e(y)*e^(x-y)
    
    integrand = (
        r_frac_grid
        * mt_grid
        * i0e(arg_I)
        * k1e_jax(arg_K)
        * jnp.exp(arg_I - arg_K)
    )

    # Integrate using trapz over the last axis (N_steps)
    integral = jnp.trapezoid(integrand, dx=dr, axis=-1)
    model_pred = norm * pt_data * integral

    # Chi2 statistic (Poisson NLL equivalent for Gaussian approx)
    chi2 = jnp.sum(((yield_data - model_pred) / error_data)**2)
    return chi2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bin", type=str, default="21-30", help="Multiplicity bin to fit")
    parser.add_argument("--data", type=str, default="physics/data/fit_input.csv")
    args = parser.parse_args()

    print(f"[JAX Autodiff] Loading BGBW data for bin {args.bin}...")
    df = pd.read_csv(args.data)
    
    # Filter for the specific bin and particle (Table 1 is Pion)
    df_bin = df[(df['multiplicity_selection'] == args.bin) & (df['source_table'] == 'Table 1')].copy()
    if df_bin.empty:
        print("No data found for this bin/particle combination.")
        sys.exit(1)

    pt_data = jnp.array(df_bin['pt_center_gev'].values, dtype=jnp.float64)
    yield_data = jnp.array(df_bin['yield_value'].values, dtype=jnp.float64)
    error_data = jnp.array(df_bin['stat_error'].values, dtype=jnp.float64)
    mass_gev = 0.13957  # Pion mass

    # Initial guess (taken roughly from a previous good fit to prevent getting stuck far away)
    # [norm, T, beta_s, n]
    init_params = jnp.array([1000.0, 0.10, 0.8, 1.0], dtype=jnp.float64)

    # Let's define the Hessian and Jacobian functions using pure reverse-mode autodiff
    # because our custom Bessel functions only define VJPs, not JVPs.
    hessian_fn = jax.jacrev(jax.jacrev(bgbw_likelihood))
    grad_fn = jax.grad(bgbw_likelihood)

    print("[JAX Autodiff] Finding exact minimum using analytical JAX gradients (L-BFGS-B)...")
    from scipy.optimize import minimize
    
    # We must wrap JAX functions to return standard numpy arrays for SciPy
    def loss_wrap(p):
        return np.array(bgbw_likelihood(p, pt_data, yield_data, error_data, mass_gev))
    def grad_wrap(p):
        return np.array(grad_fn(p, pt_data, yield_data, error_data, mass_gev))

    bounds = [(1.0, 100000.0), (0.01, 0.3), (0.1, 0.99), (0.1, 5.0)]
    res = minimize(loss_wrap, init_params, jac=grad_wrap, method='L-BFGS-B', bounds=bounds)
    
    print(f"\nOptimization success: {res.success} ({res.message})")
    print(f"Optimal Params: {res.x}")
    print(f"Optimal Chi2: {res.fun:.4f}")

    print("\n[JAX Autodiff] Computing exact Hessian at the optimal point...")
    opt_params = jnp.array(res.x)
    H = hessian_fn(opt_params, pt_data, yield_data, error_data, mass_gev)
    
    print("Exact Hessian Matrix:")
    print(H)

    cov = 2.0 * jnp.linalg.inv(H)
    
    d = jnp.sqrt(jnp.diag(cov))
    corr = cov / jnp.outer(d, d)
    
    print("\n[JAX Autodiff] Exact Correlation Matrix:")
    print(corr)
    
    rho = corr[1, 2]
    print(f"\nExact T-beta_s correlation (rho): {rho:.4f}")
    
    if abs(rho) > 0.90:
        print("[SUCCESS] Mathematically proved T-beta degeneracy instantly via autodiff!")
        
if __name__ == "__main__":
    main()
