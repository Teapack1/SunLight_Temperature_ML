import cv2
import os
import time
import random
import serial

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
    ser.write(f"{value:.2f}\n".encode())

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

# Create a window to display the webcam feed
cv2.namedWindow("Webcam Feed", cv2.WINDOW_NORMAL)

try:
    for i in range(IMAGE_COUNT):
        # Generate a random control value and send it to the microcontroller
        control_value = random.uniform(0, 1)
        send_control_value(control_value)
        
        # Wait for the specified capture interval
        time.sleep(CAPTURE_INTERVAL)

        # Capture an image from the webcam
        ret, frame = cap.read()

        # Display the webcam feed in the window
        cv2.imshow("Webcam Feed", frame)

        # Save the image to the photos folder
        img_filename = os.path.join(IMAGE_FOLDER, IMAGE_FILE_FORMAT.format(i))
        cv2.imwrite(img_filename, frame)

        # Print the current image number in the terminal
        print(f"Capturing image {i}")

        # Store the control value in the list
        control_values.append((i, control_value))

        # Check if the 'x' key is pressed to interrupt the program
        key = cv2.waitKey(1)
        if key == ord('x'):
            break

finally:
    # Release the webcam, close the window, and close the serial connection
    cap.release()
    cv2.destroyAllWindows()
    ser.close()

# Save the control values to the text file
with open(TEXT_FILE_NAME, "w") as text_file:
    for i, control_value in control_values:
        text_file.write(f"{i}, {control_value:.2f}\n")
