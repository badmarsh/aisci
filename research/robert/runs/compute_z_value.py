import pandas as pd
from scipy.stats import chi2, norm
import uproot
import numpy as np

# Load the model comparison
df = pd.read_csv('/home/ubuntu/aisci/research/robert/runs/2026-05-30-multiplicity-fit/model_comparison.csv')

# Let's focus on bin 101-125
df_bin = df[df['group_label'] == '101-125']

# Get chi2/ndf for Tsallis 1c and Robert 3c
# Assuming ndf = 47 points - params. 
# Tsallis 1c params = 3. ndf = 44
# Robert 3c params = 3 norms + 3 T + 2 U = 8 params. ndf = 39

tsallis_row = df_bin[(df_bin['model_name'] == 'tsallis') & (df_bin['component_count'] == 1)].iloc[0]
robert_row = df_bin[(df_bin['model_name'] == 'manuscript_juttner') & (df_bin['component_count'] == 3)].iloc[0]

chi2_tsallis = tsallis_row['chi2_ndf'] * 44
chi2_robert = robert_row['chi2_ndf'] * 39

dchi2 = chi2_tsallis - chi2_robert
dndf = 44 - 39

if dchi2 > 0:
    p_val = chi2.sf(dchi2, dndf)
    z_val = norm.isf(p_val)
else:
    p_val = 1.0
    z_val = 0.0

print(f"Tsallis chi2: {chi2_tsallis:.2f}")
print(f"Robert chi2: {chi2_robert:.2f}")
print(f"Delta chi2: {dchi2:.2f}")
print(f"p-value: {p_val:.2e}")
print(f"Z-value (Sigma): {z_val:.2f} sigma")

# Create a ROOT file for rooagent to plot
spectra = pd.read_csv('/home/ubuntu/aisci/research/robert/runs/2026-05-30-multiplicity-fit/hepdata_pt_spectra.csv')
spectra_bin = spectra[spectra['group_label'] == '101-125']

with uproot.recreate('/home/ubuntu/aisci/research/robert/runs/results.root') as f:
    f['tree'] = {'pt': spectra_bin['pt'].values, 'yield': spectra_bin['value'].values}
    
print("Created results.root")
