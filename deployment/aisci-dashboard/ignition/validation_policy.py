from dataclasses import dataclass

@dataclass
class ValidationPolicy:
    version: str = "1.0.0"
    chi2_critical: float = 20.0
    chi2_warning: float = 3.0
    rho_warning: float = 0.90
    rho_critical: float = 0.95
    
    def validate_chi2(self, chi2_ndf: float) -> tuple[str, str]:
        if chi2_ndf > self.chi2_critical:
            return "critical", f"χ²/ndf = {chi2_ndf:.1f} — model fails mathematically and physically"
        elif chi2_ndf > self.chi2_warning:
            return "warning", f"χ²/ndf = {chi2_ndf:.1f} — poor fit quality, consider alternative models"
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

default_policy = ValidationPolicy()
