import tkinter as tk
from tkinter import ttk
import serial
import threading
import time
from datetime import datetime
import serial.tools.list_ports

# Initialize the serial connection
def init_serial(port):
    global ser
    try:
        ser = serial.Serial(port, 9600, timeout=1)  # Use the selected COM port
        time.sleep(2)
        if not ser.is_open:
            ser.open()
        print('COM is open:', ser.is_open)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        exit(1)

# Send command to Arduino
def send_command(command):
    global ser
    ser.write((command + '\n').encode())  # Send the command with a newline
    time.sleep(0.5)  # Give some time for the Arduino to process

# Read data from the serial port
def read_from_arduino():
    global lid_status, run_status
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(f"Received: {line}")
            display_serial_text(line)
            if line.startswith("NANO : "):
                command = line.split(" : ")[1].strip()
                if command == "LID OPEN":
                    update_circle_color("red")
                    canvas.itemconfig(text_run_status, text="STOP")
                    canvas.itemconfig(text_lid_status, text="LID : OPENED")
                    lid_status = True
                    run_status = False
                    left_button.config(text="START PROCESS", background="forestgreen")
                elif command == "LID CLOSE":
                    update_circle_color("lime")
                    canvas.itemconfig(text_run_status, text="READY")
                    canvas.itemconfig(text_lid_status, text="LID : CLOSED")
                    lid_status = False
                elif command == "FINISH":
                    # send_command("PC : OPEN")
                    # display_serial_text("PC : STOP")
                    left_button.config(text="START PROCESS", background="forestgreen")
                    run_status = False
                elif command == "RUN":
                    update_circle_color("yellow")
                    canvas.itemconfig(text_run_status, text="PROCESS..")
                    canvas.itemconfig(text_lid_status, text="LID : CLOSED")
                    lid_status = False
                    run_status = True
                elif command == "Red":
                    update_circle_color("red")
                    canvas.itemconfig(text_run_status, text="Process")
                elif command == "Green":
                    update_circle_color("lime")
                    canvas.itemconfig(text_run_status, text="Finish")
                else:
                    display_serial_text(f"Unknown command: {command}")

def display_serial_text(text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text_box.config(state=tk.NORMAL)
    text_box.insert(tk.END, f"{timestamp} - {text}\n")
    text_box.yview(tk.END)  # Scroll to the end of the text box
    text_box.config(state=tk.DISABLED)

# Update the circle color based on serial data
def update_circle_color(color):
    canvas.itemconfig(circle, fill=color)

def tio_tok_color():
    global blink_count
    if blink_count <= 6:  # 6 steps for 3 rounds of blinking (red -> white -> red -> white -> red -> white)
        new_color = "red" if blink_count % 2 == 0 else "brown"
        canvas.itemconfig(circle, fill=new_color)
        root.after(100, tio_tok_color)  # Call this function again after 100ms
        blink_count += 1
    else:
        blink_count = 0

blink_count = 0

def button_click_run():
    global lid_status, run_status
    if not lid_status:
        if run_status:
            send_command("PC : STOP")
            display_serial_text("PC : STOP")
            left_button.config(text="START PROCESS", background="forestgreen")
            run_status = False
        else:
            send_command("PC : RUN")
            display_serial_text("PC : RUN")
            left_button.config(text="END PROCESS", background="gray24")
    else:
        tio_tok_color()
        display_serial_text("PC : Can't run! Please close the lid.")
        left_button.config(text="START PROCESS", background="forestgreen")
        run_status = False

def button_click_open():
    if run_status:
        send_command("PC : OPEN")
        display_serial_text("PC : STOP")
        left_button.config(text="START PROCESS", background="forestgreen")
    else:
        send_command("PC : OPEN")
        display_serial_text("PC : OPEN")

def list_com_ports():
    datacom = []
    ports = serial.tools.list_ports.comports()
    for port in ports:
        datacom.append(port.device)
    return datacom

datacom = list_com_ports()

run_status = False
lid_status = True

# Create the main window
root = tk.Tk()
root.title("Control Centrifuge")
root.geometry("800x450")  # Update the window size as needed
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Create a Canvas widget
canvas = tk.Canvas(root, width=800, height=125)
canvas.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

# Draw a circle
circle = canvas.create_oval(100, 50, 150, 100, fill="white")
text_run_status = canvas.create_text(170, 60, text="WAIT", font=("Arial", 14), anchor="w")
text_lid_status = canvas.create_text(170, 85, text="LID : -", font=("Arial", 14), anchor="w")

# Create and place the left button
left_button = tk.Button(root, text="START PROCESS", font=("Arial", 16), background="forestgreen", fg="white", command=button_click_run)
left_button.grid(row=1, column=0, sticky="ew", padx=10, pady=10, ipady=10)

# Create and place the right button
right_button = tk.Button(root, text="OPEN LID", font=("Arial", 16), background="firebrick", fg="white", command=button_click_open)
right_button.grid(row=1, column=1, sticky="ew", padx=10, pady=10, ipady=10)

# Create a Text widget for serial output
text_box = tk.Text(root, width=100, height=10, state=tk.DISABLED)
text_box.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Create a list of options for the dropdown menu
options = datacom

# Create a StringVar to hold the selected option
selected_option = tk.StringVar(value="COM Port")

# Create the Combobox
combobox = ttk.Combobox(root, textvariable=selected_option, values=options, state='readonly')
combobox.grid(row=3, column=0, padx=0, pady=5)

# Function to display the selected option
def show_selection(event):
    print("Selected:", selected_option.get())
    init_serial(port=selected_option.get())
    start_serial_thread()

combobox.bind("<<ComboboxSelected>>", show_selection)

def start_serial_thread():
    # Start the serial read thread
    thread = threading.Thread(target=read_from_arduino, daemon=True)
    thread.start()
    send_command("PC : STATUS")
    display_serial_text("PC : STATUS")

# Run the Tkinter event loop
root.mainloop()
