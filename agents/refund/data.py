# data.py

orders = {
    "ORD001": {
        "customer_id": "CUST001",
        "product": "Headphones",
        "reason": "damaged",
        "days_since_purchase": 10,
        "value": 2000
    },

    "ORD002": {
        "customer_id": "CUST002",
        "product": "Laptop",
        "reason": "changed_mind",
        "days_since_purchase": 10,
        "value": 75000
    },

    "ORD003": {
        "customer_id": "CUST003",
        "product": "Mobile Phone",
        "reason": "damaged",
        "days_since_purchase": 5,
        "value": 30000
    },

    "ORD004": {
        "customer_id": "CUST004",
        "product": "Headphones",
        "reason": "damaged",
        "days_since_purchase": 45,
        "value": 2000
    }
}


customer_history = {
    "CUST001": {
        "previous_refunds": 1,
        "suspicious": False
    },

    "CUST002": {
        "previous_refunds": 0,
        "suspicious": False
    },

    "CUST003": {
        "previous_refunds": 8,
        "suspicious": True
    },

    "CUST004": {
        "previous_refunds": 0,
        "suspicious": False
    }
}