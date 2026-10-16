# data.py

expense_reports = {
    "EXP001": {
        "employee_id": "EMP001",
        "category": "travel",
        "description": "Flight for client onsite visit",
        "days_since_expense": 12,
        "amount": 8000,
        "has_receipt": True
    },

    "EXP002": {
        "employee_id": "EMP002",
        "category": "meals",
        "description": "Team dinner",
        "days_since_expense": 45,
        "amount": 3500,
        "has_receipt": True
    },

    "EXP003": {
        "employee_id": "EMP003",
        "category": "client_entertainment",
        "description": "Client hospitality event",
        "days_since_expense": 5,
        "amount": 12000,
        "has_receipt": True
    },

    "EXP004": {
        "employee_id": "EMP004",
        "category": "office_supplies",
        "description": "Monitor and keyboard",
        "days_since_expense": 60,
        "amount": 4500,
        "has_receipt": False
    },

    "EXP005": {
        "employee_id": "EMP002",
        "category": "travel",
        "description": "Flight and hotel for regional conference",
        "days_since_expense": 10,
        "amount": 25000,
        "has_receipt": True
    }
}


employee_history = {
    "EMP001": {
        "previous_claims": 3,
        "flagged": False
    },

    "EMP002": {
        "previous_claims": 1,
        "flagged": False
    },

    "EMP003": {
        "previous_claims": 11,
        "flagged": True
    },

    "EMP004": {
        "previous_claims": 0,
        "flagged": False
    }
}
