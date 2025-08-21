import numpy as np
from scipy.optimize import fsolve


class PrandtlMeyerExpansion:
    """
    Class for Prandtl-Meyer expansion wave calculations
    """

    def __init__(self, gamma=1.4):
        """
        Initialize the class
        """
        self.gamma = gamma

    def prandtl_meyer_angle(self, M):
        """
        Compute the Prandtl-Meyer expansion angle for a given Mach number
        """
        if M <= 1:
            raise ValueError("The Prandtl–Meyer function is only defined for M > 1.")

        term1 = np.sqrt((self.gamma + 1) / (self.gamma - 1))
        term2 = np.arctan(np.sqrt((self.gamma - 1) / (self.gamma + 1) * (M ** 2 - 1)))
        term3 = np.arctan(np.sqrt(M ** 2 - 1))

        nu_rad = term1 * term2 - term3  # In radians
        nu_deg = np.degrees(nu_rad)  # Convert to degrees

        return nu_deg

    def mach_from_expansion(self, M1, theta_deg):
        """
        Compute downstream Mach number after expansion wave
        """
        nu1 = self.prandtl_meyer_angle(M1)
        nu_target = nu1 + theta_deg  # target expansion angle

        # Solve the equation: prandtl_meyer(M2) - nu_target = 0
        def func(M2):
            return self.prandtl_meyer_angle(M2) - nu_target

        M2_guess = M1 + 0.5  # Initial guess
        M2_solution = fsolve(func, M2_guess)[0]

        return M2_solution

    def pressure_ratio_pm(self, M1, theta_deg):
        """
        Compute pressure ratio after expansion wave (p2/p1)
        """
        M2 = self.mach_from_expansion(M1, theta_deg)
        num = 1 + (self.gamma - 1) / 2 * M1 ** 2
        den = 1 + (self.gamma - 1) / 2 * M2 ** 2
        p_ratio = (num / den) ** (self.gamma / (self.gamma - 1))
        return p_ratio

    def temperature_ratio_pm(self, M1, theta_deg):
        """
        Compute temperature ratio after expansion wave (T2/T1)
        """
        M2 = self.mach_from_expansion(M1, theta_deg)
        num = 1 + (self.gamma - 1) / 2 * M1 ** 2
        den = 1 + (self.gamma - 1) / 2 * M2 ** 2
        return num / den

    def density_ratio_pm(self, M1, theta_deg):
        """
        Compute density ratio after expansion wave (rho2/rho1)
        """
        p_ratio = self.pressure_ratio_pm(M1, theta_deg)
        T_ratio = self.temperature_ratio_pm(M1, theta_deg)
        return p_ratio / T_ratio

    def calculate_all_ratios(self, M1, theta_deg):
        """
        Compute all ratios and the resulting Mach number
        """
        M2 = self.mach_from_expansion(M1, theta_deg)
        p_ratio = self.pressure_ratio_pm(M1, theta_deg)
        T_ratio = self.temperature_ratio_pm(M1, theta_deg)
        rho_ratio = self.density_ratio_pm(M1, theta_deg)

        return {
            'M2': M2,
            'pressure_ratio': p_ratio,
            'temperature_ratio': T_ratio,
            'density_ratio': rho_ratio,
            'nu1': self.prandtl_meyer_angle(M1),
            'nu2': self.prandtl_meyer_angle(M2)
        }


# Usage example:
if __name__ == "__main__":
    # Create class instance
    pm = PrandtlMeyerExpansion(gamma=1.4)

    # Example calculation
    M1 = 2.0
    theta = 10.0  # degrees

    print(f"Initial Mach number: M1 = {M1}")
    print(f"Expansion angle: θ = {theta}°")
    print("-" * 40)

    # Compute all results
    results = pm.calculate_all_ratios(M1, theta)

    print(f"Resulting Mach number: M2 = {results['M2']:.4f}")
    print(f"Pressure ratio: p2/p1 = {results['pressure_ratio']:.4f}")
    print(f"Temperature ratio: T2/T1 = {results['temperature_ratio']:.4f}")
    print(f"Density ratio: ρ2/ρ1 = {results['density_ratio']:.4f}")
    print(f"Initial PM angle: ν1 = {results['nu1']:.4f}°")
    print(f"Resulting PM angle: ν2 = {results['nu2']:.4f}°")



