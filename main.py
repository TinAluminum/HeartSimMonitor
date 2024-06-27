import tkinter as tk
import serial
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
    def __init__(self, root, arduino_reader, y_limits):
        self.root = root
        self.arduino_reader = arduino_reader

        # Set background color of the Tkinter window
        self.root.config(bg='#457b9d')

        # Create labels for displaying the four values in a 2x2 grid
        self.labels = []
        self.titles = ["P1", "P2", "F1", "F2"]
        for i, title in enumerate(self.titles):
            frame = tk.Frame(root, bg='#457b9d', padx=5, pady=5)
            frame.grid(row=i//2, column=i%2, padx=10, pady=10)  # 2x2 grid
            label_title = tk.Label(frame, text=title, font=("Consolas", 25), bg='#457b9d')
            label_title.pack(side=tk.LEFT)
            label_value = tk.Label(frame, text="Waiting for data...", font=("Consolas", 25), width=10, height=2,
                                   bg='white', relief='solid', borderwidth=1)
            label_value.pack(side=tk.LEFT)
            self.labels.append(label_value)

        # Set up the plot with four subplots in a 2x2 grid
        self.fig, self.axs = plt.subplots(2, 2, figsize=(5, 3))
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
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=2, pady=20)

        self.update_labels()
        self.update_plot()

    def update_labels(self):
        for i, value in enumerate(self.arduino_reader.values):
            if value is not None:
                self.labels[i].config(text=f"{value:.2f}")
        self.root.after(100, self.update_labels)

    def update_plot(self):
        if all(value is not None for value in self.arduino_reader.values):
            for i, value in enumerate(self.arduino_reader.values):
                self.y_data[i].append(value)
                if len(self.y_data[i]) > 100:
                    self.y_data[i].pop(0)
                self.lines[i].set_ydata(self.y_data[i] + [None] * (100 - len(self.y_data[i])))
            self.canvas.draw()
        self.root.after(100, self.update_plot)

def main():
    port_name = '/dev/cu.usbserial-1110'  # Replace with your actual port name

    arduino_reader = ArduinoReader(port_name)
    threading.Thread(target=arduino_reader.read_value, daemon=True).start()

    root = tk.Tk()
    root.title("Arduino Data Display with Live Plot")

    # Set custom y-axis limits for each plot
    y_limits = [(-3, 3), (-3, 3), (0, 10), (0, 10)]  # Replace with your desired limits

    app = App(root, arduino_reader, y_limits)

    def on_closing():
        arduino_reader.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()