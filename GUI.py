import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from Same_Family_Shock_Solver import Intersection_of_Shock_Waves_Same_Family
from Oblique_Shock_Solver import ObliqueShockAnalyzer
from Expansion_Wave_Solver import PrandtlMeyerExpansion
from Graphics import plot_pressure_theta_analysis
from Animation import supersonic_animation_tkinter

# -------------------- ANALYZER --------------------
analyzer_obs = ObliqueShockAnalyzer()
analyzer_pm = PrandtlMeyerExpansion()

# -------------------- WINDOW --------------------
root = tk.Tk()
root.title("Same Family Shock Wave Intersection")
root.geometry("1920x1080")

# -------------------- LEFT FRAME --------------------
left_frame = tk.Frame(root, width=350, height=1080, bg="#CACACA")
left_frame.pack(side=tk.LEFT, fill=tk.Y)
left_frame.pack_propagate(False)

# Entry variables
mach_inlet = tk.DoubleVar()
Theta1_var = tk.DoubleVar()
Theta_plus_var = tk.DoubleVar()

# -------------------- MIDDLE FRAME --------------------
middle_frame = tk.Frame(root, width=700, height=1080, bg="#EDEDED")
middle_frame.pack(side=tk.LEFT, fill=tk.Y)
middle_frame.pack_propagate(False)

# Region selection Combobox
tk.Label(middle_frame, text="Select Region", font=("Arial", 14), bg="#EDEDED").pack(pady=15)
regions = ["Region 1", "Region 2", "Region 3", "Region 4"]
region_combobox = ttk.Combobox(middle_frame, values=regions, font=("Arial", 14), width=30, state="readonly",
                               background="#EDEDED")
region_combobox.current(0)
region_combobox.pack(pady=10)

# Bind Entry variables
Beta_var = tk.DoubleVar()
Mach_var = tk.DoubleVar()
T_var = tk.DoubleVar()
P_var = tk.DoubleVar()
density_var = tk.DoubleVar()
total_pres_var = tk.DoubleVar()
Theta_region_var = tk.DoubleVar()
Status_var = tk.StringVar()

entries_labels = ["Mach Number", "Temperature Ratio", "Density Ratio", "Beta",
                  "Pressure Ratio", "Total Pressure Ratio", "Theta"]
entries_vars = [Mach_var, T_var, density_var, Beta_var, P_var, total_pres_var, Theta_region_var]

for lbl, var in zip(entries_labels, entries_vars):
    tk.Label(middle_frame, text=lbl, font=("Arial", 14), bg="#EDEDED").pack(pady=10)
    tk.Entry(middle_frame, font=("Arial", 14), width=35, textvariable=var, state="readonly").pack(pady=5)

tk.Label(middle_frame, text="STATUS", font=("Arial", 14), bg="#EDEDED").pack(pady=10)
tk.Label(middle_frame, textvariable=Status_var, font=("Arial", 14), bg="#EDEDED", wraplength=650, justify="center").pack(
    pady=65)
tk.Label(middle_frame, text="The calculated ratios are relative to the inlet region.",
         font=("Arial", 14), bg="#EDEDED", wraplength=650, justify="center").pack(pady=30)

# -------------------- CALCULATED VALUES --------------------
calculated_values = {}
photo1 = None
photo2 = None
theta_iter = 0
theta_iter2 = 0
Status = 0


def update_entries(region):
    if region in calculated_values:
        Beta_var.set(round(calculated_values[region][0], 4))
        Mach_var.set(round(calculated_values[region][1], 4))
        T_var.set(round(calculated_values[region][2], 4))
        P_var.set(round(calculated_values[region][3], 4))
        density_var.set(round(calculated_values[region][4], 4))
        total_pres_var.set(round(calculated_values[region][5], 4))
        Theta_region_var.set(round(calculated_values[region][6], 4))


