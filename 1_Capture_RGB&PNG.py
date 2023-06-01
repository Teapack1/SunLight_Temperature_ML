import os
import time
import cv2
import random
import serial
import keyboard

# Sensor and data settings
CAPTURE_INTERVAL = 0
CAPTURE_COUNT = 3000
DATA_FILE_NAME = "color_dataset.txt"

# Webcam and image settings
CAPTURE_INTERVAL = 0.5
IMAGE_COUNT = 256
IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512
IMAGE_FOLDER = "photos"
IMAGE_FILE_FORMAT = "img_{}.png"
TEXT_FILE_NAME = "image_control_values.txt"
CAMERA_INDEX = 1

# Serial port settings
SERIAL_PORT = "COM4"  # Replace this with the correct serial port on your development PC
BAUD_RATE = 9600

# Set up the serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

def send_control_value(value):
    ser.write(f"{value:.3f}\n".encode())

# Create the photos folder if it doesn't exist
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# Set up the webcam
cap = cv2.VideoCapture(CAMERA_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT)
cap.set(cv2.CAP_PROP_AUTO_WB, 0.0)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.0)

# Initialize an empty list to store control values
control_values = []

def control_value_generator():
    value = 0.0
    while True:
        yield value
        value += 0.001
        if value > 1.0:
            value = 0.0

control_value_generator = control_value_generator()

# Create a window to display the webcam feed
cv2.namedWindow("Webcam Feed", cv2.WINDOW_NORMAL)

try:
    for i in range(1, CAPTURE_COUNT):
        # Get the next control value and send it to the microcontroller
        #control_value = random.uniform(0.0, 1.0)
        control_value = next(control_value_generator)
        send_control_value(control_value)

        ser.write("3".encode())

        # Wait for the specified capture interval
        time.sleep(CAPTURE_INTERVAL)

        # Capture an image from the webcam
        ret, frame = cap.read()
        # Print the current image number in the terminal
        print(f"Capturing image {i}")
        # Display the webcam feed in the window
        cv2.imshow("Webcam Feed", frame)
        # Save the image to the photos folder
        img_filename = os.path.join(IMAGE_FOLDER, IMAGE_FILE_FORMAT.format(i))
        cv2.imwrite(img_filename, frame)


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

        # Check for 'q' key press to stop the loop !!!!!!!!!!!!!!!!
        if cv2.waitKey(1) == ord('q'):
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
