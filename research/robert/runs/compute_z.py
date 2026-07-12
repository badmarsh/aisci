import pandas as pd
from scipy.stats import chi2, norm

# Load the model comparison
df = pd.read_csv('/home/ubuntu/aisci/research/robert/runs/2026-05-30-multiplicity-fit/model_comparison.csv')
df_bin = df[df['group_label'] == '101-125']

tsallis_row = df_bin[(df_bin['model_name'] == 'tsallis') & (df_bin['component_count'] == 1)].iloc[0]
robert_row = df_bin[(df_bin['model_name'] == 'manuscript_juttner') & (df_bin['component_count'] == 3)].iloc[0]

# 47 data points
chi2_tsallis = tsallis_row['chi2_ndf'] * (47 - 3)
chi2_robert = robert_row['chi2_ndf'] * (47 - 8)

dchi2 = chi2_tsallis - chi2_robert
dndf = 5

p_val = chi2.sf(dchi2, dndf)
z_val = norm.isf(p_val)

print(f"Tsallis chi2: {chi2_tsallis:.2f}")
print(f"Robert chi2: {chi2_robert:.2f}")
print(f"Delta chi2: {dchi2:.2f}")
print(f"p-value: {p_val:.2e}")
print(f"Z-value (Sigma): {z_val:.2f} sigma")
