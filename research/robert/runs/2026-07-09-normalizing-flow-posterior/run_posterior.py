import sys
import os
import jax
import jax.numpy as jnp
import numpy as np
import pandas as pd
import blackjax
import corner
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import argparse

# Add root to pythonpath
sys.path.append(os.getcwd())
from physics.src.bgbw_jax_autodiff import bgbw_likelihood

def main():
    run_dir = "research/robert/runs/2026-07-09-normalizing-flow-posterior"
    os.makedirs(run_dir, exist_ok=True)
    
    bin_name = "21-30"
    df = pd.read_csv("libs/physics-core/data/fit_input.csv")
    df_bin = df[(df['multiplicity_selection'] == bin_name) & (df['source_table'] == 'Table 1')].copy()
    
    pt_data = jnp.array(df_bin['pt_center_gev'].values, dtype=jnp.float64)
    yield_data = jnp.array(df_bin['yield_value'].values, dtype=jnp.float64)
    error_data = jnp.array(df_bin['stat_error'].values, dtype=jnp.float64)
    mass_gev = 0.13957

    # Log posterior
    def log_prob(params_dict):
        # Unpack from dict for BlackJAX
        p = jnp.array([params_dict["norm"], params_dict["T"], params_dict["beta_s"], params_dict["n"]])
        
        # Priors: Uniform
        in_bounds = (
            (p[0] > 0) & (p[0] < 100000) &
            (p[1] > 0.01) & (p[1] < 0.3) &
            (p[2] > 0.1) & (p[2] < 0.999) &
            (p[3] > 0.1) & (p[3] < 5.0)
        )
        
        # If out of bounds, return -inf
        chi2 = bgbw_likelihood(p, pt_data, yield_data, error_data, mass_gev)
        return jnp.where(in_bounds, -0.5 * chi2, -jnp.inf)

    # Find MAP (Maximum A Posteriori) using L-BFGS-B (from previous exact JAX grad)
    print("Finding MAP estimate...")
    init_params = jnp.array([1000.0, 0.10, 0.8, 1.0], dtype=jnp.float64)
    
    # We must wrap for SciPy
    grad_fn = jax.grad(bgbw_likelihood)
    def loss_wrap(p):
        return np.array(bgbw_likelihood(jnp.array(p), pt_data, yield_data, error_data, mass_gev))
    def grad_wrap(p):
        return np.array(grad_fn(jnp.array(p), pt_data, yield_data, error_data, mass_gev))
        
    bounds = [(1.0, 100000.0), (0.01, 0.3), (0.1, 0.99), (0.1, 5.0)]
    res = minimize(loss_wrap, init_params, jac=grad_wrap, method='L-BFGS-B', bounds=bounds)
    
    map_p = res.x
    print(f"MAP Params: {map_p}")
    
    initial_position = {
        "norm": map_p[0],
        "T": map_p[1],
        "beta_s": map_p[2],
        "n": map_p[3]
    }
    
    # Compute inverse Hessian for mass matrix
    print("Computing exact Hessian at MAP for mass matrix...")
    hessian_fn = jax.jacrev(jax.jacrev(bgbw_likelihood))
    H = hessian_fn(jnp.array(map_p), pt_data, yield_data, error_data, mass_gev)
    cov = 2.0 * jnp.linalg.inv(H)
    
    # Use NUTS (No-U-Turn Sampler)
    print("Setting up NUTS sampler...")
    
    # We use blackjax's window adaptation
    adapt = blackjax.window_adaptation(blackjax.nuts, log_prob)
    rng_key = jax.random.PRNGKey(42)
    
    # Adapt
    print("Running adaptation phase (burn-in)...")
    (state, parameters), _ = adapt.run(rng_key, initial_position, num_steps=500)
    
    # Sample
    print("Running NUTS sampling...")
    kernel = blackjax.nuts(log_prob, **parameters).step
    
    @jax.jit
    def one_step(state, rng_key):
        return kernel(rng_key, state)
        
    keys = jax.random.split(rng_key, 2000)
    
    states = []
    current_state = state
    for i, key in enumerate(keys):
        current_state, _ = one_step(current_state, key)
        states.append(current_state.position)
        if (i+1) % 500 == 0:
            print(f"Sampled {i+1}/2000")
            
    # Convert to array
    samples = np.array([
        [s["norm"], s["T"], s["beta_s"], s["n"]] for s in states
    ])
    
    # Plot Corner
    print("Generating corner plot...")
    fig = corner.corner(
        samples,
        labels=[r"Norm", r"$T_{\mathrm{kin}}$", r"$\beta_s$", r"$n$"],
        truths=map_p,
        show_titles=True,
        title_fmt=".4f"
    )
    fig.savefig(f"{run_dir}/posterior_corner_bin_{bin_name}.png")
    
    # Save samples
    df_samples = pd.DataFrame(samples, columns=["norm", "T", "beta_s", "n"])
    df_samples.to_csv(f"{run_dir}/mcmc_samples_bin_{bin_name}.csv", index=False)
    
    print(f"Saved posterior corner plot to {run_dir}/posterior_corner_bin_{bin_name}.png")

if __name__ == "__main__":
    main()
