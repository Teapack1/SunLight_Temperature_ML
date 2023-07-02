import pandas as pd
import numpy as np
import cv2
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Flatten, concatenate, Conv2D, MaxPooling2D
import joblib

# Load the RGBW and target values
data = pd.read_csv('color_dataset.txt', header=None)
rgbw_values = data.iloc[:, 2:6].values
target_values = data.iloc[:, 1].values

# Normalize the RGBW values
scaler = MinMaxScaler()
rgbw_values = scaler.fit_transform(rgbw_values)

# Load the images
image_dir = 'photos'
image_files = sorted(os.listdir(image_dir), key=lambda x: int(x.split('.')[0]))  # sort the files by the sample number
images = []
for image_file in image_files:
    image = load_img(os.path.join(image_dir, image_file), target_size=(240, 240))
    image = img_to_array(image)
    images.append(image)

# Convert the list of images to a numpy array and normalize pixel values
images = np.array(images) / 255.0

# Split the data into a training set and a test set
rgbw_train, rgbw_test, images_train, images_test, target_train, target_test = train_test_split(rgbw_values, images, target_values, test_size=0.2, random_state=42)

# Define the model
input_A = Input(shape=[4], name="rgbw_input")
input_B = Input(shape=[240, 240, 3], name="image_input")
hidden1 = Conv2D(32, (3, 3), activation='relu')(input_B)
hidden2 = MaxPooling2D((2, 2))(hidden1)
hidden3 = Flatten()(hidden2)
concat = concatenate([input_A, hidden3])
output = Dense(1)(concat)
model = Model(inputs=[input_A, input_B], outputs=[output])

# Compile the model
model.compile(loss="mse", optimizer='adam')

# Train the model
model.fit([rgbw_train, images_train], target_train, epochs=10, validation_data=([rgbw_test, images_test], target_test))

# Save the model for future use
model.save('model.h5')

# Save the scaler for future use
scaler_filename = "scaler.save"
joblib.dump(scaler, scaler_filename)
