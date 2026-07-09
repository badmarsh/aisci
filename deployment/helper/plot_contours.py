import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def main():
    scan_dir = Path("research/robert/runs/2026-07-08-bgbw-profile-scan")
    
    if not scan_dir.exists():
        print(f"Directory {scan_dir} does not exist.")
        return
        
    csv_files = sorted(scan_dir.glob("contour_bin_*.csv"))
    
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Plot all points, colored by delta_chi2
        sc = ax.scatter(df["beta_s"], df["T_kin_gev"], c=df["delta_chi2"], cmap="viridis_r", s=100)
        plt.colorbar(sc, label="$\\Delta\\chi^2$")
        
        # Highlight the 68% CL region (1-sigma)
        mask_1sigma = df["delta_chi2"] < 1.0
        if mask_1sigma.any():
            ax.scatter(df.loc[mask_1sigma, "beta_s"], df.loc[mask_1sigma, "T_kin_gev"], 
                       edgecolors="red", facecolors="none", s=200, linewidth=2, label="68% CL")
                       
        # Highlight the 95% CL region (2-sigma, delta_chi2 < 4.0)
        mask_2sigma = df["delta_chi2"] < 4.0
        if mask_2sigma.any():
            ax.scatter(df.loc[mask_2sigma, "beta_s"], df.loc[mask_2sigma, "T_kin_gev"], 
                       edgecolors="orange", facecolors="none", s=300, linewidth=2, label="95% CL")
        
        bin_label = csv_file.stem.split("contour_bin_")[1]
        
        ax.set_xlabel(r"$\langle \beta_s \rangle$ (Surface Velocity)")
        ax.set_ylabel(r"$T_{kin}$ (Kinetic Freeze-out Temperature) [GeV]")
        ax.set_title(f"BGBW Parameter Degeneracy: Multiplicity Bin {bin_label}")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.6)
        
        out_file = scan_dir / f"{csv_file.stem}.png"
        fig.savefig(out_file, dpi=300, bbox_inches="tight")
        plt.close(fig)
        
        print(f"Generated {out_file}")

if __name__ == "__main__":
    main()
