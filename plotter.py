import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque


def update_data(ser, pressure1_data, pressure2_data, flowrate1_data):
    try:
        line = ser.readline().decode('utf-8').strip()
        if line:
            data = line.split(',')
            if len(data) == 3:
                pressure1 = float(data[0])
                pressure2 = float(data[1])
                flowrate1 = float(data[2])
                pressure1_data.append(pressure1)
                pressure2_data.append(pressure2)
                flowrate1_data.append(flowrate1)
    except Exception as e:
        print(f"Error: {e}")


def animate(ser, ax, pressure1_data, pressure2_data, flowrate1_data):

    update_data(ser, pressure1_data, pressure2_data, flowrate1_data)

    ax[0].clear()
    ax[0].plot(pressure1_data)
    ax[0].set_title('Pressure 1')
    ax[0].set_ylim([0, 2])

    ax[1].clear()
    ax[1].plot(pressure2_data)
    ax[1].set_title('Pressure 2')
    ax[1].set_ylim([-0.1, 1])

    ax[2].clear()
    ax[2].plot(flowrate1_data)
    ax[2].set_title('Flow Rate 1')
    ax[2].set_ylim([0, 1])

def real_time_plot(port):
    # '/dev/cu.usbserial-1110'
    # Initialize serial connection (change 'COM3' to the correct port for your Arduino)
    ser = serial.Serial(port, 9600, timeout=1)

    # Initialize deque for storing data
    max_len = 100  # Maximum length of data to display
    pressure1_data = deque(maxlen=max_len)
    pressure2_data = deque(maxlen=max_len)
    flowrate1_data = deque(maxlen=max_len)

    # Initialize the plot
    fig, ax = plt.subplots(3, 1, figsize=(10, 8))


    # Set up the animation
    ani = animation.FuncAnimation(fig, animate(ser, ax, pressure1_data, pressure2_data, flowrate1_data), interval=10)  # Interval is 500ms

    # Display the plot
    plt.tight_layout()
    plt.show()
