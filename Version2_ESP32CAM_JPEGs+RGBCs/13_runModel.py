from keras.models import load_model
from PIL import Image
import numpy as np
from joblib import load
import pickle

IMG_HEIGHT = 128
IMG_WIDTH = 128
IMG_CHANNELS = 3

# Load the trained model
model = load_model('model.h5')

# Load the normalizer
with open('rgbw_normalizer.pkl', 'rb') as f:
    rgbw_normalizer = pickle.load(f)

def predict_control_value(rgbw, img_path):
    # Normalize RGBW values with the same normalizer you used in training phase
    rgbw = np.array(rgbw).reshape(1, -1)
    rgbw = rgbw_normalizer.transform(rgbw)

    # Open, resize and normalize the image
    img = Image.open(img_path).resize((IMG_WIDTH, IMG_HEIGHT))
    img = np.array(img) / 255.0  # Normalize to [0,1]
    img = img.reshape((1, IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS))

    # Predict the control value
    control_value = model.predict([img, rgbw])

    return control_value[0][0]


# Example usage:
rgbw_value = [1029, 910, 637, 2560]  # Replace with your RGBW value
img_path = 'TW_STMPLES/photos/80.png'  # Replace with your image path
control_value = predict_control_value(rgbw_value, img_path)

print('Predicted control value:', control_value)
