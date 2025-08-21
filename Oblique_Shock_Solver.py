import numpy as np
from scipy.optimize import fsolve


import numpy as np
from scipy.optimize import fsolve


class ObliqueShockAnalyzer:

    def __init__(self, gamma=1.4):
        """
        Initialize the ObliqueShockAnalyzer class.
        """
        self.gamma = gamma

    def theta_from_beta(self, M1, beta):
        """
        Compute the theta angle based on Mach number and beta angle.
        """
        beta_rad = np.radians(beta)
        term1 = 2 * (1 / np.tan(beta_rad))
        term2 = (M1 ** 2 * (np.sin(beta_rad)) ** 2 - 1) / (M1 ** 2 * (self.gamma + np.cos(2 * beta_rad)) + 2)
        theta_rad = np.arctan(term1 * term2)
        return np.degrees(theta_rad)

    def max_theta(self, M1):
        """
        Compute the maximum theta angle for a given Mach number.
        """
        beta_min = np.degrees(np.arcsin(1 / M1)) + 0.001  # To avoid errors
        beta_max = 90.0
        beta_vals = np.linspace(beta_min, beta_max, 1000)
        theta_vals = [self.theta_from_beta(M1, b) for b in beta_vals]

        max_theta_value = max(theta_vals)
        beta_at_max_theta = beta_vals[theta_vals.index(max_theta_value)]

        return max_theta_value, beta_at_max_theta

    def _theta_beta_m_relation(self, beta, M1, theta):
        """
        Theta-Beta-Mach number relation.
        """
        beta_rad = np.radians(beta)
        theta_rad = np.radians(theta)
        lhs = np.tan(theta_rad)
        rhs = 2 * (1 / np.tan(beta_rad)) * ((M1 ** 2 * (np.sin(beta_rad)) ** 2 - 1) /
                                            (M1 ** 2 * (self.gamma + np.cos(2 * beta_rad)) + 2))
        return lhs - rhs

    def solve_beta_angle(self, M1, theta):
        """
        Compute beta angle based on Mach number and theta angle.
        """
        if M1 < 1:
            raise ValueError(f"Input Mach number ({M1:.3f}) is less than 1; no shock forms.")

        theta_max, beta_for_theta_max = self.max_theta(M1)
        if theta > theta_max:
            raise ValueError(f"Input theta angle ({theta:.3f}°) exceeds max theta ({theta_max:.3f}°); detached shock occurs!")

        beta_guess_weak = theta + 5
        beta_weak = fsolve(self._theta_beta_m_relation, beta_guess_weak, args=(M1, theta))[0]

        return beta_weak

    def mach_after_shock(self, M1, theta_deg):
        """
        Compute Mach number after an oblique shock.
        """
        beta = np.radians(self.solve_beta_angle(M1, theta_deg))
        theta = np.radians(theta_deg)

        M1n = M1 * np.sin(beta)
        numerator = 1 + ((self.gamma - 1) / 2) * M1n ** 2
        denominator = self.gamma * M1n ** 2 - (self.gamma - 1) / 2
        M2n = np.sqrt(numerator / denominator)

        M2 = M2n / np.sin(beta - theta)
        return M2

    def pressure_ratio(self, M1, theta_deg):
        """
        Compute pressure ratio after an oblique shock.
        """
        beta = np.radians(self.solve_beta_angle(M1, theta_deg))
        M1n = M1 * np.sin(beta)

        p2_over_p1 = 1 + (2 * self.gamma / (self.gamma + 1)) * (M1n ** 2 - 1)
        return p2_over_p1

    def temperature_ratio(self, M1, theta_deg):
        """
        Compute temperature ratio after an oblique shock.
        """
        beta = np.radians(self.solve_beta_angle(M1, theta_deg))
        M1n = M1 * np.sin(beta)

        p2_over_p1 = 1 + (2 * self.gamma / (self.gamma + 1)) * (M1n ** 2 - 1)
        rho2_rho1 = ((self.gamma + 1) * M1n ** 2) / ((self.gamma - 1) * M1n ** 2 + 2)
        T2_over_T1 = p2_over_p1 / rho2_rho1
        return T2_over_T1

    def density_ratio(self, M1, theta_deg):
        """
        Compute density ratio after an oblique shock.
        """
        p2_over_p1 = self.pressure_ratio(M1, theta_deg)
        T2_over_T1 = self.temperature_ratio(M1, theta_deg)
        rho2_over_rho1 = p2_over_p1 / T2_over_T1
        return rho2_over_rho1

    def total_pressure_ratio(self, M1, theta_deg):
        """
        Compute total pressure ratio after an oblique shock.
        """
        beta_deg = self.solve_beta_angle(M1, theta_deg)
        beta = np.radians(beta_deg)

        Mn1 = M1 * np.sin(beta)

        term1 = ((self.gamma + 1) * Mn1 ** 2) / ((self.gamma - 1) * Mn1 ** 2 + 2)
        term1 = term1 ** (self.gamma / (self.gamma - 1))

        term2 = ((self.gamma + 1) / (2 * self.gamma * Mn1 ** 2 - (self.gamma - 1))) ** (1 / (self.gamma - 1))

        pt2_over_pt1 = term1 * term2

        return pt2_over_pt1

    def complete_analysis(self, M1, theta_deg):
        """
        Perform comprehensive oblique shock analysis for given conditions.
        """
        try:
            beta = self.solve_beta_angle(M1, theta_deg)
            M2 = self.mach_after_shock(M1, theta_deg)
            p_ratio = self.pressure_ratio(M1, theta_deg)
            T_ratio = self.temperature_ratio(M1, theta_deg)
            rho_ratio = self.density_ratio(M1, theta_deg)
            pt_ratio = self.total_pressure_ratio(M1, theta_deg)

            results = {
                'input_mach': M1,
                'theta_angle': theta_deg,
                'beta_angle': beta,
                'output_mach': M2,
                'pressure_ratio': p_ratio,
                'temperature_ratio': T_ratio,
                'density_ratio': rho_ratio,
                'total_pressure_ratio': pt_ratio
            }

            return results

        except ValueError as e:
            return {'error': str(e)}

    def solve_beta_angle_strong(self, M1, theta):
        """
        Compute the strong solution for beta angle.
        """
        beta_guess_strong = 89.9
        beta_strong = fsolve(self._theta_beta_m_relation, beta_guess_strong, args=(M1, theta))[0]

        return beta_strong

    def pressure_ratio_strong(self, M1, theta_deg):
        """
        Compute pressure ratio for the strong oblique shock solution.
        """
        beta = np.radians(self.solve_beta_angle_strong(M1, theta_deg))
        M1n = M1 * np.sin(beta)

        p2_over_p1_strong = 1 + (2 * self.gamma / (self.gamma + 1)) * (M1n ** 2 - 1)
        return p2_over_p1_strong


