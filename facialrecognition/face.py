import os
import pickle
from datetime import datetime

import cv2
import face_recognition
from cv2 import COLOR_BGR2RGB
import numpy as np
import cvzone
from cv2.version import opencv_version
from Encode import encodeListKnownwithIds, encodeListKnown, PassengerIds
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

# Check if Firebase is already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://face-recog-4a40c-default-rtdb.firebaseio.com/",
        'storageBucket': "face-recog-4a40c.appspot.com"
    })

bucket = storage.bucket()
# Open the webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set width
cap.set(4, 480)  # Set height

# Load the background image
imgBackground = cv2.imread('Background/Background.png')

# Importing the mode images into a list
folderModePath = 'Background/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# Load the encoding file
print('Loading Encode file...')
file = open('EncodeFile.p', 'rb')
encodeListKnownwithIds = pickle.load(file)
file.close()
encodeListKnown, PassengerIds = encodeListKnownwithIds
print('Encode file loaded')

modeType = 0
counter = 0
id = -1
imgPassenger = []
PassengerInfo = {}  # Initialize PassengerInfo dictionary to avoid key errors

# Check if the background image is loaded successfully
if imgBackground is None:
    print("Error: Could not load background image.")
    exit()

# Resize the background image (if needed)
imgBackground = cv2.resize(imgBackground, (700, 500))  # Adjust to your dimensions

# Define the coordinates and size of the left box (webcam feed)
x, y = 34, 115  # Position of the top-left corner of the box
box_w, box_h = 343, 330  # Width and height of the box

# Define the coordinates and size of the right box (for imgModeList[0])
right_x, right_y = 440, 30  # Position of the top-left corner of the right box
right_w, right_h = 230, 440  # Width and height of the right box (adjust accordingly)

while True:
    success, img = cap.read()

    if not success:
        print("Error: Could not read frame.")
        break

    # Resize the webcam feed to match the left box's dimensions
    img_resized = cv2.resize(img, (box_w, box_h))

    # Overlay the webcam feed onto the background image inside the left box
    imgBackground[y:y + box_h, x:x + box_w] = img_resized

    # Resize the image from imgModeList to match the right box's dimensions
    imgModeResized = cv2.resize(imgModeList[modeType], (right_w, right_h))

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, COLOR_BGR2RGB)

    faceCurrentFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurrentFrame)

    if faceCurrentFrame:
        # Corrected loop using zip
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurrentFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                print(PassengerIds[matchIndex])
                id = PassengerIds[matchIndex]

                print(id)
                if counter == 0:
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                PassengerInfo = db.reference(f'Passengers/{id}').get()
                print(PassengerInfo)

                # Get the Image from Storage
                blob = bucket.get_blob(f'faces/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgPassenger = cv2.imdecode(array, cv2.IMREAD_COLOR)  # Use cv2.IMREAD_COLOR to read the image correctly


            if 10<counter<20:
                modeType = 2

            imgModeResized = cv2.resize(imgModeList[modeType], (right_w, right_h))

            if counter<=10:
            # Add the 'Sex' information onto imgModeResized
                if 'Sex' in PassengerInfo:
                    cv2.putText(imgModeResized, f" {PassengerInfo['Sex']}", (15, 55),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.putText(imgModeResized, f" {PassengerInfo['Nin']}", (64, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                    cv2.putText(imgModeResized, f" {PassengerInfo['Date-of-birth']}", (80, 278),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                    cv2.putText(imgModeResized, f" {PassengerInfo['Surname']}", (105, 313),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                    cv2.putText(imgModeResized, f" {PassengerInfo['Given-name']}", (115, 352),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                    cv2.putText(imgModeResized, f" {PassengerInfo['Nationality']}", (112, 393),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

                    # Calculate aspect ratio of imgPassenger to resize proportionally
                    aspect_ratio = imgPassenger.shape[1] / imgPassenger.shape[0]
                    new_width = right_w
                    new_height = int(new_width / aspect_ratio)

                    # If new height exceeds right box height, adjust height and width accordingly
                    if new_height > int(right_h / 3):
                        new_height = int(right_h / 3)
                        new_width = int(new_height * aspect_ratio)

                    # Resize imgPassenger proportionally
                    imgPassenger_resized = cv2.resize(imgPassenger, (new_width, new_height))

                    # Determine the position to overlay imgPassenger onto imgModeResized
                    passenger_y, passenger_x = 92, 62 # Adjust as needed

                    # Overlay the imgPassenger onto imgModeResized
                    imgModeResized[passenger_y:passenger_y + imgPassenger_resized.shape[0],
                                   passenger_x:passenger_x + imgPassenger_resized.shape[1]] = imgPassenger_resized

            counter += 1

            if counter>=20:
                modeType = 0
                counter= 0
                PassengerInfo = []
                imgPassenger = []

                imgModeResized = cv2.resize(imgModeList[modeType], (right_w, right_h))

    else:
        modeType = 0
        counter = 0
    # Overlay the imgModeResized image (with text) onto the background image inside the right box
    imgBackground[right_y:right_y + right_h, right_x:right_x + right_w] = imgModeResized

    # Display the final image with the webcam overlay and the mode image
    cv2.imshow("Face Attendance", imgBackground)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
