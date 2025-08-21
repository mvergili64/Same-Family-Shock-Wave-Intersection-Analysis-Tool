import tkinter as tk
import turtle
import math
import numpy as np

def supersonic_animation_tkinter(Teta1=10, Teta2=12, Beta1=39, Beta2=62,
                                 Beta3=57.06, Beta4=57.58, teta_iter=0.27,
                                 Case=0, speedt=1, step_num=2500):

    root = tk.Tk()
    root.title("Supersonic Animation")
    root.geometry("1366x768")

    canvas = tk.Canvas(root, width=1366, height=500)
    canvas.pack()

    screen = turtle.TurtleScreen(canvas)
    screen.tracer(0)

    # Flags
    running = tk.BooleanVar(value=False)
    step = tk.IntVar(value=0)

    # Animation parameters will be kept globally
    turtles = {}
    paths = {}

    def setup_scene():
        """Ground + all initial turtles and paths setup"""
        nonlocal turtles, paths

        screen.clearscreen()  # clear on every reset
        screen.tracer(0)

        # === Ground ===
        ground = turtle.RawTurtle(screen)
        ground.hideturtle()
        ground.speed(0)
        ground.penup()
        ground.goto(-680, -200)
        ground.pendown()
        ground.forward(200)
        teta1_start = ground.pos()
        ground.left(Teta1)
        ground.forward(200)
        teta2_start = ground.pos()
        ground.left(Teta2)
        ground.forward(400)

        # Functions
        def find_x_for_y(y_target, x0, y0, angle_deg):
            angle_rad = np.radians(angle_deg)
            m = np.tan(angle_rad)
            x_target = x0 + (y_target - y0) / m
            return x_target, y_target

        def intersect(p1, angle1, p2, angle2):
            a1 = math.radians(angle1)
            a2 = math.radians(angle2)
            x1, y1 = p1
            x2, y2 = p2
            dx1, dy1 = math.cos(a1), math.sin(a1)
            dx2, dy2 = math.cos(a2), math.sin(a2)
            det = dx1 * (-dy2) - dy1 * (-dx2)
            if abs(det) < 1e-6:
                return None
            t = ((x2 - x1) * (-dy2) - (y2 - y1) * (-dx2)) / det
            xi = x1 + t * dx1
            yi = y1 + t * dy1
            return (xi, yi)

        # === Shock intersection point ===
        P1 = intersect(teta1_start, Beta1, teta2_start, Beta2)

        # === Red lines ===
        red = turtle.RawTurtle(screen)
        red.hideturtle()
        red.color("red")
        red.speed(0)

        if P1:
            red.pensize(2)
            red.penup(); red.goto(teta1_start); red.pendown(); red.goto(P1)
            red.penup(); red.goto(teta2_start); red.pendown(); red.goto(P1)

            if Case == 0:
                my_color="red"
                red.penup(); red.goto(P1); red.color(my_color); red.setheading(0)
                red.pendown()
                P_1 = intersect(P1, 180 - Beta3, teta2_start, Teta1 + Teta2)
                red.goto(P_1)
            else:
                my_color="purple"
                for t in range(-1,2,1):
                    red.penup(); red.goto(P1); red.color(my_color); red.setheading(0)
                    red.pendown()
                    P_1 = intersect(P1, 180 - Beta3+(t*5), teta2_start, Teta1 + Teta2)
                    red.goto(P_1)

            red.color("red")
            red.penup(); red.goto(P1); red.setheading(0)
            red.pendown(); red.left(Beta4); red.forward(200)

            # Slip-line
            red.color("black")
            red.penup(); red.goto(P1); red.setheading(0)
            red.pendown(); red.left(Teta1+Teta2+teta_iter)
            for _ in range(int(200/20/2)):
                red.pendown(); red.forward(20)
                red.penup(); red.forward(20)

        # === Flow turtles ===
        starty = P1[1] - 50
        Flow = turtle.RawTurtle(screen)
        Flow.hideturtle(); Flow.color("blue"); Flow.speed(0)
        Flow.penup(); Flow.goto(-600, starty); Flow.pendown(); Flow.pensize(3)

        Flow1 = turtle.RawTurtle(screen)
        Flow1.hideturtle(); Flow1.color("blue"); Flow1.speed(0)
        Flow1.penup(); Flow1.goto(-600, P1[1] + 50); Flow1.pendown(); Flow1.pensize(3)

        # === Target paths ===
        flow_paths = []
        P = find_x_for_y(starty, teta1_start[0], teta1_start[1], Beta1)
        flow_paths.append(P)
        P = intersect(teta2_start, Beta2, P, Teta1)
        flow_paths.append(P)
        P = intersect(P1, 180 - Beta3, P, Teta1 + Teta2)
        flow_paths.append(P)

        flow1_paths = []
        P = find_x_for_y(P1[1] + 50, P1[0], P1[1], Beta4)
        flow1_paths.append(P)

        # Store parameters
        turtles = {
            "Flow": Flow, "Flow1": Flow1
        }
        paths = {
            "flow_paths": flow_paths,
            "flow1_paths": flow1_paths,
            "Flow_final_angle": Teta1+Teta2+teta_iter,
            "Flow1_final_angle": Teta1+Teta2+teta_iter,
            "Flow_final_distance": 150,
            "Flow1_final_distance": 150,
            "Flow_final_started": False,
            "Flow1_final_started": False
        }
        screen.update()

    # === Animation ===
    def animate():
        if not running.get():
            return
        if step.get() >= step_num:
            return

        Flow = turtles["Flow"]
        Flow1 = turtles["Flow1"]

        # Flow movement
        if paths["flow_paths"]:
            target = paths["flow_paths"][0]
            Flow.setheading(Flow.towards(target))
            Flow.forward(speedt)
            if Flow.distance(target) < speedt:
                Flow.goto(target)
                paths["flow_paths"].pop(0)
                if not paths["flow_paths"]:
                    paths["Flow_final_started"] = True
                    Flow.setheading(paths["Flow_final_angle"])
        elif paths["Flow_final_started"] and paths["Flow_final_distance"] > 0:
            step_move = min(speedt, paths["Flow_final_distance"])
            Flow.forward(step_move)
            paths["Flow_final_distance"] -= step_move

        # Flow1 movement
        if paths["flow1_paths"]:
            target = paths["flow1_paths"][0]
            Flow1.setheading(Flow1.towards(target))
            Flow1.forward(speedt)
            if Flow1.distance(target) < speedt:
                Flow1.goto(target)
                paths["flow1_paths"].pop(0)
                if not paths["flow1_paths"]:
                    paths["Flow1_final_started"] = True
                    Flow1.setheading(paths["Flow1_final_angle"])
        elif paths["Flow1_final_started"] and paths["Flow1_final_distance"] > 0:
            step_move = min(speedt, paths["Flow1_final_distance"])
            Flow1.forward(step_move)
            paths["Flow1_final_distance"] -= step_move

        step.set(step.get()+1)
        screen.update()
        root.after(10, animate)

    # === Buttons ===
    def start_anim():
        if not running.get():
            running.set(True)
            animate()

    def stop_anim():
        running.set(False)

    def reset_anim():
        running.set(False)
        step.set(0)
        setup_scene()

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Button(frame, text="Start", command=start_anim, width=10).pack(side="left", padx=5)
    tk.Button(frame, text="Stop", command=stop_anim, width=10).pack(side="left", padx=5)
    tk.Button(frame, text="Reset", command=reset_anim, width=10).pack(side="left", padx=5)

    # Draw ground immediately at the start
    setup_scene()

    root.mainloop()




