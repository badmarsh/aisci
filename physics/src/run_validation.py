import json
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sympy_validation_agent import SymPyPhysicsValidator

def run():
    validator = SymPyPhysicsValidator()
    formulas = [
        {"id": "F.01", "section": "§2.1", "description": "Differential elastic cross-section", "expression": "A * F_N**2 * exp(B*t)", "dimensions": "[mb·GeV⁻²]"},
        {"id": "F.02", "section": "§2.3", "description": "Linear Regge trajectory", "expression": "alpha_0 + alpha_prime * t", "dimensions": "[1]"},
        {"id": "F.03", "section": "§4.1", "description": "Tsallis distribution form", "expression": "exp(-beta_T*p_T/T) * (1 + (q-1)*p_T/T)**(-1/(q-1))", "dimensions": "[1]"},
        {"id": "F.04", "section": "§4.3", "description": "Proper velocity parameterization", "expression": "U/sqrt(1 + U**2)", "dimensions": "[1]"},
        {"id": "F.05", "section": "§5.1", "description": "Energy momentum", "expression": "E**2 - p**2*c**2 - m**2*c**4", "dimensions": "[GeV²]"},
        {"id": "F.06", "section": "§6.2", "description": "Failing kinematic constraint", "expression": "p_T - p", "dimensions": "[GeV]"}
    ]
    results = []
    for f in formulas:
        # redirect stdout to avoid polluting json
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            res = validator.validate_equation(f['expression'])
        finally:
            sys.stdout = old_stdout
            
        results.append({
            'id': f['id'],
            'section': f['section'],
            'description': f['description'],
            'expression': f['expression'],
            'valid': res['overall_validity'],
            'note': ', '.join(res['warnings']) if res['warnings'] else 'Dimensionally consistent',
            'dimensions': f['dimensions']
        })
    print(json.dumps(results))

if __name__ == "__main__":
    run()
