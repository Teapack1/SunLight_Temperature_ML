import pandas as pd
import matplotlib.pyplot as plt
import joblib
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

# Load the data from a file
df = pd.read_csv("color_dataset_TCS34xxx.csv")

# Separate inputs and target
features = df[['R', 'G', 'B', 'W']]
targets = df['control_value']

# Normalize the data
scaler = MinMaxScaler()
features = scaler.fit_transform(features)

# save the scaler object to a file
joblib.dump(scaler, 'scaler_TCS34.pkl')

# Split the data into training and test sets
features_train, features_test, targets_train, targets_test = train_test_split(features, targets, test_size=0.2, random_state=42)
features_train, features_val, targets_train, targets_val = train_test_split(features_train, targets_train, test_size=0.2, random_state=42)

# Define the model architecture
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(4,)),
    tf.keras.layers.Dense(1024, activation='relu'),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dense(1)
])

# Compile the model
model.compile(loss='mean_squared_error', optimizer='adam')

# Train the model
history = model.fit(features_train, targets_train, epochs=15, verbose=1, validation_data=(features_val, targets_val))

loss = model.evaluate(features_test, targets_test)
print("Model's loss on test set: ", loss)


plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper right')
plt.show()

# Save the model
model.save('cct_recognition_model_TCS34xxxx.h5')
