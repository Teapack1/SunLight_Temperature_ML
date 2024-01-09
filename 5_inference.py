import asyncio
import websockets
import numpy as np
import os
import joblib
from keras.models import load_model
import time

MODEL = os.join("MODEL", "model_020.keras")
SCALER = os.join("MODEL", "dataset20_scaler.pkl")
CAPTURE_INTERVAL = 2  # s

scaler = joblib.load(SCALER)
model = load_model(MODEL)


async def run_prediction(websocket):
    await websocket.send(f"control_value:{0.0}")

    while True:
        rgbw_values_received = False
        while not rgbw_values_received:
            message = await websocket.recv()
            message_type, data = message.split(":", 1)

            if message_type == "rgbw_values":
                print("Received RGBW values")

                rgbw_values = data.strip().split(",")
                if len(rgbw_values) != 4:
                    print("Invalid data received. Skipping capture.")
                    continue

                try:
                    rgbw_array = np.array(rgbw_values, dtype=float).reshape(1, -1)
                    rgbw_scaled = scaler.transform(rgbw_array)
                    rgbw_values_received = True
                    input_data = np.array(rgbw_scaled, dtype=np.float32)

                    predicted_control_value = model.predict(input_data)
                    control_value = predicted_control_value.item()
                    await websocket.send(f"control_value:{control_value:.3f}")
                except Exception as e:
                    print(f"Error processing the value: {e}")

                time.sleep(CAPTURE_INTERVAL)  # Prediction pause


async def main():
    async with websockets.serve(run_prediction, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
