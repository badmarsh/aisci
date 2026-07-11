import jax
import jax.numpy as jnp
from jax.scipy.special import i0e
import scipy.special as sc
import numpy as np
import pandas as pd
import argparse
import sys
import os
import numpyro
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS
import corner
import matplotlib.pyplot as plt

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


def bgbw_model_pred(norm, temperature, beta_s, n_value, pt_data, mass_gev):
    mt = jnp.sqrt(mass_gev**2 + pt_data**2)

    N_steps = 200
    r_frac = jnp.linspace(0.0, 1.0, N_steps)
    dr = 1.0 / (N_steps - 1)

    beta_r = jnp.minimum(beta_s * (r_frac ** n_value), 0.999999)
    rho = jnp.arctanh(beta_r)

    pt_grid = jnp.expand_dims(pt_data, 1)
    mt_grid = jnp.expand_dims(mt, 1)
    rho_grid = jnp.expand_dims(rho, 0)
    r_frac_grid = jnp.expand_dims(r_frac, 0)

    arg_I = pt_grid * jnp.sinh(rho_grid) / temperature
    arg_K = mt_grid * jnp.cosh(rho_grid) / temperature
    
    integrand = (
        r_frac_grid
        * mt_grid
        * i0e(arg_I)
        * k1e_jax(arg_K)
        * jnp.exp(arg_I - arg_K)
    )

    integral = jnp.trapezoid(integrand, dx=dr, axis=-1)
    return norm * pt_data * integral

def numpyro_model(pt_data, error_data, mass_gev, yield_data=None):
    # Priors
    norm = numpyro.sample('norm', dist.Uniform(1.0, 100000.0))
    temperature = numpyro.sample('T_kin', dist.Uniform(0.01, 0.3))
    beta_s = numpyro.sample('beta_s', dist.Uniform(0.1, 0.99))
    n_value = numpyro.sample('n', dist.Uniform(0.1, 5.0))

    # Expected yield
    mu = bgbw_model_pred(norm, temperature, beta_s, n_value, pt_data, mass_gev)

    # Likelihood
    # Chi2 statistic corresponds to Gaussian likelihood with known sigma
    numpyro.sample('obs', dist.Normal(mu, error_data), obs=yield_data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, default="physics/data/fit_input_ins1735345_v0m_unfolded.csv")
    parser.add_argument("--run-dir", type=str, default="research/robert/runs/2026-07-11-mcmc")
    parser.add_argument("--samples", type=int, default=500, help="Number of posterior samples")
    args = parser.parse_args()

    os.makedirs(args.run_dir, exist_ok=True)
    df = pd.read_csv(args.data)
    
    # Identify unique bins
    bins = df['multiplicity_selection'].unique()
    print(f"Found {len(bins)} bins. Running MCMC for each...")
    
    # We will use GPU if available, else CPU.
    try:
        numpyro.set_platform("gpu")
        print("Set Numpyro to GPU.")
    except Exception as e:
        print(f"Failed to set GPU, using default: {e}")
    
    mass_gev = 0.13957  # Pion mass
    
    for b in bins:
        print(f"\n--- Running NUTS for bin {b} ---")
        df_bin = df[df['multiplicity_selection'] == b].copy()
        
        pt_data = jnp.array(df_bin['pt_center_gev'].values, dtype=jnp.float64)
        yield_data = jnp.array(df_bin['yield_value'].values, dtype=jnp.float64)
        error_data = jnp.array(df_bin['stat_error'].values, dtype=jnp.float64)
        
        nuts_kernel = NUTS(numpyro_model, target_accept_prob=0.8)
        mcmc = MCMC(nuts_kernel, num_warmup=200, num_samples=args.samples, progress_bar=False)
        mcmc.run(jax.random.PRNGKey(42), pt_data=pt_data, error_data=error_data, mass_gev=mass_gev, yield_data=yield_data)
        
        # Save corner plot
        samples = mcmc.get_samples()
        # Create corner plot
        data = np.vstack([samples['T_kin'], samples['beta_s']]).T
        fig = corner.corner(data, labels=["$T_{kin}$ [GeV]", "$\\beta_s$"], show_titles=True, title_kwargs={"fontsize": 12})
        fig.savefig(f"{args.run_dir}/corner_bin_{b}.png")
        plt.close(fig)
        
        print(f"Saved corner plot to {args.run_dir}/corner_bin_{b}.png")

if __name__ == "__main__":
    main()
