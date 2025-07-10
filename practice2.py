import tkinter as tk
from tkinter import ttk
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from joblib import dump, load
import os

# ---------- Step 1: Generate Training Data ----------
def generate_traffic_dataset(file_path="traffic_data.csv", samples=300):
    if os.path.exists(file_path):
        return
    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        header = ['N_car', 'N_bus', 'N_amb', 'N_emg',
                  'S_car', 'S_bus', 'S_amb', 'S_emg',
                  'E_car', 'E_bus', 'E_amb', 'E_emg',
                  'W_car', 'W_bus', 'W_amb', 'W_emg',
                  'Green_Direction']
        writer.writerow(header)

        for _ in range(samples):
            vehicle_data = {
                d: {'car': random.randint(0, 10),
                    'bus': random.randint(0, 2),
                    'ambulance': random.randint(0, 1),
                    'emergency_car': random.randint(0, 1)}
                for d in ['N', 'S', 'E', 'W']
            }

            def score(v): return v['car'] + 3*v['bus'] + 100*v['ambulance'] + 50*v['emergency_car']
            scores = {d: score(v) for d, v in vehicle_data.items()}
            green = max(scores, key=scores.get)

            row = []
            for d in ['N', 'S', 'E', 'W']:
                row.extend([vehicle_data[d]['car'], vehicle_data[d]['bus'],
                            vehicle_data[d]['ambulance'], vehicle_data[d]['emergency_car']])
            row.append(green)
            writer.writerow(row)

# ---------- Step 2: Train ML Model ----------
def train_model(csv_file="traffic_data.csv", model_file="traffic_model.pkl"):
    data = pd.read_csv(csv_file)
    X = data.drop("Green_Direction", axis=1)
    y = data["Green_Direction"]

    model = RandomForestClassifier()
    model.fit(X, y)
    dump(model, model_file)

# ---------- Step 3: Load ML Model ----------
generate_traffic_dataset()
train_model()
model = load("traffic_model.pkl")

# ---------- Step 4: AI + ML Decision Logic ----------
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

def determine_green_direction(vehicle_data):
    input_features = []
    for d in ['North', 'South', 'East', 'West']:
        v = vehicle_data[d]
        input_features.extend([v['car'], v['bus'], v['ambulance'], v['emergency_car']])
    pred = model.predict([input_features])[0]
    return {'N': 'North', 'S': 'South', 'E': 'East', 'W': 'West'}[pred]

# ---------- Step 5: GUI Application ----------
class TrafficUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚦 AI + ML Smart Traffic Controller")

        self.canvas = tk.Canvas(root, width=400, height=400, bg="lightgrey")
        self.canvas.pack()

        self.status = tk.Label(root, text="", font=("Arial", 12), justify="left")
        self.status.pack(pady=5)

        self.chart_frame = ttk.Frame(root)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(4.5, 3))
        self.canvas_chart = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas_chart.get_tk_widget().pack()

    def update_graph(self, vehicle_counts):
        directions = ['North', 'South', 'East', 'West']
        scores = []
        for d in directions:
            v = vehicle_counts[d]
            score = v['car'] + 3*v['bus'] + 100*v['ambulance'] + 50*v['emergency_car']
            scores.append(score)

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
            color = "#00FF00" if direction == green_dir else "#FF3C3C"
            border = 4 if direction == green_dir else 1
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=border)

            v = vehicle_counts[direction]
            label = f"{direction}\n🚗 {v['car']} 🚌 {v['bus']}\n🚑 {v['ambulance']} ⚠️ {v['emergency_car']}"
            tx, ty = label_offsets[direction]
            self.canvas.create_text(tx, ty, text=label, fill="black", font=("Arial", 9), anchor="n")

        self.status.config(text=f"🟢 {green_dir} is GREEN (ML prediction)")
        self.root.update()

def run_simulation():
    root = tk.Tk()
    app = TrafficUI(root)

    def update_cycle():
        vehicle_counts = simulate_vehicle_flow()
        green_direction = determine_green_direction(vehicle_counts)
        app.update_traffic_view(green_direction, vehicle_counts)
        app.update_graph(vehicle_counts)
        root.after(3000, update_cycle)

    update_cycle()
    root.mainloop()

if __name__ == "__main__":
    run_simulation()