def calculate():
    global photo1, photo2, theta_iter, theta_iter2, Status, iteration_count_val

    # Clear error message
    error_label.config(text="", fg="red")

    ITER_NUM = 1000
    iteration_count_val = float('inf')  # Default value
    result = None  # Predefine result

    try:
        Mach_inlet_val = mach_inlet.get()
        Theta_val = Theta1_var.get()
        Theta_plus_val = Theta_plus_var.get()

        # Function call
        result = Intersection_of_Shock_Waves_Same_Family(
            Mach_inlet_val, Theta_val, Theta_plus_val, ITER_NUM
        )

        # Iteration count control
        iteration_count_val = result[-1]  # Last element is iteration_count

        # Unpack results
        [Mach_inlet_out, Theta_out, Theta_plus_out, Beta1, M_2, T2_over_T1_2, P2_over_P1,
         density_ratio_2, total_pres_ratio_2, Beta2, M_3, T3_over_T2, P3_over_P1,
         density_ratio_3, total_pres_ratio_3, Beta3, M_4, T4_over_T1, P4_over_P1, rho4_over_rho1,
         total_pres_ratio_4, Beta4, M_5, T5_over_T1, P5_over_P1, rho5_over_rho1, total_pres_ratio_5,
         Status, theta_iter, theta_iter2, _] = result

        # Store calculated values
        calculated_values["Region 1"] = [Beta1, M_2, T2_over_T1_2, P2_over_P1, density_ratio_2, total_pres_ratio_2,
                                         Theta_val]
        calculated_values["Region 2"] = [Beta2, M_3, T3_over_T2, P3_over_P1, density_ratio_3, total_pres_ratio_3,
                                         Theta_plus_val]
        calculated_values["Region 3"] = [Beta3, M_5, T5_over_T1, P5_over_P1, rho5_over_rho1, total_pres_ratio_5,
                                         theta_iter2]
        calculated_values["Region 4"] = [Beta4, M_4, T4_over_T1, P4_over_P1, rho4_over_rho1, total_pres_ratio_4,
                                         theta_iter]

        # Status message
        if Status == 0:
            Status_var.set("Shock Wave Forms")
        else:
            Status_var.set("Expansion Wave Forms")

        update_entries("Region 1")

        # Graph calculation and display
        P3_over_P2 = P3_over_P1 / P2_over_P1
        Theta_Total = Theta_val + Theta_plus_val
        plot_pressure_theta_analysis(Mach_inlet_val, M_2, M_3, Theta_val, Theta_Total,
                                     P2_over_P1, P3_over_P2, Status, analyzer_obs, analyzer_pm,
                                     True, (10, 6))

        img1_tmp = Image.open("graph.png").resize((820, 400))
        photo1 = ImageTk.PhotoImage(img1_tmp)
        canvas1.create_image(0, 0, anchor=tk.NW, image=photo1)

        img2_tmp = Image.open("graph_zoomed.png").resize((820, 400))
        photo2 = ImageTk.PhotoImage(img2_tmp)
        canvas2.create_image(0, 0, anchor=tk.NW, image=photo2)

    except UnboundLocalError as e:
        if "Beta3" in str(e):
            if result is not None and len(result) > 0:
                try:
                    iteration_count_val = result[-1]
                except (IndexError, TypeError):
                    pass
            if ITER_NUM <= iteration_count_val:
                error_label.config(text="Increase iteration count")
                print(f"Iteration count: {iteration_count_val}")
            else:
                error_label.config(text="Input theta is larger than max theta, detached shock occurs!")
        else:
            error_label.config(text=f"Variable Error: {str(e)}")

    except ValueError as e:
        error_label.config(text=f"Input Error: {str(e)}")
    except FileNotFoundError as e:
        error_label.config(text=f"File Not Found: {str(e)}")
    except Exception as e:
        error_label.config(text=f"Error: {str(e)}")


# -------------------- LEFT FRAME --------------------
tk.Label(left_frame, text="Mach", font=("Arial", 14), bg="#CACACA").pack(pady=15)
tk.Entry(left_frame, textvariable=mach_inlet, font=("Arial", 14), width=25).pack(pady=10)

tk.Label(left_frame, text="Theta1", font=("Arial", 14), bg="#CACACA").pack(pady=15)
tk.Entry(left_frame, textvariable=Theta1_var, font=("Arial", 14), width=25).pack(pady=10)

tk.Label(left_frame, text="Theta2", font=("Arial", 14), bg="#CACACA").pack(pady=15)
tk.Entry(left_frame, textvariable=Theta_plus_var, font=("Arial", 14), width=25).pack(pady=10)

tk.Button(left_frame, text="Calculate", font=("Arial", 14), bg="#FBFBFB", command=calculate).pack(pady=20)

# Photo under calculate button
photo_label = tk.Label(left_frame, bg="lightgray")
photo_label.pack(pady=10)
photo_img = Image.open("photo.png")
photo_img = photo_img.resize((300, 200))
photo_img_tk = ImageTk.PhotoImage(photo_img)
photo_label.config(image=photo_img_tk)  # type: ignore
photo_label.image = photo_img_tk


# -------------------- Flow Animation Button --------------------
def run_animation():
    if not calculated_values:
        error_label.config(text="Please run calculation first!")
        return

    try:
        Theta_out_val = calculated_values["Region 1"][6]
        Theta_plus_out_val = Theta_plus_var.get()
        Beta1_val = calculated_values["Region 1"][0]
        Beta2_val = calculated_values["Region 2"][0]
        Beta3_val = calculated_values["Region 3"][0]
        Beta4_val = calculated_values["Region 4"][0]
        supersonic_animation_tkinter(
            Theta_out_val,
            Theta_plus_out_val,
            Beta1_val,
            Beta2_val + Theta_out_val,
            Beta4_val,
            Beta3_val + Theta_out_val,
            theta_iter,
            Status,
            1,
            2500
        )
        # Clear error message if animation ran successfully
        error_label.config(text="")
    except Exception as e:
        error_message = f"Animation Error: {str(e)}"
        error_label.config(text=error_message)


tk.Button(left_frame, text="Run Flow Animation", font=("Arial", 14), bg="#FBFBFB",
          command=run_animation).pack(pady=30)

# Error message label (under animation button)
error_label = tk.Label(left_frame, text="", font=("Arial", 12), bg="#CACACA", fg="red", wraplength=300,
                       justify="center")
error_label.pack(pady=10)

# -------------------- RIGHT FRAME --------------------
right_frame = tk.Frame(root, width=870, height=1080, bg="#EDEDED")
right_frame.pack(side=tk.LEFT, fill=tk.Y)
right_frame.pack_propagate(False)

tk.Label(right_frame, text="Pressure-Deflection Angle Diagram", font=("Arial", 14), bg="#EDEDED").pack(pady=15)
canvas1 = tk.Canvas(right_frame, width=820, height=400, bg="white")
canvas1.pack(pady=10)

canvas2 = tk.Canvas(right_frame, width=820, height=400, bg="white")
canvas2.pack(pady=10)

region_combobox.bind("<<ComboboxSelected>>", lambda event: update_entries(region_combobox.get()))

# -------------------- START APP --------------------
root.mainloop()
