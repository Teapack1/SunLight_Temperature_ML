import asyncio
import websockets
import cv2
import numpy as np
import os
import base64

CAPTURE_INTERVAL = 0.1
IMAGE_COUNT = 32
IMAGE_WIDTH = 240
IMAGE_HEIGHT = 240
IMAGE_FOLDER = "photos"
DATA_FILE_NAME = "color_dataset.txt"

# Create the photos folder if it doesn't exist
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# Create the text file
with open(DATA_FILE_NAME, 'w') as f:
    f.write("")

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

async def hello(websocket, path):
    for i in range(1, IMAGE_COUNT):
        control_value = next(control_value_generator)
        await websocket.send(f"control_value:{control_value:.3f}")

        # Wait for the specified capture interval
        await asyncio.sleep(CAPTURE_INTERVAL)

        while True:
            message = await websocket.recv()

            message_type, data = message.split(':', 1)
            print(message_type)
            print(data)

            if message_type == 'image':
                decoded_data = base64.b64decode(data)
                nparr = np.frombuffer(decoded_data, np.uint8)
                img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                cv2.imshow('Received Image', img_np)
                cv2.waitKey(1)

                # Save the image to the photos folder
                img_filename = os.path.join(IMAGE_FOLDER, f"{i}.png")
                cv2.imwrite(img_filename, img_np)

            elif message_type == "rgbw_values":
                rgbw_values = data.strip().split(',')
                if len(rgbw_values) != 4:
                    print("Invalid data received. Skipping capture.")
                    continue

                R, G, B, W = map(int, rgbw_values)

                # Print the current capture number and control value in the terminal
                print(f"Capturing frame {i}, control value: {control_value:.3f}, color values: {rgbw_values}")

                # Store the control value and sensor readings in the list
                control_values.append((i, control_value, R, G, B, W))

                # Check if the 'x' key is pressed to interrupt the program
                key = cv2.waitKey(1)
                if key == ord('x'):
                    break

                # Save the control values and sensor readings to the text file
                with open(DATA_FILE_NAME, "w") as text_file:
                    for i, control_value, R, G, B, W in control_values:
                        text_file.write(f"{i}, {control_value}, {R}, {G}, {B}, {W}\n")

                break

async def main():
    async with websockets.serve(hello, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
