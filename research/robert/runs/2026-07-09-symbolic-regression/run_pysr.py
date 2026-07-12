import pandas as pd
import numpy as np
from pysr import PySRRegressor
import os

def main():
    run_dir = "research/robert/runs/2026-07-09-symbolic-regression"
    os.makedirs(run_dir, exist_ok=True)
    
    # Load data
    data_path = "libs/physics-core/data/fit_input.csv"
    df = pd.read_csv(data_path)
    
    # Filter for Table 1 (Pion) and a specific bin, e.g., '21-30'
    bins = df[df['source_table'] == 'Table 1']['multiplicity_selection'].unique()
    print(f"Found bins: {bins}")
    
    for bin_name in ['21-30', '126-150']: # Test with lowest and highest multiplicity
        print(f"\n--- Running PySR for bin {bin_name} ---")
        df_bin = df[(df['multiplicity_selection'] == bin_name) & (df['source_table'] == 'Table 1')].copy()
        
        X = df_bin[['pt_center_gev']].values
        y = df_bin['yield_value'].values
        weights = 1.0 / (df_bin['stat_error'].values ** 2)
        
        # We need a custom loss for chi2: weight * (pred - target)^2
        # However, it's easier to just pass weights and use the default MSE loss
        # PySR's default loss when weights are passed is exactly sum(weights * (y - y_pred)^2) / sum(weights)
        
        model = PySRRegressor(
            niterations=100,  # Run for enough iterations
            binary_operators=["+", "*", "-", "/"],
            unary_operators=["exp", "log", "sqrt"],
            loss="loss(prediction, target, weight) = weight * (prediction - target)^2",
            weights=weights,
            maxsize=20, # Max complexity
            temp_equation_file=True,
            tempdir=run_dir,
            verbosity=1,
            procs=4, # Use 4 processes
        )
        
        # Fit the model
        model.fit(X, y, weights=weights)
        
        # Save results
        out_csv = f"{run_dir}/pysr_results_bin_{bin_name}.csv"
        model.equations_.to_csv(out_csv, index=False)
        print(f"Saved results to {out_csv}")
        
        # Best model
        print("Best equation discovered (by loss/complexity):")
        print(model.sympy())

if __name__ == "__main__":
    main()
