from flask import Flask, request, jsonify
import cv2
import os
import numpy as np


app = Flask(__name__)

# Constants:
SAMPLES_COUNT = 1
TOTAL_SAMPLES_COUNT = 10
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

control_value_generator = control_value_generator()

@app.route('/post', methods=['POST'])
def post():
    print("client accessed")
    global SAMPLES_COUNT
    current_control_value = next(control_value_generator)
    # Get the image data
    image_data = request.get_data()

    # Convert the image to a numpy array and then to a OpenCV format
    npimg = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # Save the image
    image_path = os.path.join(IMAGE_FOLDER, f"img_{SAMPLES_COUNT}.png")
    cv2.imwrite(image_path, img)

    # Display the image
    cv2.imshow('image', img)


    # Get the RGB data
    r = request.args.get('r')
    g = request.args.get('g')
    b = request.args.get('b')
    c = request.args.get('c')

    print(f"Sample: {SAMPLES_COUNT}/{TOTAL_SAMPLES_COUNT}, Control value: {current_control_value}, Received RGB data: r={r}, g={g}, b={b}, c={c}")

    # Save the data to the file
    with open(DATASET_FILE_NAME, 'a') as f:
        f.write(f"{SAMPLES_COUNT}, {current_control_value}, {r}, {g}, {b}\n")

    SAMPLES_COUNT += 1
    cv2.destroyAllWindows()

    if SAMPLES_COUNT >= TOTAL_SAMPLES_COUNT:
        return jsonify({"control_value": current_control_value, "status": "DONE"})

    return jsonify({"control_value": current_control_value, "status": "CONTINUE"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
