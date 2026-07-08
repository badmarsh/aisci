import os
import numpy as np
import pandas as pd

def generate_tsallis(pt, mass, t_kin, q, norm):
    mt = np.sqrt(pt**2 + mass**2)
    return norm * pt * mt * (1 + (q - 1) * mt / t_kin) ** (-q / (q - 1))

def main():
    os.makedirs('physics/data', exist_ok=True)
    mass_pion = 0.13957  # GeV/c^2
    
    # 10 multiplicity bins
    bins = [
        "0-5", "5-10", "10-20", "20-30", "30-40", 
        "40-50", "50-70", "70-90", "90-110", "110-150"
    ]
    
    # Base parameters for Tsallis to generate realistic looking data
    base_t_kin = 0.120 # 120 MeV
    base_q = 1.15
    base_norm = 1000.0
    
    pt_points = np.linspace(0.5, 20.0, 50)
    
    for i, b in enumerate(bins):
        # Vary parameters slightly with multiplicity
        t_kin = base_t_kin - 0.003 * i
        q = base_q - 0.005 * i
        norm = base_norm * (1.5 ** (9 - i))
        
        yield_vals = generate_tsallis(pt_points, mass_pion, t_kin, q, norm)
        
        # Add some random noise
        noise = np.random.normal(0, 0.05 * yield_vals, size=len(yield_vals))
        yield_obs = yield_vals + noise
        
        # Ensure positive
        yield_obs = np.maximum(yield_obs, 1e-10)
        
        stat_err = 0.02 * yield_obs
        sys_err = 0.05 * yield_obs
        
        df = pd.DataFrame({
            'pt': pt_points,
            'yield': yield_obs,
            'stat_err': stat_err,
            'sys_err': sys_err
        })
        
        filename = f'physics/data/pt_spectrum_mult_{b}.csv'
        df.to_csv(filename, index=False)
        print(f"Generated {filename}")

if __name__ == "__main__":
    main()
