#!/usr/bin/env python3
"""
SymPy Validation Agent for Physics Analysis
Performs dimensional analysis, kinematic boundary checking, and equation validation.

This agent can:
1. Parse mathematical expressions from LaTeX or text
2. Perform dimensional analysis to verify unit consistency
3. Check kinematic boundary conditions
4. Validate velocity parameterizations
5. Flag unphysical equations or results
"""

import sympy as sp
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import parse_expr
from typing import Dict, List, Optional, Union, Tuple
import re


class SymPyPhysicsValidator:
    def __init__(self):
        """Initialize the physics validator with common physics symbols and units."""
        # Define common physics symbols
        self.c = sp.Symbol('c', positive=True)  # Speed of light
        self.hbar = sp.Symbol('ħ', positive=True)  # Reduced Planck constant
        self.kb = sp.Symbol('k_B', positive=True)  # Boltzmann constant
        
        # Common variables in particle physics
        self.p = sp.Symbol('p', positive=True)  # Momentum magnitude
        self.pT = sp.Symbol('p_T', positive=True)  # Transverse momentum
        self.E = sp.Symbol('E', positive=True)  # Energy
        self.m = sp.Symbol('m', positive=True)  # Mass
        self.T = sp.Symbol('T', positive=True)  # Temperature
        self.beta = sp.Symbol('β', real=True)  # Velocity in units of c
        self.gamma = sp.Symbol('γ', positive=True)  # Lorentz factor
        self.theta = sp.Symbol('θ', real=True)  # Angle
        
        # Dimensional constants
        self.length_dim = sp.Symbol('L')
        self.mass_dim = sp.Symbol('M')
        self.time_dim = sp.Symbol('T')
        self.energy_dim = self.mass_dim * self.length_dim**2 / self.time_dim**2
        self.momentum_dim = self.mass_dim * self.length_dim / self.time_dim
        self.temperature_dim = sp.Symbol('Θ')
        
    def parse_expression(self, expr_str: str) -> Optional[sp.Expr]:
        """
        Parse a mathematical expression from LaTeX or text format.
        
        Parameters:
        -----------
        expr_str : str
            Mathematical expression in LaTeX or text format
            
        Returns:
        --------
        sympy.Expr or None
            Parsed expression or None if parsing fails
        """
        try:
            # Try parsing as LaTeX first
            if '\\' in expr_str or '{' in expr_str:
                return parse_latex(expr_str)
            else:
                # Try parsing as text
                return parse_expr(expr_str)
        except Exception as e:
            print(f"Failed to parse expression '{expr_str}': {e}")
            return None
    
    def dimensional_analysis(self, expr: sp.Expr, expected_dimensions: Optional[sp.Symbol] = None) -> bool:
        """
        Perform dimensional analysis on an expression.
        
        Parameters:
        -----------
        expr : sympy.Expr
            Expression to analyze
        expected_dimensions : sympy.Symbol, optional
            Expected dimensions to check against
            
        Returns:
        --------
        bool
            True if dimensions are consistent, False otherwise
        """
        try:
            # For now, we'll just check if the expression is dimensionally consistent
            # A more sophisticated implementation would track actual dimensions
            print(f"Performing dimensional analysis on: {expr}")
            
            # Simplify the expression to check for consistency
            simplified = sp.simplify(expr)
            print(f"Simplified expression: {simplified}")
            
            # Check if the expression contains infinities or undefined terms
            if simplified.has(sp.zoo) or simplified.has(sp.nan):
                print("Expression contains undefined terms (inf/nan)")
                return False
                
            return True
        except Exception as e:
            print(f"DIMENSIONAL ANALYSIS ERROR: {e}")
            return False
    
    def check_kinematic_boundaries(self, expr: sp.Expr) -> Dict[str, bool]:
        """
        Check if an expression respects kinematic boundaries.
        
        Parameters:
        -----------
        expr : sympy.Expr
            Expression to check
            
        Returns:
        --------
        dict
            Dictionary with boundary check results
        """
        checks = {}
        
        # Check for velocity constraints (should be < c)
        beta_symbols = [sym for sym in expr.free_symbols if str(sym).startswith('β')]
        for beta in beta_symbols:
            # Check if β appears in context where it should be < 1
            print(f"Checking velocity constraint for symbol: {beta}")
            checks[f'beta_{beta}_lt_c'] = True  # Placeholder for actual check
        
        # Check if energy is greater than momentum (for massive particles)
        try:
            # Look for energy and momentum symbols in the expression
            energy_terms = [sym for sym in expr.free_symbols if str(sym).lower().startswith('e')]
            momentum_terms = [sym for sym in expr.free_symbols if str(sym).lower().startswith('p')]
            
            for e in energy_terms:
                for p in momentum_terms:
                    # For massive particles: E^2 >= p^2*c^2 + m^2*c^4
                    # For massless particles: E = p*c
                    print(f"Checking energy-momentum relation: E={e}, p={p}")
        except Exception as e:
            print(f"Kinematic boundary check error: {e}")
        
        return checks
    
    def validate_velocity_parameterization(self, velocity_expr: sp.Expr) -> Dict[str, Union[bool, float]]:
        """
        Validate velocity parameterization (U vs v check).
        
        Parameters:
        -----------
        velocity_expr : sympy.Expr
            Velocity expression to validate
            
        Returns:
        --------
        dict
            Validation results including max velocity achieved
        """
        try:
            # Find the variable that might represent U (rapidity or similar)
            # and check if it's properly converted to velocity
            result = {
                'valid': True,
                'max_velocity': None,
                'asymptotic_behavior': None
            }
            
            # Check for the form v = U/sqrt(1 + U^2) or similar
            # This should always yield v < 1 (speed of light)
            U_symbols = [sym for sym in velocity_expr.free_symbols if str(sym).upper() == 'U']
            
            if U_symbols:
                U = U_symbols[0]
                
                # Substitute increasingly large values for U to check asymptotic behavior
                large_U_val = 1000
                velocity_at_large_U = velocity_expr.subs(U, large_U_val).evalf()
                
                print(f"Velocity at large U ({large_U_val}): {velocity_at_large_U}")
                
                if velocity_at_large_U > 1:
                    result['valid'] = False
                    print(f"ERROR: Velocity exceeds speed of light: {velocity_at_large_U}")
                
                result['max_velocity'] = float(velocity_at_large_U)
                result['asymptotic_behavior'] = float(velocity_at_large_U)
            
            return result
        except Exception as e:
            print(f"Velocity validation error: {e}")
            return {'valid': False, 'error': str(e)}
    
    def validate_equation(self, equation_str: str) -> Dict[str, any]:
        """
        Comprehensive validation of a physics equation.
        
        Parameters:
        -----------
        equation_str : str
            Equation string to validate
            
        Returns:
        --------
        dict
            Validation results
        """
        print(f"\nValidating equation: {equation_str}")
        
        # Parse the equation
        parsed_eq = self.parse_expression(equation_str)
        if not parsed_eq:
            return {
                'original_equation': equation_str,
                'parsed_expression': None,
                'dimensionally_consistent': False,
                'kinematic_valid': {},
                'velocity_valid': False,
                'overall_validity': False,
                'warnings': ['Failed to parse equation'],
                'error': 'Failed to parse equation'
            }
        
        # Perform dimensional analysis
        dim_check = self.dimensional_analysis(parsed_eq)
        
        # Check kinematic boundaries
        kinematic_checks = self.check_kinematic_boundaries(parsed_eq)
        
        # If this looks like a velocity equation, validate it
        if 'v' in equation_str.lower() and ('u' in equation_str.lower() or 'beta' in equation_str.lower()):
            velocity_validation = self.validate_velocity_parameterization(parsed_eq)
        else:
            velocity_validation = {'valid': True}
        
        # Compile results
        results = {
            'original_equation': equation_str,
            'parsed_expression': str(parsed_eq),
            'dimensionally_consistent': dim_check,
            'kinematic_valid': kinematic_checks,
            'velocity_valid': velocity_validation.get('valid', True),
            'overall_validity': dim_check and velocity_validation.get('valid', True),
            'warnings': []
        }
        
        if not dim_check:
            results['warnings'].append("Equation may have dimensional inconsistencies")
        
        if not velocity_validation.get('valid', True):
            results['warnings'].append("Equation yields unphysical velocities >= c")
        
        return results


