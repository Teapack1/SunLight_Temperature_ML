import asyncio
import websockets
import cv2
import numpy as np
import os
import base64
import random


CAPTURE_INTERVAL = 0.3
total_samples = 3000  # Total number of samples
set_samples = 1000  # Number of samples in each set
IMAGE_WIDTH = 240
IMAGE_HEIGHT = 240
IMAGE_FOLDER = "photos"
DATA_FILE_NAME = "color_dataset.txt"
global i_gl
i_gl = 1

# Create the photos folder if it doesn't exist
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# Create the text file if it doesn't exist
if not os.path.exists(DATA_FILE_NAME):
    with open(DATA_FILE_NAME, "w") as text_file:
        text_file.write("")

# Initialize an empty list to store control values
control_values = []

def control_value_generator():
    value = 0.0
    while True:
        yield value
        value += 0.001
        if value > 1.0:
            value = 0.0

# def control_value_generator():
#     value = 0.0
#     while True:
#         yield value
#         value = random.uniform(0.0, 1.0)

control_value_generator = control_value_generator()

async def hello(websocket):
    global i_gl
    for i in range(i_gl, total_samples + 1):
        i_gl = i
        print(i_gl)
        control_value = next(control_value_generator)
        await websocket.send(f"control_value:{control_value:.3f}")


        image_received = False
        light_specs_received = False
        rgbw_values_received = False

        while not (image_received and light_specs_received and rgbw_values_received):
            message = await websocket.recv()
            message_type, data = message.split(':', 1)

            if message_type == 'image':
                print("Received image")

                decoded_data = base64.b64decode(data)
                nparr = np.frombuffer(decoded_data, np.uint8)
                img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                cv2.imshow('Received Image', img_np)
                cv2.waitKey(1)

                # Save the image to the photos folder
                img_filename = os.path.join(IMAGE_FOLDER, f"{i}.png")
                cv2.imwrite(img_filename, img_np)

                image_received = True

            elif message_type == "light_specs":
                print("Received light specs")

                try:
                    cct, lux = data.strip().split(',')
                    light_specs_received = True
                except ValueError:
                    print("Invalid data received. Skipping capture.")
                    continue

            elif message_type == "rgbw_values":
                print("Received RGBW values")

                rgbw_values = data.strip().split(',')
                if len(rgbw_values) != 4:
                    print("Invalid data received. Skipping capture.")
                    continue

                R, G, B, W = map(int, rgbw_values)

                # Store the control value and sensor readings in the list
                control_values.append((i, round(control_value, 3), R, G, B, W))

                rgbw_values_received = True

        # Check if the 'x' key is pressed to interrupt the program
        key = cv2.waitKey(1)
        if key == ord('x'):
            break

        # Save the control values and sensor readings to the text file
        with open(DATA_FILE_NAME, "w") as text_file:
            for i, control_value, R, G, B, W in control_values:
                text_file.write(f"{i}, {control_value}, {R}, {G}, {B}, {W}\n")

        # Print the current capture number and control value in the terminal
        print(
            f"Capturing frame {i}/{set_samples} ({total_samples}), control value: {control_value:.3f}, color values: {rgbw_values}, cct: {cct}, lux: {lux}")

        # After each set of samples, pause and wait for a key press to continue
        if i % set_samples == 0:
            print(f"Finished set of {set_samples} samples.")
            print("Type 'n' and press Enter to start the next set, or any other key to exit.")

            # Wait for the user to press 'n' to start the next set
            user_input = input()
            if user_input.lower() != 'n':
                break


async def main():
    async with websockets.serve(hello, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
