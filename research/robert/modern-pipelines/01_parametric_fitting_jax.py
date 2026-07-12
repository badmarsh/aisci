import jax
import jax.numpy as jnp
from jax import grad, jit

def model(params, x):
    """Simple Gaussian model for fitting."""
    mu, sigma, amplitude = params
    return amplitude * jnp.exp(-0.5 * ((x - mu) / sigma)**2)

def mse_loss(params, x, y):
    """Mean squared error loss function."""
    predictions = model(params, x)
    return jnp.mean((predictions - y)**2)

# JIT-compile the loss and its gradient for maximum speed
loss_and_grad = jit(jax.value_and_grad(mse_loss))

def main():
    # Synthetic data
    key = jax.random.PRNGKey(42)
    x = jnp.linspace(-5, 5, 100)
    true_params = jnp.array([0.0, 1.0, 5.0])
    y_true = model(true_params, x)
    y_obs = y_true + 0.1 * jax.random.normal(key, x.shape)
    
    # Initial guess
    params = jnp.array([0.5, 1.5, 3.0])
    learning_rate = 0.1
    
    print("Starting optimization...")
    for i in range(100):
        loss, grads = loss_and_grad(params, x, y_obs)
        params = params - learning_rate * grads
        if i % 20 == 0:
            print(f"Iteration {i:3d} | Loss: {loss:.4f} | Params: {params}")
            
    print(f"\nFinal parameters: {params}")
    print(f"True parameters:  {true_params}")

if __name__ == "__main__":
    main()
