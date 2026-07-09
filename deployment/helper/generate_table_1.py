import json
from pathlib import Path

def generate_table():
    run_dir = Path("research/robert/runs/2026-07-09-jacobian-fix")
    results_file = run_dir / "fit_results.json"
    
    with open(results_file, "r") as f:
        data = json.load(f)
        
    baseline_file = Path("research/robert/runs/2026-04-27-baseline-fit/fit_run_status.json")
    if baseline_file.exists():
        with open(baseline_file, "r") as f:
            baseline_data = json.load(f)
            
        for bin_label in data:
            if bin_label in baseline_data and isinstance(data[bin_label], dict) and isinstance(baseline_data[bin_label], dict):
                data[bin_label].update(baseline_data[bin_label])
        
    # The models Robert wants in Table 1
    models_to_report = {
        "manuscript_1c": "Jüttner 1c (Eq. X)",
        "tsallis_2c": "Tsallis 2c",
        "blast_wave_1c": "BGBW 1c"
    }
    
    bins = sorted(data.keys(), key=lambda x: int(x.split('-')[0]) if '-' in x else x)
    
    md = [
        "# Replacement Table 1",
        "",
        "| Multiplicity Bin | Model | $\\chi^2/\\text{ndf}$ | Parameters |",
        "|---|---|---|---|"
    ]
    
    for bin_label in bins:
        bin_data = data[bin_label]
        if not isinstance(bin_data, dict):
            continue
        
        for model_key, model_name in models_to_report.items():
            if model_key not in bin_data:
                continue
                
            model_res = bin_data[model_key]
            
            if model_res.get("success") is False:
                continue
                
            chi2_ndf = model_res.get("chi2_ndf")
            chi2_str = f"{chi2_ndf:.2f}" if chi2_ndf is not None else "N/A"
            
            params = model_res.get("parameters", {})
            errors = model_res.get("parameter_errors", {})
            
            param_strs = []
            for k, v in params.items():
                err = errors.get(k)
                err_str = f" ± {err:.3g}" if err is not None else ""
                
                # Format specific parameters better
                if k.startswith("temperature"):
                    param_strs.append(f"$T$ = {v:.3g}{err_str}")
                elif k.startswith("beta") or k.startswith("U"):
                    param_strs.append(f"$\\beta/U$ = {v:.3g}{err_str}")
                elif k.startswith("q"):
                    param_strs.append(f"$q$ = {v:.3g}{err_str}")
            
            params_formatted = ", ".join(param_strs)
            
            md.append(f"| {bin_label} | {model_name} | {chi2_str} | {params_formatted} |")
            
    with open("research/robert/table1_replacement.md", "w") as f:
        f.write("\n".join(md))
        
    print("Table 1 replacement generated at research/robert/table1_replacement.md")

if __name__ == "__main__":
    generate_table()
