import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Load the model
model = tf.keras.models.load_model('nonlinear_regression_model.h5')

# Initialize the scaler
scaler = MinMaxScaler()

# Take input from the user
R = float(input("Enter R value: "))
G = float(input("Enter G value: "))
B = float(input("Enter B value: "))
#W = float(input("Enter W value: "))

# Create a numpy array from the user's input
input_data = np.array([[R, G, B]])

# Normalize the input data like the training data
input_data = scaler.fit_transform(input_data)

# Make a prediction
prediction = model.predict(input_data)

# Print the prediction
print("Predicted control value: ", prediction[0][0])
