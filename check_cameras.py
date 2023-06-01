import cv2

def check_camera(index):
    cap = cv2.VideoCapture(index)
    if cap.isOpened():
        cap.release()
        return True
    return False

max_cameras = 10
available_cameras = []

for i in range(max_cameras):
    if check_camera(i):
        available_cameras.append(i)

print("Available cameras:", available_cameras)