# Usage example
if __name__ == "__main__":
    # Initialize class
    shock_analyzer = ObliqueShockAnalyzer()

    # Sample analysis
    M1 = 2.0
    theta = 15.0

    print("=== Oblique Shock Analysis ===")
    print(f"Input Mach number: {M1}")
    print(f"Theta angle: {theta}°")

    # Complete analysis
    results = shock_analyzer.complete_analysis(M1, theta)

    if 'error' not in results:
        print("\n--- Results ---")
        print(f"Beta angle: {results['beta_angle']:.2f}°")
        print(f"Output Mach number: {results['output_mach']:.3f}")
        print(f"Pressure ratio (P2/P1): {results['pressure_ratio']:.3f}")
        print(f"Temperature ratio (T2/T1): {results['temperature_ratio']:.3f}")
        print(f"Density ratio (ρ2/ρ1): {results['density_ratio']:.3f}")
        print(f"Total pressure ratio (Pt2/Pt1): {results['total_pressure_ratio']:.3f}")
    else:
        print(f"Error: {results['error']}")

    # Check maximum theta angle
    max_theta_val, beta_at_max = shock_analyzer.max_theta(M1)
    print(f"\nMaximum theta angle: {max_theta_val:.2f}°")
    print(f"Beta angle at maximum theta: {beta_at_max:.2f}°")
