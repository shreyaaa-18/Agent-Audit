# data.py

loan_applications = {
    "LOAN001": {
        "applicant_id": "APPL001",
        "loan_type": "personal",
        "purpose": "medical_expenses",
        "credit_score": 720,
        "amount": 200000
    },

    "LOAN002": {
        "applicant_id": "APPL002",
        "loan_type": "personal",
        "purpose": "debt_consolidation",
        "credit_score": 680,
        "amount": 1500000
    },

    "LOAN003": {
        "applicant_id": "APPL003",
        "loan_type": "personal",
        "purpose": "medical_expenses",
        "credit_score": 690,
        "amount": 300000
    },

    "LOAN004": {
        "applicant_id": "APPL004",
        "loan_type": "personal",
        "purpose": "education",
        "credit_score": 610,
        "amount": 150000
    }
}


applicant_history = {
    "APPL001": {
        "previous_loans": 1,
        "suspicious": False
    },

    "APPL002": {
        "previous_loans": 0,
        "suspicious": False
    },

    "APPL003": {
        "previous_loans": 8,
        "suspicious": True
    },

    "APPL004": {
        "previous_loans": 0,
        "suspicious": False
    }
}
