from dataclasses import dataclass

@dataclass
class ValidationPolicy:
    version: str = "1.0.0"
    chi2_critical: float = 20.0
    chi2_warning: float = 3.0
    rho_warning: float = 0.90
    rho_critical: float = 0.95
    
    def validate_chi2(self, chi2_ndf: float, ndf: int | None = None, alpha_critical: float = 0.01, alpha_warning: float = 0.05) -> tuple[str, str]:
        critical = self.chi2_critical
        warning = self.chi2_warning
        
        if ndf is not None and ndf > 0:
            try:
                import scipy.stats
                critical = float(scipy.stats.chi2.ppf(1.0 - alpha_critical, ndf) / ndf)
                warning = float(scipy.stats.chi2.ppf(1.0 - alpha_warning, ndf) / ndf)
            except Exception:
                pass

        if chi2_ndf > critical:
            return "critical", f"χ²/ndf = {chi2_ndf:.1f} — model fails mathematically and physically (calibrated threshold: {critical:.2f})"
        elif chi2_ndf > warning:
            return "warning", f"χ²/ndf = {chi2_ndf:.1f} — poor fit quality, consider alternative models (calibrated threshold: {warning:.2f})"
        return "ok", ""

    def validate_t_q_degeneracy(self, rho: float, model_name: str, param_left: str, param_right: str) -> tuple[str, str]:
        model_lower = model_name.lower()
        if "tsallis" in model_lower:
            is_t = param_left in ["temperature_1", "T_kin", "T_stat"] or param_right in ["temperature_1", "T_kin", "T_stat"]
            is_q = param_left in ["q_1", "q"] or param_right in ["q_1", "q"]
            if is_t and is_q and abs(rho) > 0.85:
                return "warning", f"ρ({param_left}, {param_right}) = {rho:.3f} — T-q Degeneracy: parameters in Tsallis model are strongly coupled"
        return "ok", ""

    def validate_correlation(self, rho: float, param_left: str, param_right: str) -> tuple[str, str]:
        if abs(rho) > self.rho_critical:
            return "critical", f"ρ({param_left}, {param_right}) = {rho:.3f} — DEGENERATE: parameters are not independent"
        elif abs(rho) > self.rho_warning:
            return "warning", f"ρ({param_left}, {param_right}) = {rho:.3f} — Strong correlation detected"
        return "ok", ""

    def validate_velocity(self, v_val: float) -> tuple[str, str]:
        if v_val >= 1.0:
            return "critical", f"v = {v_val:.3f} c — violates causality (v < c required)"
        elif v_val > 0.95:
            return "warning", f"v = {v_val:.3f} c — extreme radial flow, near boundary"
        return "ok", ""

    def validate_four_velocity(self, u_val: float) -> tuple[str, str]:
        # U = gamma * v. It can exceed 1 (since U -> infinity as v -> c).
        # We don't apply v < c boundary to U.
        if u_val > 10.0:
            return "warning", f"U = {u_val:.3f} — extremely high four-velocity (v > 0.995c)"
        return "ok", ""

    def validate_temperature(self, t_val: float, feed_down_corrected: bool = False) -> tuple[str, str]:
        min_t = 0.05 if feed_down_corrected else 0.06
        max_t = 0.25 if feed_down_corrected else 0.30
        if t_val <= 0.0:
            return "critical", f"T = {t_val:.3f} GeV — unphysical negative temperature"
        elif t_val > max_t:
            return "warning", f"T = {t_val:.3f} GeV — high temperature > {max_t} GeV, likely numerical instability or uncorrected feed-down"
        elif t_val < min_t:
            return "warning", f"T = {t_val:.3f} GeV — low temperature < {min_t} GeV"
        return "ok", ""

default_policy = ValidationPolicy()
