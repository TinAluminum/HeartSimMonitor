import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd


class ArduinoReader:
    def __init__(self, port_name):
        self.port_name = port_name
        self.ser = serial.Serial(port_name, 9600)
        time.sleep(2)  # Give some time for the connection to establish
        self.values = [None, None, None, None]
        self.running = True

    def read_value(self):
        while self.running:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8').rstrip()
                parts = line.split(',')
                if len(parts) == 4:
                    try:
                        self.values = [float(part.strip()) for part in parts]
                    except ValueError:
                        pass  # Ignore any non-numeric values
            time.sleep(0.1)  # Adjust the sleep time as necessary

    def stop(self):
        self.running = False
        if self.ser.is_open:
            self.ser.close()


class App:
    def __init__(self, root, arduino_reader, y_limits, value_ranges):
        self.root = root
        self.arduino_reader = arduino_reader
        self.value_ranges = value_ranges

        # Set background color of the Tkinter window
        self.root.config(bg='#457b9d')

        # Create labels for displaying the four values in a 2x8 grid
        self.labels = []
        self.mean_labels = []
        self.titles = ["P1", "P2", "F1", "F2"]
        for i, title in enumerate(self.titles):
            # Current value labels
            frame = tk.Frame(root, bg='#457b9d', padx=5, pady=5)
            frame.grid(row=0, column=i, padx=10, pady=10)  # 1st row for current values
            label_title = tk.Label(frame, text=title, font=("Consolas", 25), bg='#457b9d')
            label_title.pack(side=tk.LEFT)
            label_value = tk.Label(frame, text="Waiting for data...", font=("Consolas", 25), width=10, height=2,
                                   bg='white', relief='solid', borderwidth=1)
            label_value.pack(side=tk.LEFT)
            self.labels.append(label_value)

            # Mean value labels
            frame_mean = tk.Frame(root, bg='#457b9d', padx=5, pady=5)
            frame_mean.grid(row=1, column=i, padx=10, pady=10)  # 2nd row for mean values
            label_mean_title = tk.Label(frame_mean, text=f"Mean {title}", font=("Consolas", 25), bg='#457b9d')
            label_mean_title.pack(side=tk.LEFT)
            label_mean_value = tk.Label(frame_mean, text="Waiting for data...", font=("Consolas", 25), width=10,
                                        height=2,
                                        bg='white', relief='solid', borderwidth=1)
            label_mean_value.pack(side=tk.LEFT)
            self.mean_labels.append(label_mean_value)

        # Set up the plot with four subplots in a 2x2 grid
        self.fig, self.axs = plt.subplots(2, 2, figsize=(15, 4))
        self.fig.patch.set_facecolor('#457b9d')  # Set background color for the figure
        self.lines = []
        self.x_data = list(range(100))
        self.y_data = [[] for _ in range(4)]
        self.y_limits = y_limits
        for i, ax in enumerate(self.axs.flatten()):
            ax.set_facecolor('white')  # Set background color for the axes
            line, = ax.plot(self.x_data, [None] * 100, '#e63946')
            ax.grid(True)
            ax.set_xlim(0, 99)
            ax.set_ylim(self.y_limits[i])
            self.lines.append(line)

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=8, pady=20)

        self.update_labels()
        self.update_plot()

        self.new_button = tk.Button(root, text="Export session data", font=("Consolas", 15), command=self.export_to_excel)
        self.new_button.grid(row=4, column=0, columnspan=8, pady=10)

        self.update_labels()
        self.update_plot()

    def export_to_excel(self):
        print("Converting to excel")

        filename = "Output.xlsx"
        # Generate time data
        time = [i * 0.1 for i in range(len(self.y_data[0]))]

        # Create a dictionary with the data
        data_dict = {
            'Time (s)': time,
            'P1': self.y_data[0],
            'P2': self.y_data[1],
            'F1': self.y_data[2],
            'F2': self.y_data[3]
        }

        # Create a DataFrame
        df = pd.DataFrame(data_dict)

        # Save to Excel file
        df.to_excel(filename, index=False)


    def scale_value(self, value, original_range, new_range):
        return ((value - original_range[0]) / (original_range[1] - original_range[0])) * (new_range[1] - new_range[0]) + new_range[0]

    def update_labels(self):
        for i, value in enumerate(self.arduino_reader.values):
            if value is not None:
                scaled_value = self.scale_value(value, self.value_ranges[self.titles[i]]['original'], self.value_ranges[self.titles[i]]['new'])
                self.labels[i].config(text=f"{scaled_value:.2f}")
                self.y_data[i].append(scaled_value)

                if len(self.y_data[i]) > 100:
                    self.y_data[i].pop(0)

                mean_value = np.mean(self.y_data[i])
                self.mean_labels[i].config(text=f"{mean_value:.2f}")

        self.root.after(100, self.update_labels)

    def update_plot(self):
        if all(value is not None for value in self.arduino_reader.values):
            for i, value in enumerate(self.arduino_reader.values):
                self.lines[i].set_ydata(self.y_data[i] + [None] * (100 - len(self.y_data[i])))
            self.canvas.draw()
        self.root.after(100, self.update_plot)


def main_app(port_name):
    arduino_reader = ArduinoReader(port_name)
    threading.Thread(target=arduino_reader.read_value, daemon=True).start()

    root = tk.Tk()
    root.title("Arduino Data Display with Live Plot")

    # Set custom y-axis limits for each plot
    y_limits = [(0, 200), (0, 200), (0, 10), (0, 10)]  # Updated limits for P1 and P2 in new range

    # Define the original and new ranges for each value
    value_ranges = {
        "P1": {"original": (0, 0.2), "new": (0, 200)},
        "P2": {"original": (0, 0.2), "new": (0, 200)},
        "F1": {"original": (0, 10), "new": (0, 10)},
        "F2": {"original": (0, 10), "new": (0, 10)}
    }

    app = App(root, arduino_reader, y_limits, value_ranges)

    def on_closing():
        arduino_reader.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


def start_ui():
    def start_main_app():
        port_name = port_combobox.get()
        start_window.destroy()
        main_app(port_name)

    def list_ports():
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    start_window = tk.Tk()
    start_window.title("Select Port")

    tk.Label(start_window, text="Select Port Name:").pack(pady=10)
    available_ports = list_ports()
    port_combobox = ttk.Combobox(start_window, values=available_ports)
    port_combobox.pack(pady=10)
    port_combobox.set(available_ports[0] if available_ports else '')

    start_button = tk.Button(start_window, text="Start", command=start_main_app)
    start_button.pack(pady=10)

    start_window.mainloop()


if __name__ == "__main__":
    start_ui()