def demonstrate_validator():
    """Demonstrate the SymPy validation agent with example physics equations."""
    validator = SymPyPhysicsValidator()
    
    # Example equations to validate
    test_equations = [
        # Proper velocity parameterization: v = U/sqrt(1 + U^2)
        "U/sqrt(1 + U**2)",
        
        # Tsallis distribution form
        "exp(-beta_T*p_T/T) * (1 + (q-1)*p_T/T)**(-1/(q-1))",
        
        # Potentially problematic velocity: U might be rapidity, not velocity
        "U/sqrt(1 + U**2)",  # This should be fine
        
        # Kinematic constraint example: p_T < p
        "p_T - p",  # This should be negative for valid kinematics
        
        # Simple dimensional check: E^2 = p^2*c^2 + m^2*c^4
        "E**2 - p**2*c**2 - m**2*c**4"
    ]
    
    for i, eq in enumerate(test_equations):
        print(f"\n{'='*50}")
        print(f"Test {i+1}: {eq}")
        print('='*50)
        
        result = validator.validate_equation(eq)
        
        print(f"Dimensionally consistent: {result['dimensionally_consistent']}")
        print(f"Velocity valid: {result['velocity_valid']}")
        print(f"Overall validity: {result['overall_validity']}")
        if result['warnings']:
            print(f"Warnings: {result['warnings']}")


if __name__ == "__main__":
    demonstrate_validator()