
import tkinter as tk
from tkinter import ttk
import random
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# ---------- AI Logic ----------

def calculate_weighted_score(vehicles):
    return (
        vehicles.get('car', 0) * 1 +
        vehicles.get('bus', 0) * 3 +
        vehicles.get('ambulance', 0) * 100 +
        vehicles.get('emergency_car', 0) * 50
    )

def determine_green_direction(vehicle_data):
    scores = {direction: calculate_weighted_score(data) for direction, data in vehicle_data.items()}
    return max(scores, key=scores.get)

# ---------- Traffic Simulation ----------

def simulate_vehicle_flow():
    return {
        'North': {'car': random.randint(0, 10), 'bus': random.randint(0, 2),
                  'ambulance': random.randint(0, 1), 'emergency_car': random.randint(0, 1)},
        'South': {'car': random.randint(0, 10), 'bus': random.randint(0, 2),
                  'ambulance': random.randint(0, 1), 'emergency_car': random.randint(0, 1)},
        'East':  {'car': random.randint(0, 10), 'bus': random.randint(0, 2),
                  'ambulance': random.randint(0, 1), 'emergency_car': random.randint(0, 1)},
        'West':  {'car': random.randint(0, 10), 'bus': random.randint(0, 2),
                  'ambulance': random.randint(0, 1), 'emergency_car': random.randint(0, 1)}
    }

# ---------- GUI with Embedded Chart ----------


class TrafficUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚦 AI Smart Traffic Controller")
        # Upper frame for simulation
        self.canvas = tk.Canvas(root, width=400, height=400, bg="lightgrey")
        self.canvas.pack()

        self.status = tk.Label(root, text="", font=("Arial", 12), justify="left")
        self.status.pack(pady=5)

        # Lower frame for live graph
        self.chart_frame = ttk.Frame(root)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(4.5, 3))
        self.canvas_chart = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas_chart.get_tk_widget().pack()

    def update_graph(self, vehicle_counts):
        directions = ['North', 'South', 'East', 'West']
        scores = [calculate_weighted_score(vehicle_counts[d]) for d in directions]

        self.ax.clear()
        self.ax.bar(directions, scores, color=['pink', 'orange', 'blue', 'skyblue'])
        self.ax.set_title("Live Traffic Load")
        self.ax.set_ylim(0, 150)
        self.ax.set_ylabel("Weighted Score")
        self.canvas_chart.draw()

    def update_traffic_view(self, green_dir, vehicle_counts):
        self.canvas.delete("all")
        directions = ['North', 'South', 'East', 'West']
        positions = {
            'North': (150, 50, 250, 100),
            'South': (150, 300, 250, 350),
            'West':  (50, 150, 100, 250),
            'East':  (300, 150, 350, 250)
        }
        label_offsets = {
            'North': (200, 105),
            'South': (200, 355),
            'West':  (75, 255),
            'East':  (325, 255)
        }

        for direction in directions:
            x1, y1, x2, y2 = positions[direction]
            color = "green" if direction == green_dir else "red"
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
            if direction == green_dir:
                self.canvas.create_rectangle(x1-5, y1-5, x2+5, y2+5, outline="black", width=3)

            v = vehicle_counts[direction]
            label = f"{direction}\n🚗 {v['car']} 🚌 {v['bus']}\n🚑 {v['ambulance']} ⚠️ {v['emergency_car']}"
            tx, ty = label_offsets[direction]
            self.canvas.create_text(tx, ty, text=label, fill="black", font=("Arial", 9), anchor="n")

        self.status.config(text=f"🟢 {green_dir} is GREEN (highest priority)")
        self.root.update()

# ---------- Main Simulation

def run_simulation():
    root = tk.Tk()
    app = TrafficUI(root)

    def update_every_cycle():
        vehicle_counts = simulate_vehicle_flow()
        best_direction = determine_green_direction(vehicle_counts)
        app.update_traffic_view(best_direction, vehicle_counts)
        app.update_graph(vehicle_counts)
        root.after(3000, update_every_cycle)

    update_every_cycle()
    root.mainloop()

if __name__ == "__main__":
    run_simulation()
