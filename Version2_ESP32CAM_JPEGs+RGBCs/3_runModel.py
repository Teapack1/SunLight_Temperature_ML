from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import os

# Load the saved model
model = load_model('model.h5')

# Load the saved scaler
scaler = joblib.load('scaler.save')

# Load the RGBW and target values
data = pd.read_csv('color_dataset.txt', header=None)
rgbw_values = data.iloc[:, 2:6].values
target_values = data.iloc[:, 1].values

# Normalize the RGBW values
rgbw_values = scaler.transform(rgbw_values)

# Load the images
image_dir = 'photos'
image_files = sorted(os.listdir(image_dir), key=lambda x: int(x.split('.')[0]))  # sort the files by the sample number
images = []
for image_file in image_files:
    image = load_img(os.path.join(image_dir, image_file), target_size=(240, 240))
    image = img_to_array(image) / 255.0  # normalize pixel values
    images.append(image)

# Convert the list of images to a numpy array
images = np.array(images)

# Predict the control values for the training data
control_values = model.predict([rgbw_values, images])

print(f"Predicted control values: {control_values}")
