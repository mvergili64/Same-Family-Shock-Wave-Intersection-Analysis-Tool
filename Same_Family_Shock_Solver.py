from Oblique_Shock_Solver import ObliqueShockAnalyzer
from Expansion_Wave_Solver import PrandtlMeyerExpansion
import time
import pandas as pd

def save_to_csv(results, filename="results.csv"):
    """Save results to a CSV file"""
    try:
        df = pd.DataFrame([results])
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"✅ Results saved to '{filename}'.")
        return True
    except PermissionError:
        print(f"❌ The file '{filename}' might be open. Please close it and try again.")
        return False
    except Exception as e:
        print(f"❌ Failed to save CSV file: {e}")
        return False

def Intersection_of_Shock_Waves_Same_Family(Mach_inlet, Theta, Theta_plus, ITER_NUM=1000):
    start_time = time.time()
    analyzer_obs = ObliqueShockAnalyzer()
    analyzer_pm = PrandtlMeyerExpansion()

    # First shock flow properties
    Beta1 = analyzer_obs.solve_beta_angle(Mach_inlet, Theta)
    M_2 = analyzer_obs.mach_after_shock(Mach_inlet, Theta)
    T2_over_T1_2 = analyzer_obs.temperature_ratio(Mach_inlet, Theta)
    P2_over_P1 = analyzer_obs.pressure_ratio(Mach_inlet, Theta)
    density_ratio_2 = analyzer_obs.density_ratio(Mach_inlet, Theta)
    total_pres_ratio_2 = analyzer_obs.total_pressure_ratio(Mach_inlet, Theta)

    # Second shock flow properties
    Beta2 = analyzer_obs.solve_beta_angle(M_2, Theta_plus)
    M_3 = analyzer_obs.mach_after_shock(M_2, Theta_plus)
    T3_over_T2 = analyzer_obs.temperature_ratio(M_2, Theta_plus)
    P3_over_P2 = analyzer_obs.pressure_ratio(M_2, Theta_plus)
    density_ratio_3 = analyzer_obs.density_ratio(M_2, Theta_plus)
    total_pres_ratio_3 = analyzer_obs.total_pressure_ratio(M_2, Theta_plus)

    # Parameters
    TOLERANCE = 0.001
    STEP_SIZE = 0.001
    MAX_ITERATIONS = ITER_NUM

    # Expansion wave case
    teta_iter = 0.001
    P4_over_P1 = 10
    P5_over_P1 = 1
    Theta_total = Theta + Theta_plus
    A = 0
    iteration_count = 0

    print("🔄 Expansion wave analysis started...")

    try:
        while abs(P4_over_P1 - P5_over_P1) > TOLERANCE and iteration_count < MAX_ITERATIONS:
            P4_over_P1 = analyzer_pm.pressure_ratio_pm(M_3, teta_iter) * P2_over_P1 * P3_over_P2
            P5_over_P1 = analyzer_obs.pressure_ratio(Mach_inlet, Theta_total + teta_iter)
            teta_iter += STEP_SIZE
            iteration_count += 1

        if iteration_count < MAX_ITERATIONS:
            M_4 = analyzer_pm.mach_from_expansion(M_3, teta_iter)
            M_5 = analyzer_obs.mach_after_shock(Mach_inlet, Theta_total - teta_iter)
            T4_over_T1 = analyzer_pm.temperature_ratio_pm(M_3, teta_iter) * T2_over_T1_2 * T3_over_T2
            T5_over_T1 = analyzer_obs.temperature_ratio(Mach_inlet, Theta_total - teta_iter)
            rho4_over_rho1 = analyzer_pm.density_ratio_pm(M_3, teta_iter) * density_ratio_3 * density_ratio_2
            rho5_over_rho1 = analyzer_obs.density_ratio(Mach_inlet, Theta_total - teta_iter)
            total_pres_ratio_4 = 1 * total_pres_ratio_3 * total_pres_ratio_2
            total_pres_ratio_5 = analyzer_obs.total_pressure_ratio(Mach_inlet, Theta_total - teta_iter)
            Beta4 = analyzer_obs.solve_beta_angle(M_3, teta_iter)
            Beta3 = analyzer_obs.solve_beta_angle(Mach_inlet, Theta_total - teta_iter)

            A = 1
            end_time = time.time()
            elapsed_time = end_time - start_time
            results = {
                "Case": "Expansion Wave",
                "Inlet Mach": Mach_inlet,
                "First Ramp Angle": Theta,
                "Ramp Increase Angle": Theta_plus,
                "Mach 2": M_2,
                "Mach 3": M_3,
                "Beta1": Beta1,
                "Beta2": Beta2,
                "Beta3": Beta3,
                "Beta4": Beta4,
                "P2/P1": P2_over_P1,
                "P3/P1": P3_over_P2 * P2_over_P1,
                "P4/P1": P4_over_P1,
                "P5/P1": P5_over_P1,
                "Theta": teta_iter,
                "Mach 4": M_4,
                "Mach 5": M_5,
                "T4/T1": T4_over_T1,
                "T5/T1": T5_over_T1,
                "rho4/rho1": rho4_over_rho1,
                "rho5/rho1": rho5_over_rho1,
                "Pt4/Pt1": total_pres_ratio_4,
                "Pt5/Pt1": total_pres_ratio_5,
                "Iteration Count": iteration_count,
                "Execution Time (s)": elapsed_time
            }
            save_to_csv(results)
            for key, value in results.items():
                print(f"{key}: {value}")
        else:
            print(f"⚠️ No solution found for expansion wave. ({MAX_ITERATIONS} iterations)")

    except Exception as e:
        print(f"❌ Error in expansion wave calculation: {e}")

    if A == 0:
        # Shock wave case
        print("🔄 Shock wave analysis started...")
        P4_over_P1 = 10
        P5_over_P1 = 1
        teta_iter = 0.001
        iteration_count = 0

        try:
            while abs(P4_over_P1 - P5_over_P1) > TOLERANCE and iteration_count < MAX_ITERATIONS:
                P4_over_P1 = analyzer_obs.pressure_ratio(M_3, teta_iter) * P2_over_P1 * P3_over_P2
                P5_over_P1 = analyzer_obs.pressure_ratio(Mach_inlet, Theta_total - teta_iter)
                teta_iter += STEP_SIZE
                iteration_count += 1

            if iteration_count < MAX_ITERATIONS:
                M_4 = analyzer_obs.mach_after_shock(M_3, teta_iter)
                M_5 = analyzer_obs.mach_after_shock(Mach_inlet, Theta_total - teta_iter)
                T4_over_T1 = analyzer_obs.temperature_ratio(M_3, teta_iter) * T2_over_T1_2 * T3_over_T2
                T5_over_T1 = analyzer_obs.temperature_ratio(Mach_inlet, Theta_total - teta_iter)
                rho4_over_rho1 = analyzer_obs.density_ratio(M_3, teta_iter) * density_ratio_3 * density_ratio_2
                rho5_over_rho1 = analyzer_obs.density_ratio(Mach_inlet, Theta_total - teta_iter)
                total_pres_ratio_4 = analyzer_obs.total_pressure_ratio(M_3, teta_iter) * total_pres_ratio_3 * total_pres_ratio_2
                total_pres_ratio_5 = analyzer_obs.total_pressure_ratio(Mach_inlet, Theta_total - teta_iter)
                Beta4 = analyzer_obs.solve_beta_angle(M_3, teta_iter)
                Beta3 = analyzer_obs.solve_beta_angle(Mach_inlet, Theta_total - teta_iter)
                teta_iter = teta_iter * -1

                end_time = time.time()
                elapsed_time = end_time - start_time

                results = {
                    "Case": "Shock Wave",
                    "Inlet Mach": Mach_inlet,
                    "First Ramp Angle": Theta,
                    "Ramp Increase Angle": Theta_plus,
                    "Mach 2": M_2,
                    "Mach 3": M_3,
                    "Beta1": Beta1,
                    "Beta2": Beta2,
                    "Beta3": Beta3,
                    "Beta4": Beta4,
                    "P2/P1": P2_over_P1,
                    "P3/P1": P3_over_P2 * P2_over_P1,
                    "P4/P1": P4_over_P1,
                    "P5/P1": P5_over_P1,
                    "Theta": teta_iter,
                    "Mach 4": M_4,
                    "Mach 5": M_5,
                    "T4/T1": T4_over_T1,
                    "T5/T1": T5_over_T1,
                    "rho4/rho1": rho4_over_rho1,
                    "rho5/rho1": rho5_over_rho1,
                    "Pt4/Pt1": total_pres_ratio_4,
                    "Pt5/Pt1": total_pres_ratio_5,
                    "Iteration Count": iteration_count,
                    "Execution Time (s)": elapsed_time
                }
                for key, value in results.items():
                    print(f"{key}: {value}")
                save_to_csv(results)
            else:
                print(f"⚠️ No solution found for shock wave. ({MAX_ITERATIONS} iterations)")

        except Exception as e:
            print(f"❌ Error in shock wave calculation: {e}")

    return Mach_inlet, Theta, Theta_plus, Beta1, M_2, T2_over_T1_2, P2_over_P1, density_ratio_2, total_pres_ratio_2, Beta2, M_3, T3_over_T2*T2_over_T1_2, P3_over_P2*P2_over_P1, density_ratio_3*density_ratio_2, total_pres_ratio_3*total_pres_ratio_2, Beta3, M_4, T4_over_T1, P4_over_P1, rho4_over_rho1, total_pres_ratio_4, Beta4, M_5, T5_over_T1, P5_over_P1, rho5_over_rho1, total_pres_ratio_5, A, teta_iter, teta_iter+Theta+Theta_plus, iteration_count
