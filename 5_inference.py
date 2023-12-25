import asyncio
import websockets
import cv2
import numpy as np
import os
import base64
import joblib
import tflite_runtime.interpreter as tflite
import time

MODEL = os.path.join('MODEL', 'color_model.tflite')
SCALER = os.path.join('MODEL', 'color_scaler.pkl')
CAPTURE_INTERVAL = 2 #s

scaler = joblib.load(SCALER)
interpreter = tflite.Interpreter(model_path=MODEL)
interpreter.allocate_tensors()

# Get input and output tensors
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

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
                
                try:
                    rgbw_array = np.array(rgbw_values, dtype=float).reshape(1, -1)  # Convert to numpy array and reshape
                    rgbw_scaled = scaler.transform(rgbw_array)
                    rgbw_values_received = True
                    print("here1")
                    input_data = np.array(rgbw_scaled, dtype=np.float32)        
                    interpreter.set_tensor(input_details[0]['index'], input_data)
                    print("here2")
                    interpreter.invoke()
                    print("here3")
                    predicted_control_value = interpreter.get_tensor(output_details[0]['index'])
                    print("Control value sent")
                    print(f"Capturing frame with color values: {rgbw_values}, predicted control value: {predicted_control_value}")
        
                    control_value = predicted_control_value.item()
                    await websocket.send(f"control_value:{control_value:.3f}")
                except Exception as e:
                    print(f"Error processing the value: {e}")
                
                time.sleep(CAPTURE_INTERVAL)    # Prediction pause
    
async def main():
    async with websockets.serve(run_prediction, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())