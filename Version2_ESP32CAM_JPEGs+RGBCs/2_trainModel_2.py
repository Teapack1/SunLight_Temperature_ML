import os
import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image
from keras.layers import Dense, Flatten, Input
from keras.models import Model
from keras.optimizers import Adam
from keras.applications import MobileNetV2
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from keras.layers import Dropout
from keras.regularizers import l2
import pickle
import matplotlib.pyplot as plt

# Constants for your dataset
IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS = 128, 128, 3 # replace with your image size and channels
RGBW_DIM = 4 # RGBW

# Load RGBW values and target control values
data_df = pd.read_csv('TW_STMPLES/color_dataset.txt', sep=',', header=None, names=['index', 'control_value', 'R', 'G', 'B', 'W'])

rgbw_values = data_df[['R', 'G', 'B', 'W']].values
target_values = data_df['control_value'].values

# Load images
image_folder = 'TW_STMPLES/photos'
image_files = [os.path.join(image_folder, f'{i}.png') for i in data_df['index']]
images = np.array([np.array(Image.open(f).resize((IMG_HEIGHT, IMG_WIDTH))) for f in image_files])

# Preprocess your data
# Normalize the pixel values to be between -1 and 1
images = (images / 127.5) - 1

# Normalize the RGBW values
scaler = MinMaxScaler()
rgbw_values = scaler.fit_transform(rgbw_values)

# Save the RGBW normalizer for later use
with open('rgbw_normalizer.pkl', 'wb') as f:
    pickle.dump(scaler, f)

# Split data into train and validation sets
images_train, images_val, rgbw_values_train, rgbw_values_val, target_values_train, target_values_val = train_test_split(images, rgbw_values, target_values, test_size=0.2)

# Use a pre-trained MobileNet model for the image data
base_model = MobileNetV2(input_shape=(IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS), include_top=False, weights='imagenet')
base_model.trainable = False # Freeze the weights of the pre-trained model
img_input = Input(shape=(IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS))
img_model = base_model(img_input, training=False)
img_model = Flatten()(img_model)
img_model = Dense(512, activation='relu', kernel_regularizer=l2(0.01))(img_model)  # L2 Regularization
img_model = Dropout(0.3)(img_model)  # Increased Dropout

# Build a Deeper Dense network for the RGBW data
rgbw_input = Input(shape=(RGBW_DIM,))
rgbw_model = Dense(256, activation='relu', kernel_regularizer=l2(0.01))(rgbw_input)  # Increased to 256 units
rgbw_model = Dropout(0.3)(rgbw_model)  # Increased Dropout
rgbw_model = Dense(128, activation='relu', kernel_regularizer=l2(0.01))(rgbw_model)  # Increased to 128 units
rgbw_model = Dropout(0.3)(rgbw_model)  # Increased Dropout
rgbw_model = Dense(64, activation='relu', kernel_regularizer=l2(0.01))(rgbw_model)   # Kept at 64 units

# Merge the two networks
merged = tf.keras.layers.concatenate([img_model, rgbw_model])

# Add a Dense output layer to predict the target value
output = Dense(1, activation='sigmoid')(merged)

# Build and compile the model
model = Model(inputs=[img_input, rgbw_input], outputs=[output])
model.compile(optimizer=Adam(), loss='mean_squared_error')

# Train the model on your data
history = model.fit([images, rgbw_values], target_values, batch_size=32, epochs=12, validation_split=0.2)


plt.figure(figsize=(10, 5))
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend(['Train', 'Validation'], loc='upper right')
plt.show()

plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')

# Plot training & validation accuracy values
plt.subplot(1, 2, 2)
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')

plt.tight_layout()
plt.show()

# Save the trained model for later use
model.save('model.h5')
