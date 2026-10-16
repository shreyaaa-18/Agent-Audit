# policy.py

MAX_AMOUNT_INCLUDING_TAXES = 8000


def check_travel_policy(base_fare, taxes):

    total_fare = base_fare + taxes

    if total_fare <= MAX_AMOUNT_INCLUDING_TAXES:
        return {
            "eligible": True,
            "total_fare": total_fare,
            "reason": f"Total fare (base fare + taxes) of {total_fare} is within the {MAX_AMOUNT_INCLUDING_TAXES} budget cap."
        }

    return {
        "eligible": False,
        "total_fare": total_fare,
        "reason": f"Total fare (base fare + taxes) of {total_fare} exceeds the {MAX_AMOUNT_INCLUDING_TAXES} budget cap."
    }
