import pandas as pd
import numpy as np
from iminuit import Minuit
from iminuit.cost import LeastSquares
import matplotlib.pyplot as plt

def boltzmann_soft(pt, A, T):
    return A * np.exp(-pt / T)

def run_biro_analysis():
    # Load ALICE 13 TeV data
    df = pd.read_csv('/home/ubuntu/aisci/libs/physics-core/data/fit_input_ins1735345.csv')
    
    results = []
    
    for bin_name in df['manuscript_bin'].unique():
        bin_data = df[df['manuscript_bin'] == bin_name]
        pt = bin_data['pt_center_gev'].values
        yield_ = bin_data['yield_value'].values
        stat_err = bin_data['stat_error'].values
        
        # Fit range 0.15 < pT < p0. p0 is found by minimizing |chi2/ndf - 1|
        best_p0 = None
        best_chi2_diff = float('inf')
        best_T = None
        best_chi2_ndf = None
        
        for p0 in np.linspace(0.8, 1.3, 50):
            mask = (pt >= 0.15) & (pt <= p0)
            if np.sum(mask) < 3:
                continue
                
            pt_fit = pt[mask]
            y_fit = yield_[mask]
            y_err_fit = stat_err[mask]
            
            least_squares = LeastSquares(pt_fit, y_fit, y_err_fit, boltzmann_soft)
            m = Minuit(least_squares, A=y_fit[0], T=0.2)
            m.limits['A'] = (0, None)
            m.limits['T'] = (0.01, 1.0)
            m.migrad()
            
            if m.valid:
                chi2 = m.fval
                ndf = len(pt_fit) - 2
                chi2_ndf = chi2 / ndf if ndf > 0 else float('inf')
                
                diff = abs(chi2_ndf - 1)
                if diff < best_chi2_diff:
                    best_chi2_diff = diff
                    best_p0 = p0
                    best_T = m.values['T']
                    best_chi2_ndf = chi2_ndf
        
        results.append({
            'bin': bin_name,
            'p0': best_p0,
            'T': best_T,
            'chi2_ndf': best_chi2_ndf
        })
        print(f"Bin {bin_name}: p0={best_p0:.2f}, T={best_T:.4f} GeV, chi2/ndf={best_chi2_ndf:.2f}")

if __name__ == "__main__":
    run_biro_analysis()
