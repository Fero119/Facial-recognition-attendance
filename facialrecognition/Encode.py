import os
from fileinput import filename

import cv2
import face_recognition
import pickle
from cv2 import COLOR_BGR2RGB
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-recog-4a40c-default-rtdb.firebaseio.com/",
    'storageBucket' : "face-recog-4a40c.appspot.com"
})

# Importing Passenger images
folderPath = 'faces'
PathList = os.listdir(folderPath)
print(PathList)
imgList = []
PassengerIds = []
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    PassengerIds.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(PassengerIds)

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img,COLOR_BGR2RGB)
        encode= face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

print('Encoding started....')
encodeListKnown = findEncodings(imgList)
encodeListKnownwithIds = [encodeListKnown,PassengerIds]
print('Encoding complete')

file = open("EncodeFile.p",'wb')
pickle.dump(encodeListKnownwithIds,file)
file.close()
print('file saved')