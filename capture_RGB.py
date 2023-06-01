import os
import time
import random
import serial
import keyboard

# Sensor and data settings
CAPTURE_INTERVAL = 0
CAPTURE_COUNT = 3000
DATA_FILE_NAME = "color_dataset.txt"

# Serial port settings
SERIAL_PORT = "COM4"  # Replace this with the correct serial port on your development PC
BAUD_RATE = 9600

# Set up the serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

def send_control_value(value):
    ser.write(f"{value:.3f}\n".encode())

# Initialize an empty list to store control values
control_values = []

# def control_value_generator():
#     value = 0.0
#     while True:
#         yield value
#         value += 0.001
#         if value > 1.0:
#             value = 0.0


#control_value_generator = control_value_generator()

try:
    for i in range(1, CAPTURE_COUNT):
        # Get the next control value and send it to the microcontroller
        control_value = random.uniform(0.0, 1.0)
        #control_value = next(control_value_generator)
        send_control_value(control_value)

        ser.write("3".encode())

        # Wait for the specified capture interval
        time.sleep(CAPTURE_INTERVAL)

        # Read the RGBW values from the serial port
        rgbw_values = ser.readline().decode().strip().split(',')
        if len(rgbw_values) != 4:
            print("Invalid data received. Skipping capture.")
            continue

        R, G, B, W = map(int, rgbw_values)


        # Print the current capture number and control value in the terminal
        print(f"Capturing frame {i}, control value: {control_value:.3f}, color values: {rgbw_values}")

        # Store the control value and sensor readings in the list
        control_values.append((i, control_value, R, G, B, W))

        # Check if the 'q' key is pressed to interrupt the program
        if keyboard.is_pressed('q'):  # Update this line
            break

        # Ask for user input to continue after 1000 captures
        if i % 1000 == 0:
            print("Press 'n' to continue with the next 1000 captures or any other key to stop.")
            user_input = input()
            if user_input.lower() != 'n':
                break

finally:
    # Close the serial connection
    ser.close()

# Save the control values and sensor readings to the text file
with open(DATA_FILE_NAME, "w") as text_file:
    for i, control_value, R, G, B, W in control_values:
        text_file.write(f"{i}, {control_value:.3f}, {R}, {G}, {B}, {W}\n")
