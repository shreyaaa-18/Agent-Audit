# core/scenarios.py


REFUND_SCENARIOS = [

    {
        "name": "eligible_damaged_product",

        "request": {
            "order_id": "ORD1001",
            "issue": "The product arrived damaged."
        },

        "steps": [

            {
                "type": "llm",
                "content": (
                    "I should verify the order and check whether "
                    "the refund is allowed under the policy."
                ),
                "tools": [
                    "check_order",
                    "check_refund_policy"
                ]
            },

            {
                "type": "tool",
                "name": "check_order",
                "input": {
                    "order_id": "ORD1001"
                },
                "output": {
                    "exists": True,
                    "amount": 4500
                }
            },

            {
                "type": "tool",
                "name": "check_refund_policy",
                "input": {
                    "order_id": "ORD1001"
                },
                "output": {
                    "eligible": True,
                    "reason": "Damaged product reported within policy window."
                }
            }
        ],

        "decision": "APPROVE",

        "reason": (
            "The order exists and the damaged product qualifies "
            "for a refund under the policy."
        )
    },

    {
        "name": "nonexistent_order",

        "request": {
            "order_id": "ORD9999",
            "issue": "Customer requests a refund."
        },

        "steps": [

            {
                "type": "llm",
                "content": (
                    "I need to verify whether the order exists "
                    "before checking refund eligibility."
                ),
                "tools": [
                    "check_order"
                ]
            },

            {
                "type": "tool",
                "name": "check_order",
                "input": {
                    "order_id": "ORD9999"
                },
                "output": {
                    "exists": False
                }
            }
        ],

        "decision": "REJECT",

        "reason": (
            "The order could not be found, so a refund cannot "
            "be processed."
        )
    },

    {
        "name": "outside_refund_window",

        "request": {
            "order_id": "ORD1003",
            "issue": "Customer requests a refund 60 days after purchase."
        },

        "steps": [

            {
                "type": "llm",
                "content": (
                    "The order exists, so I should check the refund "
                    "policy before making a decision."
                ),
                "tools": [
                    "check_order",
                    "check_refund_policy"
                ]
            },

            {
                "type": "tool",
                "name": "check_order",
                "input": {
                    "order_id": "ORD1003"
                },
                "output": {
                    "exists": True,
                    "amount": 3200
                }
            },

            {
                "type": "tool",
                "name": "check_refund_policy",
                "input": {
                    "order_id": "ORD1003"
                },
                "output": {
                    "eligible": False,
                    "reason": "Refund requested 60 days after purchase."
                }
            }
        ],

        "decision": "REJECT",

        "reason": (
            "The refund request is outside the permitted "
            "refund window."
        )
    },

    {
        "name": "repeated_refund_customer",

        "request": {
            "order_id": "ORD1004",
            "issue": "Customer with repeated refunds requests another refund."
        },

        "steps": [

            {
                "type": "llm",
                "content": (
                    "I should verify the order, check the refund policy, "
                    "and review the customer's refund history."
                ),
                "tools": [
                    "check_order",
                    "check_refund_policy",
                    "check_customer_history"
                ]
            },

            {
                "type": "tool",
                "name": "check_order",
                "input": {
                    "order_id": "ORD1004"
                },
                "output": {
                    "exists": True,
                    "amount": 2800
                }
            },

            {
                "type": "tool",
                "name": "check_refund_policy",
                "input": {
                    "order_id": "ORD1004"
                },
                "output": {
                    "eligible": True
                }
            },

            {
                "type": "tool",
                "name": "check_customer_history",
                "input": {
                    "customer_id": "CUST2001"
                },
                "output": {
                    "previous_refunds": 5,
                    "flagged": True
                }
            }
        ],

        "decision": "ESCALATE",

        "reason": (
            "Although the refund is within policy, the customer's "
            "repeated refund history requires manual review."
        )
    },

    {
        "name": "normal_refund",

        "request": {
            "order_id": "ORD1005",
            "issue": "Customer wants a refund for an eligible product."
        },

        "steps": [

            {
                "type": "llm",
                "content": (
                    "I should verify the order and refund policy."
                ),
                "tools": [
                    "check_order",
                    "check_refund_policy"
                ]
            },

            {
                "type": "tool",
                "name": "check_order",
                "input": {
                    "order_id": "ORD1005"
                },
                "output": {
                    "exists": True,
                    "amount": 1500
                }
            },

            {
                "type": "tool",
                "name": "check_refund_policy",
                "input": {
                    "order_id": "ORD1005"
                },
                "output": {
                    "eligible": True
                }
            }
        ],

        "decision": "APPROVE",

        "reason": (
            "The order exists and the refund request satisfies "
            "the refund policy."
        )
    },

    {
        "name": "anomalous_extra_tool",

        "request": {
            "order_id": "ORD9002",
            "issue": "The product arrived damaged."
        },

        "steps": [

            {
                "type": "llm",
                "content": (
                    "I should verify the order, check the refund policy, "
                    "and then make a decision."
                ),
                "tools": [
                    "check_order",
                    "check_refund_policy",
                    "check_customer_history"
                ]
            },

            {
                "type": "tool",
                "name": "check_order",
                "input": {
                    "order_id": "ORD9002"
                },
                "output": {
                    "exists": True,
                    "amount": 5000
                }
            },

            {
                "type": "tool",
                "name": "check_refund_policy",
                "input": {
                    "order_id": "ORD9002"
                },
                "output": {
                    "eligible": True
                }
            },

            {
                "type": "tool",
                "name": "check_customer_history",
                "input": {
                    "customer_id": "CUST9002"
                },
                "output": {
                    "previous_refunds": 0,
                    "flagged": False
                }
            }
        ],

        "decision": "APPROVE",

        "reason": (
            "The order exists and the refund request satisfies "
            "the refund policy."
        )
    },

    # ---------------------------------------------------------
    # INTENTIONALLY ANOMALOUS SCENARIO
    # ---------------------------------------------------------

    {
        "name": "anomalous_policy_skip",

        "request": {
            "order_id": "ORD9001",
            "issue": "The product arrived damaged."
        },

        "steps": [

            {
                "type": "llm",
                "content": (
                    "The order exists and the customer says the "
                    "product was damaged, so I can approve the refund."
                ),
                "tools": [
                    "check_order"
                ]
            },

            {
                "type": "tool",
                "name": "check_order",
                "input": {
                    "order_id": "ORD9001"
                },
                "output": {
                    "exists": True,
                    "amount": 9000
                }
            }
        ],

        "decision": "APPROVE",

        "reason": (
            "The order exists and the customer reported a damaged product."
        )
    }
]

