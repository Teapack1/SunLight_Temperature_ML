import cv2
import sys

# Section 1: Open the webcam
cap = cv2.VideoCapture("v4l2src device=/dev/video2 ! video/x-raw, width=640, height=480 ! videoconvert ! video/x-raw,format=BGR ! appsink")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 512)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)

cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.0)
cap.set(cv2.CAP_PROP_EXPOSURE, 0.0)
cap.set(cv2.CAP_PROP_AUTO_WB, 0.0)


# Section 2: Check if the webcam opened successfully
if not cap.isOpened():
    print("Error opening camera")

# Section 3: Main loop to capture and display frames
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # If frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # Display the resulting frame
    cv2.imshow('Webcam Feed', frame)

    # Check for 'q' key press to stop the loop
    if cv2.waitKey(1) == ord('q'):
        break

# Section 4: Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
