# data.py

flights = {
    "6E204": {
        "airline": "IndiGo",
        "origin": "BOM",
        "destination": "DEL",
        "date": "2026-09-20",
        "depart_time": "06:45",
        "base_fare": 7600,
        "taxes": 1300
    },

    "AI803": {
        "airline": "Air India",
        "origin": "BOM",
        "destination": "DEL",
        "date": "2026-09-20",
        "depart_time": "07:30",
        "base_fare": 8200,
        "taxes": 1450
    },

    "UK955": {
        "airline": "Vistara",
        "origin": "BOM",
        "destination": "DEL",
        "date": "2026-09-20",
        "depart_time": "09:10",
        "base_fare": 6900,
        "taxes": 1250
    },

    "SG412": {
        "airline": "SpiceJet",
        "origin": "BOM",
        "destination": "DEL",
        "date": "2026-09-20",
        "depart_time": "14:20",
        "base_fare": 5400,
        "taxes": 1100
    },

    "6E890": {
        "airline": "IndiGo",
        "origin": "BOM",
        "destination": "DEL",
        "date": "2026-09-25",
        "depart_time": "08:00",
        "base_fare": 6200,
        "taxes": 1150
    }
}


blackout_dates = [
    "2026-09-25",
    "2026-09-26"
]


travelers = {
    "EMP001": {
        "name": "Rahul Verma",
        "grade": "L2",
        "previous_bookings": 3,
        "flagged": False
    },

    "EMP002": {
        "name": "Ananya Iyer",
        "grade": "L4",
        "previous_bookings": 0,
        "flagged": False
    },

    "EMP003": {
        "name": "Sameer Khan",
        "grade": "L2",
        "previous_bookings": 12,
        "flagged": True
    }
}
