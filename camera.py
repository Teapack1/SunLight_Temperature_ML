import asyncio
import websockets
import cv2
import numpy as np
import os
import base64
import random
import time

CAPTURE_INTERVAL = 0.3
total_samples = 1000  # Total number of samples
set_samples = 100  # Number of samples in each set
IMAGE_WIDTH = 240
IMAGE_HEIGHT = 240
IMAGE_FOLDER = "test_photos"
DATA_FILE_NAME = "color_dataset.txt"

# Create the photos folder if it doesn't exist
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

def control_value_generator():
    i =0
    while True:
        i %= 1
        i += 0.1
        yield i


# def control_value_generator():
#     while True:
#         start = random.uniform(0, 0.5)
#         for i in np.linspace(start, start + 0.5, 5):
#             yield i


gen = control_value_generator()


async def hello(websocket, path):
    while(True):
        control_value = next(gen)
        await websocket.send(f"control_value:{control_value:.3f}")
        print(control_value)
        image_received = False

        image = 1

        while not (image_received):
            message = await websocket.recv()
            message_type, data = message.split(':', 1)
            image += 1
            if message_type == 'image':
                print("Received image")

                decoded_data = base64.b64decode(data)
                nparr = np.frombuffer(decoded_data, np.uint8)
                img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                cv2.imshow('Received Image', img_np)
                cv2.waitKey(1)

                # Save the image to the photos folder
                img_filename = os.path.join(IMAGE_FOLDER, f"{image}.png")
                cv2.imwrite(img_filename, img_np)

                image_received = True

async def main():
    async with websockets.serve(hello, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
