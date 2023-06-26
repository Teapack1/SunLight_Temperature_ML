from flask import Flask, request
from flask_socketio import SocketIO, send, emit
import cv2
import os
import numpy as np
from PIL import Image

app = Flask(__name__)
socketio = SocketIO(app)

# Constants:
SAMPLES_COUNT = 10
CAPTURE_INTERVAL = 0.5
IMAGE_WIDTH = 240
IMAGE_HEIGHT = 240
IMAGE_FOLDER = "photos"
DATASET_FILE_NAME = "color_dataset.txt"

# Image folder:
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# Control value generator:
def control_value_generator():
    value = 0.0
    while True:
        yield value
        value += 0.001
        if value > 1.0:
            value = 0.0

@socketio.on('message')
def handle_message(data):
    global SAMPLES_COUNT

    # Convert the image to a numpy array and then to a OpenCV format
    npimg = np.frombuffer(data['image'], np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # Save the image
    image_path = os.path.join(IMAGE_FOLDER, f"img_{SAMPLES_COUNT}.png")
    cv2.imwrite(image_path, img)

    # Display the image
    cv2.imshow('image', img)

    # Get the RGB data
    r = data['r']
    g = data['g']
    b = data['b']
    c = data['c']

    print(f"Received RGB data: r={r}, g={g}, b={b}, c={c}")

    SAMPLES_COUNT += 1

    cv2.destroyAllWindows()  # destroys the window showing image

    # Send control value back to the client
    control_value = next(control_value_generator())
    emit('message', {'control_value': control_value, 'status': 'OK' if SAMPLES_COUNT < 10 else 'DONE'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
