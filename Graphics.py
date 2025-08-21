from Oblique_Shock_Solver import ObliqueShockAnalyzer
from Expansion_Wave_Solver import PrandtlMeyerExpansion
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import fsolve


def plot_pressure_theta_analysis(M1, M2, M3, Theta1, Theta2, P2_over_P1, P3_over_P2,
                                 Case, analyzer_obs, analyzer_pm, show_plot=True, figsize=(10, 6)):
    """
    Draws the Pressure–Deflection Angle (P–θ) diagram and finds intersection points
    """

    # Color list
    color_list = ["r", "g", "b", "purple", "black", "yellow", "cyan"]

    # Initialize solvers
    analyzer_obs = ObliqueShockAnalyzer()
    analyzer_pm = PrandtlMeyerExpansion()

    # === Inner functions ===
    def plot_pressure_vs_theta(M, Theta=0, P2_over_P1=1, color=0):
        """Plots oblique shock P–θ curve"""
        max_theta_value, _ = analyzer_obs.max_theta(M)
        Theta_list = np.arange(0.01, max_theta_value, 0.1)

        pr_weak = [analyzer_obs.pressure_ratio(M, t) * P2_over_P1 for t in Theta_list]
        pr_strong = [analyzer_obs.pressure_ratio_strong(M, t) * P2_over_P1 for t in Theta_list]
        pr_weak[-1] = pr_strong[-1]  # Connects at max theta

        if show_plot:
            plt.plot(Theta_list + Theta, pr_weak, color_list[color], label=f"MACH {M:.2f}")
            plt.plot(-1 * (Theta_list - Theta), pr_weak, color_list[color])
            plt.plot(Theta_list + Theta, pr_strong, color_list[color])
            plt.plot(-1 * (Theta_list - Theta), pr_strong, color_list[color])

        return pr_weak, pr_strong, max_theta_value

    def plot_pressure_vs_theta_pm(M, Theta=0, P2_over_P1=1, color=0):
        """Plots Prandtl–Meyer expansion P–θ curve"""
        Theta_list = np.arange(0, 90, 0.1)
        pr_pm = [analyzer_pm.pressure_ratio_pm(M, t) * P2_over_P1 for t in Theta_list]

        if show_plot:
            plt.plot(Theta_list + Theta, pr_pm, color_list[color], label=f"MACH {M:.2f}")
            plt.plot(-1 * (Theta_list - Theta), pr_pm, color_list[color])

        return pr_pm

    def difference(x):
        return f1(x) - f2(x)

    # === Setup plot ===
    if show_plot:
        plt.figure(figsize=figsize)

    if Case == 0:
        # CASE 0: Shock reflection case
        print("Drawing graph (Oblique Shock)...")

        # Mach 1
        pr1, pr1s, max_theta_value1 = plot_pressure_vs_theta(M1)

        # Mach 2
        pr2, pr2s, max_theta_value2 = plot_pressure_vs_theta(M2, Theta=Theta1, P2_over_P1=P2_over_P1, color=1)

        # Mach 3
        pr3, pr3s, max_theta_value3 = plot_pressure_vs_theta(M3, Theta=Theta2, P2_over_P1=P2_over_P1 * P3_over_P2, color=2)

        if show_plot:
            plt.xlabel("Theta (°)")
            plt.ylabel("Pressure Ratio")
            plt.title("Pressure Ratio vs Deflection Angle")
            plt.legend()
            plt.grid(True)

        # Intersection candidates
        x1 = np.arange(0.01, max_theta_value1, 0.1)   # Mach 1 curve
        y1 = pr1
        x2 = (np.arange(0.01, max_theta_value3, 0.1) - Theta2) * -1  # Mach 3 curve
        y2 = pr3

    elif Case == 1:
        # CASE 1: Expansion wave case
        print("Drawing graph (Expansion Wave)...")

        # Mach 1
        pr1, pr1s, max_theta_value1 = plot_pressure_vs_theta(M1)

        # Mach 2
        pr2, pr2s, max_theta_value2 = plot_pressure_vs_theta(M2, Theta=Theta1, P2_over_P1=P2_over_P1, color=1)

        # Mach 3 (Prandtl–Meyer expansion)
        pr3_pm = plot_pressure_vs_theta_pm(M3, Theta=Theta2, P2_over_P1=P2_over_P1 * P3_over_P2, color=2)

        # Intersection candidates
        x1 = np.arange(0.01, max_theta_value1, 0.1)  # Mach 1 curve
        y1 = pr1
        x2 = np.arange(0, 90, 0.1) + Theta2  # Expansion curve
        y2 = pr3_pm

        if show_plot:
            plt.xlabel("Theta (°)")
            plt.ylabel("Pressure Ratio")
            plt.title("Pressure Ratio vs Deflection Angle")
            plt.legend()
            plt.grid(True)

    else:
        raise ValueError("Case parameter must be either 0 (shock) or 1 (expansion)!")

    # === Find intersection point ===
    try:
        f1 = interp1d(x1, y1, kind='linear', fill_value="extrapolate")
        f2 = interp1d(x2, y2, kind='linear', fill_value="extrapolate")

        x_common = np.linspace(max(min(x1), min(x2)), min(max(x1), max(x2)), 1000)
        x0 = x_common[np.argmin(np.abs(f1(x_common) - f2(x_common)))]

        # Solve numerically
        x_intersect = fsolve(difference, x0)[0]
        y_intersect = f1(x_intersect)

        print(f"Theta5 = {x_intersect:.4f}, P4/P1 = P5/P1 = {y_intersect:.4f}")

        if show_plot:
            plt.plot(x_intersect, y_intersect, 'ro', label="Intersection Point")

    except Exception as e:
        print(f"Intersection not found: {e}")
        return None, None

    # Save full plot
    plt.savefig("graph.png")

    # Zoomed view
    x_center = x_intersect
    y_center = y_intersect
    x_range = 0.5
    y_range = 0.3
    plt.xlim(x_center - x_range, x_center + x_range)
    plt.ylim(y_center - y_range, y_center + y_range)
    plt.savefig("graph_zoomed.png")

    # Show plot
    if show_plot:
        plt.show(block=False)
        plt.close()

    return x_intersect, y_intersect
