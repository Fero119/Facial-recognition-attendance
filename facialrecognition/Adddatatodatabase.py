import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Use the correct path to your serviceAccountKey.json file
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-recog-4a40c-default-rtdb.firebaseio.com/"
})

ref = db.reference('Passengers')

data = {
    "321654": {
        "Surname": "Akingbola",
        "Given-name": "Feranmi.A",
        "Nin": "30000056743",
        "Nationality": "Nigerian",
        "Date-of-birth": "24 Oct 1999",
        "Sex": "M",
        "Place-of-birth": "Akure",
        "Last flight booking": "2023-12-11 00:54:34"
    },
    "741852": {
            "Surname": "Elon",
            "Given-name": "Musk.R",
            "Nin": "31200562109",
            "Nationality": "South Africa",
            "Date-of-birth": "19 Sept 1971",
            "Sex": "M",
            "Place-of-birth": "Pretoria",
            "Last flight booking": "2023-12-11 00:54:34"
    },
    "963852": {
                "Surname": "Jeff",
                "Given-name": "Bezos.P",
                "Nin": "31992287108",
                "Nationality": "United States",
                "Date-of-birth": "12 Jan 1964",
                "Sex": "M",
                "Place-of-birth": "New Mexico",
                "Last flight booking": "2023-12-11 00:54:34"
    }
}

for key,value in data.items():
    ref.child(key).set(value)