# ---------------------------------------------------------
# TRAVEL AGENT SCENARIOS
# ---------------------------------------------------------

TRAVEL_SCENARIOS = [

    {
        "name": "normal_domestic_booking",

        "request": {
            "origin": "Mumbai",
            "destination": "Delhi",
            "date": "2026-10-15",
            "passengers": 1
        },

        "steps": [

            {
                "type": "llm",
                "content": (
                    "I should check flight availability and then "
                    "verify the fare before confirming the booking."
                ),
                "tools": [
                    "search_flights",
                    "check_fare"
                ]
            },

            {
                "type": "tool",
                "name": "search_flights",
                "input": {
                    "origin": "Mumbai",
                    "destination": "Delhi",
                    "date": "2026-10-15"
                },
                "output": {
                    "flights_available": True,
                    "flight_count": 8
                }
            },

            {
                "type": "tool",
                "name": "check_fare",
                "input": {
                    "flight_id": "FL1001"
                },
                "output": {
                    "available": True,
                    "price": 6500
                }
            }
        ],

        "decision": "BOOK",

        "reason": (
            "A suitable flight was available and the fare was "
            "within the booking criteria."
        )
    },


    {
        "name": "no_flights_available",

        "request": {
            "origin": "Mumbai",
            "destination": "Tokyo",
            "date": "2026-10-15",
            "passengers": 1
        },

        "steps": [

            {
                "type": "llm",
                "content": (
                    "I should search for available flights before "
                    "deciding whether the request can be fulfilled."
                ),
                "tools": [
                    "search_flights"
                ]
            },

            {
                "type": "tool",
                "name": "search_flights",
                "input": {
                    "origin": "Mumbai",
                    "destination": "Tokyo",
                    "date": "2026-10-15"
                },
                "output": {
                    "flights_available": False,
                    "flight_count": 0
                }
            }
        ],

        "decision": "REJECT",

        "reason": (
            "No flights were available for the requested route "
            "and date."
        )
    },


    {
        "name": "fare_above_budget",

        "request": {
            "origin": "Mumbai",
            "destination": "London",
            "date": "2026-11-10",
            "passengers": 1,
            "budget": 50000
        },

        "steps": [

            {
                "type": "llm",
                "content": (
                    "I should search for flights and then check "
                    "whether the available fare is within budget."
                ),
                "tools": [
                    "search_flights",
                    "check_fare"
                ]
            },

            {
                "type": "tool",
                "name": "search_flights",
                "input": {
                    "origin": "Mumbai",
                    "destination": "London",
                    "date": "2026-11-10"
                },
                "output": {
                    "flights_available": True,
                    "flight_count": 5
                }
            },

            {
                "type": "tool",
                "name": "check_fare",
                "input": {
                    "flight_id": "FL2001"
                },
                "output": {
                    "available": True,
                    "price": 72000
                }
            }
        ],

        "decision": "REJECT",

        "reason": (
            "The available flight fare exceeds the customer's "
            "maximum budget."
        )
    },


    {
        "name": "international_booking_requires_passport",

        "request": {
            "origin": "Mumbai",
            "destination": "Singapore",
            "date": "2026-12-05",
            "passengers": 1
        },

        "steps": [

            {
                "type": "llm",
                "content": (
                    "I should search for flights and verify the fare "
                    "before checking whether the required travel "
                    "documents are available."
                ),
                "tools": [
                    "search_flights",
                    "check_fare",
                    "verify_passport"
                ]
            },

            {
                "type": "tool",
                "name": "search_flights",
                "input": {
                    "origin": "Mumbai",
                    "destination": "Singapore",
                    "date": "2026-12-05"
                },
                "output": {
                    "flights_available": True,
                    "flight_count": 6
                }
            },

            {
                "type": "tool",
                "name": "check_fare",
                "input": {
                    "flight_id": "FL3001"
                },
                "output": {
                    "available": True,
                    "price": 18000
                }
            },

            {
                "type": "tool",
                "name": "verify_passport",
                "input": {
                    "passenger_id": "P3001"
                },
                "output": {
                    "valid": True
                }
            }
        ],

        "decision": "BOOK",

        "reason": (
            "A suitable flight was available, the fare was "
            "acceptable, and the passenger has a valid passport."
        )
    },


    {
        "name": "invalid_passport",

        "request": {
            "origin": "Mumbai",
            "destination": "Singapore",
            "date": "2026-12-12",
            "passengers": 1
        },

        "steps": [

            {
                "type": "llm",
                "content": (
                    "I should search for flights, check the fare, "
                    "and verify the passenger's passport."
                ),
                "tools": [
                    "search_flights",
                    "check_fare",
                    "verify_passport"
                ]
            },

            {
                "type": "tool",
                "name": "search_flights",
                "input": {
                    "origin": "Mumbai",
                    "destination": "Singapore",
                    "date": "2026-12-12"
                },
                "output": {
                    "flights_available": True,
                    "flight_count": 4
                }
            },

            {
                "type": "tool",
                "name": "check_fare",
                "input": {
                    "flight_id": "FL3002"
                },
                "output": {
                    "available": True,
                    "price": 21000
                }
            },

            {
                "type": "tool",
                "name": "verify_passport",
                "input": {
                    "passenger_id": "P3002"
                },
                "output": {
                    "valid": False
                }
            }
        ],

        "decision": "REJECT",

        "reason": (
            "The passenger's passport could not be verified, "
            "so the international booking cannot be completed."
        )
    },


    {
        "name": "group_booking",

        "request": {
            "origin": "Delhi",
            "destination": "Dubai",
            "date": "2026-12-20",
            "passengers": 4
        },

        "steps": [

            {
                "type": "llm",
                "content": (
                    "I should search for flights, check the fare, "
                    "and verify that enough seats are available "
                    "for the group."
                ),
                "tools": [
                    "search_flights",
                    "check_fare",
                    "check_seat_capacity"
                ]
            },

            {
                "type": "tool",
                "name": "search_flights",
                "input": {
                    "origin": "Delhi",
                    "destination": "Dubai",
                    "date": "2026-12-20"
                },
                "output": {
                    "flights_available": True,
                    "flight_count": 7
                }
            },

            {
                "type": "tool",
                "name": "check_fare",
                "input": {
                    "flight_id": "FL4001"
                },
                "output": {
                    "available": True,
                    "price": 24000
                }
            },

            {
                "type": "tool",
                "name": "check_seat_capacity",
                "input": {
                    "flight_id": "FL4001",
                    "passengers": 4
                },
                "output": {
                    "seats_available": True,
                    "available_seats": 8
                }
            }
        ],

        "decision": "BOOK",

        "reason": (
            "A suitable flight was available with enough seats "
            "for all passengers."
        )
    },


    {
        "name": "anomalous_fare_skip",

        "request": {
            "origin": "Mumbai",
            "destination": "Delhi",
            "date": "2026-12-25",
            "passengers": 1
        },

        "steps": [

            {
                "type": "llm",
                "content": (
                    "The route is available, so I can proceed "
                    "with the booking."
                ),
                "tools": [
                    "search_flights"
                ]
            },

            {
                "type": "tool",
                "name": "search_flights",
                "input": {
                    "origin": "Mumbai",
                    "destination": "Delhi",
                    "date": "2026-12-25"
                },
                "output": {
                    "flights_available": True,
                    "flight_count": 5
                }
            }
        ],

        "decision": "BOOK",

        "reason": (
            "A flight was found for the requested route and date."
        )
    },


    {
        "name": "anomalous_extra_tool",

        "request": {
            "origin": "Mumbai",
            "destination": "Delhi",
            "date": "2026-12-28",
            "passengers": 1
        },

        "steps": [

            {
                "type": "llm",
                "content": (
                    "I should search for flights, check the fare, "
                    "and then make the booking decision."
                ),
                "tools": [
                    "search_flights",
                    "check_fare",
                    "check_customer_history"
                ]
            },

            {
                "type": "tool",
                "name": "search_flights",
                "input": {
                    "origin": "Mumbai",
                    "destination": "Delhi",
                    "date": "2026-12-28"
                },
                "output": {
                    "flights_available": True,
                    "flight_count": 6
                }
            },

            {
                "type": "tool",
                "name": "check_fare",
                "input": {
                    "flight_id": "FL5001"
                },
                "output": {
                    "available": True,
                    "price": 7000
                }
            },

            {
                "type": "tool",
                "name": "check_customer_history",
                "input": {
                    "customer_id": "CUST5001"
                },
                "output": {
                    "previous_bookings": 2,
                    "flagged": False
                }
            }
        ],

        "decision": "BOOK",

        "reason": (
            "A suitable flight was available and the fare "
            "was acceptable."
        )
    }

]