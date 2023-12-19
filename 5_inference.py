import asyncio
import websockets
import cv2
import numpy as np
import os
import base64
import joblib
from keras.models import load_model
import time

MODEL = os.join('MODEL', 'model_020.keras')
SCALER = os.join('MODEL', 'dataset20_scaler.pkl')
CAPTURE_INTERVAL = 2 #s

scaler = joblib.load(SCALER)
model = load_model(MODEL)

async def run_prediction(websocket):
    
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

            rgbw_scaled = scaler.transform(rgbw_values)
            rgbw_values_received = True
            
    predicted_control_value = model.predict(rgbw_scaled)
    await websocket.send(f"control_value:{predicted_control_value:.3f}")
    print("Control value sent")

    print(
        f"Capturing frame with color values: {rgbw_values}, cct: {cct}, lux: {lux}, predicted control value: {predicted_control_value:.3f}")

    time.sleep(CAPTURE_INTERVAL)    # Prediction pause
    
async def main():
    async with websockets.serve(run_prediction, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())