import tkinter as tk
from threading import Thread
import time
import serial
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from datetime import datetime

class SerialPlotApp:
    def __init__(self, root, serial_port):
        self.root = root
        self.root.title("Serial Plotter")
        self.root.geometry("400x500")
        self.serial_port = serial_port

        # Current value labels
        self.value_labels = []
        for i in range(4):
            label = tk.Label(root, text=f"Value {i+1}: 0.00", font=("Helvetica", 16))
            label.pack(pady=5)
            self.value_labels.append(label)

        # Plot button
        self.plot_button = tk.Button(root, text="Plot", command=self.start_plot)
        self.plot_button.pack(pady=20)

        # Save button
        self.save_button = tk.Button(root, text="Save Data", command=self.save_data)
        self.save_button.pack(pady=20)

        self.running = False
        self.serial_thread = None
        self.ser = None
        self.data = []
        self.index = 0  # Initialize index for data entries
        self.start_time = time.time()  # Record the start time

        # Start serial reading thread immediately
        self.start_serial_thread()

    def update_values(self, values):
        for i, value in enumerate(values):
            self.value_labels[i].config(text=f"Value {i+1}: {value:.2f}")

    def read_serial_data(self):
        self.ser = serial.Serial(self.serial_port, 9600, timeout=1)
        while self.running:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    data = line.split(',')
                    if len(data) == 4:
                        values = [float(v) for v in data]
                        self.update_values(values)
                        self.record_data(values)
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(0.1)

    def record_data(self, values):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elapsed_time = time.time() - self.start_time  # Calculate elapsed time
        self.data.append([self.index, timestamp, elapsed_time] + values)
        self.index += 1

    def save_data(self):
        df = pd.DataFrame(self.data, columns=['Index', 'Timestamp', 'Elapsed Time', 'Pressure 1', 'Pressure 2', 'Flow Rate 1', 'Flow Rate 2'])
        filename = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        print(f"Data saved to {filename}")

    def start_serial_thread(self):
        self.running = True
        self.serial_thread = Thread(target=self.read_serial_data)
        self.serial_thread.start()

    def stop_serial_thread(self):
        self.running = False
        if self.serial_thread is not None:
            self.serial_thread.join()
        if self.ser is not None:
            self.ser.close()

    def start_plot(self):
        self.plot_serial_data()

    def plot_serial_data(self):
        # Initialize deque for storing data
        max_len = 20  # Maximum length of data to display
        pressure1_data = deque(maxlen=max_len)
        pressure2_data = deque(maxlen=max_len)
        flowrate1_data = deque(maxlen=max_len)
        flowrate2_data = deque(maxlen=max_len)

        # Initialize the plot
        fig, ax = plt.subplots(2, 2, figsize=(10, 8))

        def update_data():
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    data = line.split(',')
                    if len(data) == 4:
                        pressure1 = float(data[0])
                        pressure2 = float(data[1])
                        flowrate1 = float(data[2])
                        flowrate2 = float(data[3])
                        pressure1_data.append(pressure1)
                        pressure2_data.append(pressure2)
                        flowrate1_data.append(flowrate1)
                        flowrate2_data.append(flowrate2)
            except Exception as e:
                print(f"Error: {e}")

        def animate(i):
            update_data()

            for a in ax.flat:
                a.clear()
                a.set_facecolor('#2E2E2E')  # Set axes background to dark grey
                a.grid(True, color='white', linestyle='--', linewidth=0.5)  # Add grid with white color
                a.tick_params(axis='x', colors='white')  # Set x-axis ticks to white
                a.tick_params(axis='y', colors='white')  # Set y-axis ticks to white
                a.spines['bottom'].set_color('white')    # Set bottom spine to white
                a.spines['top'].set_color('white')       # Set top spine to white
                a.spines['left'].set_color('white')      # Set left spine to white
                a.spines['right'].set_color('white')     # Set right spine to white

            ax[0, 0].plot(pressure1_data, color='white')
            ax[0, 0].set_title('Pressure 1', color='white')
            ax[0, 0].set_ylim([-2, 2])

            ax[0, 1].plot(pressure2_data, color='white')
            ax[0, 1].set_title('Pressure 2', color='white')
            ax[0, 1].set_ylim([-2, 2])

            ax[1, 0].plot(flowrate1_data, color='white')
            ax[1, 0].set_title('Flow Rate 1', color='white')
            ax[1, 0].set_ylim([-2, 2])

            ax[1, 1].plot(flowrate2_data, color='white')
            ax[1, 1].set_title('Flow Rate 2', color='white')
            ax[1, 1].set_ylim([-2, 2])

        # Set up the animation
        ani = animation.FuncAnimation(fig, animate, interval=10)  # Interval is 10ms

        # Display the plot
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    serial_port = '/dev/cu.usbserial-1110'  # Define your serial port here
    root = tk.Tk()
    app = SerialPlotApp(root, serial_port)
    root.protocol("WM_DELETE_WINDOW", app.stop_serial_thread)
    root.mainloop()
