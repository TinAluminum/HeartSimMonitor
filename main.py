import tkinter as tk
from plotter import real_time_plot

def plot():
    print("Button Pressed!")

# Create the main window
root = tk.Tk()
root.title("Basic Tkinter Page")
root.geometry("500x400")

# Create a button with specified properties
button = tk.Button(root, text="Plot", command=real_time_plot('/dev/cu.usbserial-1110'), width=5, height=2)
button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Run the application
root.mainloop()
