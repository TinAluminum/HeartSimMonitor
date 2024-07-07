import asyncio
import math
import serial
import serial.tools.list_ports
import serial_asyncio
import threading
import tkinter as tk
from tkinter import ttk
import time

class SerialWriter:
    def __init__(self, port, loop):
        self.loop = loop
        self.port = port
        self.writer = None
        self.start_time = time.time()

    async def connect(self):
        _, self.writer = await serial_asyncio.open_serial_connection(url=self.port, baudrate=9600)

    async def write_data(self):
        while True:
            elapsed_time = time.time() - self.start_time
            cosine_value = 100 * (1 + math.cos(2 * math.pi * elapsed_time / 10))  # Period of 10 seconds, amplitude 0 to 200
            cosine_value_2 = 100 * (1 + math.cos(2 * math.pi * elapsed_time / 10 + math.pi))  # Another cosine with phase shift
            tan_value = math.tan(elapsed_time)
            sec_value = 1 / math.cos(elapsed_time)
            try:
                tan_value = min(max(tan_value, -200), 200)  # Limit the tan value to prevent overflow
                sec_value = min(max(sec_value, -200), 200)  # Limit the sec value to prevent overflow
            except ValueError:
                tan_value = 200
                sec_value = 200

            data = f"{cosine_value:.2f}, {cosine_value_2:.2f}, {tan_value:.2f}, {sec_value:.2f}\n"
            if self.writer:
                self.writer.write(data.encode())
            await asyncio.sleep(0.1)  # Adjust the sleep time for the desired data rate

class SerialReader(asyncio.Protocol):
    def __init__(self, app):
        self.app = app

    def data_received(self, data):
        message = data.decode('utf-8').strip()
        self.app.update_received_data(message)

class App:
    def __init__(self, root, writer):
        self.root = root
        self.writer = writer
        self.received_data = tk.StringVar()
        self.received_data.set("")

        self.setup_ui()

    def setup_ui(self):
        self.root.title("Serial Communication")

        tk.Label(self.root, text="Send Data:").pack(pady=10)
        self.data_entry = tk.Entry(self.root)
        self.data_entry.pack(pady=10)

        send_button = tk.Button(self.root, text="Send", command=self.send_data)
        send_button.pack(pady=10)

        tk.Label(self.root, text="Received Data:").pack(pady=10)
        self.received_label = tk.Label(self.root, textvariable=self.received_data, width=40, height=10, bg="white", relief="solid")
        self.received_label.pack(pady=10)

    def send_data(self):
        data = self.data_entry.get()
        asyncio.run_coroutine_threadsafe(self.writer.write_data(data + "\n"), loop)

    def update_received_data(self, data):
        current_data = self.received_data.get()
        new_data = current_data + data + "\n"
        self.received_data.set(new_data)

def start_serial_communication(port_name):
    global loop
    loop = asyncio.get_event_loop()

    writer = SerialWriter(port_name, loop)
    loop.run_until_complete(writer.connect())

    root = tk.Tk()
    app = App(root, writer)

    reader_protocol = SerialReader(app)
    serial_asyncio.create_serial_connection(loop, lambda: reader_protocol, url=port_name, baudrate=9600)

    def start_loop():
        loop.run_forever()

    threading.Thread(target=start_loop, daemon=True).start()

    # Start writing data
    asyncio.run_coroutine_threadsafe(writer.write_data(), loop)

    root.mainloop()

def start_ui():
    def start_main_app():
        port_name = port_combobox.get()
        start_window.destroy()
        start_serial_communication(port_name)

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
