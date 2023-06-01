import cv2
import numpy as np
from tensorflow.keras.models import load_model
import serial

# Serial port settings
SERIAL_PORT = "COM4"  # Replace this with the correct serial port on your development PC
BAUD_RATE = 9600

IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512
CAMERA_INDEX = 1

# Set up the serial connection
#ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
def send_control_value(value):
    #ser.write(f"{value:.2f}\n".encode())
    pass

# Load the saved model
saved_model = load_model("cct_recognition_model.h5")

# Initialize the webcam
cap = cv2.VideoCapture(CAMERA_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMAGE_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMAGE_HEIGHT)
cap.set(cv2.CAP_PROP_AUTO_WB, 0.0)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.0)


while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        print("Error capturing frame.")
        break

    # Resize and preprocess the frame
    input_frame = cv2.resize(frame, (224, 224))
    input_image = np.array(input_frame, dtype=np.float32) / 255.0
    input_image = np.expand_dims(input_image, axis=0)

    # Make a prediction
    cct_prediction = saved_model.predict(input_image)[0][0]

    # Control value send it to the microcontroller
    control_value = cct_prediction
    send_control_value(control_value)

    # Display the predicted CCT on the frame
    cv2.putText(frame, f"CCT: {cct_prediction:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show the frame with the prediction
    cv2.imshow("Real-time CCT Prediction", frame)

    # Exit the loop when the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the window
cap.release()
cv2.destroyAllWindows()
