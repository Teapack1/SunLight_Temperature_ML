from tensorflow.keras.models import load_model
import serial
import keyboard
import numpy as np
import joblib

SERIAL_PORT = "COM5"  # Replace this with the correct serial port on your development PC
BAUD_RATE = 9600
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

def send_control_value(value):
    ser.write(f"{value:.3f}\n".encode())

# Load the model
model = load_model('cct_recognition_model_TCS34xxxx.h5')

# load the scaler object from the file (learning scaler)
scaler = joblib.load('scaler.pkl')

while True:
    # Read the RGBW values from the serial port
    rgbw_values = ser.readline().decode().strip().split(',')
    if len(rgbw_values) != 4:
        print("Invalid data received. Skipping capture.")
        continue

    R, G, B, W = map(int, rgbw_values)

    # Normalize the input data like the training data
    inputs = scaler.transform(np.array([[R, G, B, W]]))

    # Make a prediction
    prediction = model.predict(inputs)
    send_control_value(prediction)

    # Print the prediction
    print("Predicted control value: ", prediction[0][0])

    # Check if the 'q' key is pressed to interrupt the program
    if keyboard.is_pressed('q'):
        break
