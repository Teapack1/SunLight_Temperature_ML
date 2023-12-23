import asyncio
import websockets
import cv2
import numpy as np
import os
import base64
import joblib
from keras.models import load_model
import time

MODEL = os.path.join('MODEL', 'color_model.keras')
SCALER = os.path.join('MODEL', 'color_scaler.pkl')
CAPTURE_INTERVAL = 2 #s

scaler = joblib.load(SCALER)
model = load_model(MODEL)

async def run_prediction(websocket):
    await websocket.send(f"control_value:{0.0}")
    
    while True:
        rgbw_values_received = False
        while not rgbw_values_received:
            
            message = await websocket.recv()
            message_type, data = message.split(':', 1)

            if message_type == "rgbw_values":
                print("Received RGBW values")
                rgbw_values = data.strip().split(',')
                if len(rgbw_values) != 4:
                    print("Invalid data received. Skipping capture.")
                    continue

                rgbw_array = np.array(rgbw_values, dtype=float).reshape(1, -1)  # Convert to numpy array and reshape
                rgbw_scaled = scaler.transform(rgbw_array)
                rgbw_values_received = True
                
                predicted_control_value = model.predict(rgbw_scaled)
                await websocket.send(f"control_value:{predicted_control_value[0][0]:.3f}")
                print(f"Control value sent: {predicted_control_value}")

        print(
            f"Capturing frame with color values: {rgbw_values}, predicted control value: {predicted_control_value[0][0]:.3f}")

        time.sleep(CAPTURE_INTERVAL)    # Prediction pause
    
async def main():
    async with websockets.serve(run_prediction, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())