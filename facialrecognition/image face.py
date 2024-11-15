import cv2

# Open the camera
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Error: Unable to open camera")
    exit(1)

# Set the resolution
cap.set(3, 1280)
cap.set(4, 720)

while True:
    success, img = cap.read()
    if not success:
        print("Error: Unable to read from camera")
        break

    # Check if the image is empty
    if img is None or img.empty():
        print("Error: Image is empty")
        break

    cv2.imshow("Face Attendance", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()