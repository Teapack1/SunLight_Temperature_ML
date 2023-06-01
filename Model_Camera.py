import tensorflow as tf
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
from tensorflow.keras.models import Sequential
import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split

# Load data
def load_data(image_dir, annotation_file):
    images = []
    labels = {}

    with open(annotation_file, 'r') as f:
        for line in f:
            img_num, cct = line.strip().split(', ')
            labels[int(img_num)] = float(cct)

    for filename in os.listdir(image_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            img_num = (filename.split('.')[0])
            img_num = int(img_num.split('_')[1])
            img_path = os.path.join(image_dir, filename)
            img = cv2.imread(img_path)
            img = cv2.resize(img, (224, 224))
            images.append((img, labels[img_num]))

    images, ccts = zip(*images)
    images = np.array(images, dtype=np.float32) / 255.0
    ccts = np.array(ccts, dtype=np.float32)

    return images, ccts

# Define model
def create_model():
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(256, activation='relu'),
        Dropout(0.5),
        Dense(128, activation='relu'),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])

    return model

# Load dataset
image_dir = "photos_512x512"
annotation_file = "photos_512x512/image_control_values.txt"
images, ccts = load_data(image_dir, annotation_file)

# Split data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(images, ccts, test_size=0.2, random_state=42)

# Create and train the model
model = create_model()
model.fit(x_train, y_train, batch_size=32, epochs=10, validation_data=(x_test, y_test))

# Save the model
model.save("cct_recognition_model.h5")
