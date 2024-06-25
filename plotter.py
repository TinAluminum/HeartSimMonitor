import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

def plot_serial_data(port):
    # Set the background color using hex code
    plt.rcParams['figure.facecolor'] = '#2E2E2E'  # Dark grey
    plt.rcParams['axes.facecolor'] = '#2E2E2E'    # Dark grey

    # Initialize serial connection
    ser = serial.Serial(port, 9600, timeout=1)

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
            line = ser.readline().decode('utf-8').strip()
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


