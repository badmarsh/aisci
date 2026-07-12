import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim

from fitting_pipeline import blast_wave_component_scalar

class ParameterPredictor(nn.Module):
    def __init__(self, input_dim, output_dim=3):
        super().__init__()
        # input: pt spectrum, output: [T, beta, norm]
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim),
            nn.Softplus() # Physical parameters T, norm must be positive
        )

    def forward(self, x):
        return self.net(x)

def generate_synthetic_data(x_values, num_samples=10000):
    X = []
    Y = []
    mass = 0.13957
    for _ in range(num_samples):
        temp = np.random.uniform(0.01, 0.5)
        beta = np.random.uniform(0.01, 0.99)
        norm = np.random.uniform(0.1, 10.0)
        
        y_vals = np.array([blast_wave_component_scalar(x, norm, temp, beta, 1.0, mass) for x in x_values])
        # Add a 5% Gaussian noise layer for robustness
        noise = np.random.normal(0, 0.05 * y_vals)
        y_vals_noisy = y_vals + noise
        
        scale = y_vals_noisy.max() if y_vals_noisy.max() > 0 else 1.0
        y_vals_noisy = y_vals_noisy / scale
        norm_target = norm / scale
        
        X.append(y_vals_noisy)
        Y.append([temp, beta, norm_target])
        
    return torch.tensor(np.array(X), dtype=torch.float32), torch.tensor(np.array(Y), dtype=torch.float32)

def train_ensemble(x_values_tensor, X_train, Y_train, num_models=5, epochs=300):
    ensemble = []
    mse_loss = nn.MSELoss()
    
    for m in range(num_models):
        print(f"Training Model {m+1}/{num_models}...")
        model = ParameterPredictor(input_dim=len(x_values_tensor))
        optimizer = optim.Adam(model.parameters(), lr=1e-3)
        
        model.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            preds = model(X_train)
            
            # L_data: Ensure surrogate matches analytical parameters
            l_data = mse_loss(preds, Y_train)
            
            # L_physics: Enforce hard relativistic constraint beta < 1.0
            # We heavily penalize predictions where beta >= 0.99
            l_physics = torch.mean(torch.relu(preds[:, 1] - 0.99)**2) * 100.0
            
            loss = l_data + l_physics
            loss.backward()
            optimizer.step()
            
        model.eval()
        ensemble.append(model)
    return ensemble

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    
    input_csv = args.run_dir / "fit_input.csv"
    if not input_csv.exists():
        raise FileNotFoundError(f"Missing {input_csv}")
        
    df = pd.read_csv(input_csv)
    bin_id = df["manuscript_bin"].iloc[0]
    bin_data = df[df["manuscript_bin"] == bin_id]
        
    x_values = bin_data["pt_center_gev"].values
    x_tensor = torch.tensor(x_values, dtype=torch.float32)
    
    print("Generating 10,000 synthetic Blast-Wave spectra for PINN training...")
    X_train, Y_train = generate_synthetic_data(x_values, 10000)
    
    # Train Bayesian Deep Ensemble (5 models)
    ensemble = train_ensemble(x_tensor, X_train, Y_train, num_models=5, epochs=400)
    
    print("Inference on experimental data bins...")
    results = []
    for bin_id, group in df.groupby("manuscript_bin"):
        y_vals = group["yield_value"].values
        
        scale = y_vals.max() if y_vals.max() > 0 else 1.0
        y_scaled = y_vals / scale
        
        # In case the group has missing x values or different length, we re-interpolate or just assume it matches.
        # For Robert's data, all bins share the same pT bins structurally in this simulation format.
        x_input = torch.tensor(y_scaled, dtype=torch.float32).unsqueeze(0)
        
        preds = []
        for model in ensemble:
            with torch.no_grad():
                preds.append(model(x_input).numpy()[0])
        
        preds = np.array(preds)
        mean_preds = preds.mean(axis=0)
        std_preds = preds.std(axis=0)
        
        # Scale norm back to real data magnitude
        mean_preds[2] *= scale
        std_preds[2] *= scale
        
        results.append({
            "manuscript_bin": bin_id,
            "T_mean": mean_preds[0],
            "T_std": std_preds[0],
            "beta_mean": mean_preds[1],
            "beta_std": std_preds[1],
            "norm_mean": mean_preds[2],
            "norm_std": std_preds[2],
        })
        
    out_df = pd.DataFrame(results)
    out_csv = args.run_dir / "ml_fit_parameters.csv"
    out_df.to_csv(out_csv, index=False)
    print(f"Saved ML predictions and Bayesian uncertainties to {out_csv}")

if __name__ == "__main__":
    main()
