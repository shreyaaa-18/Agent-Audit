# policy.py


def check_refund_policy(reason, days_since_purchase):

    if reason == "damaged" and days_since_purchase <= 30:
        return {
            "eligible": True,
            "reason": "Damaged products can be refunded within 30 days."
        }

    if reason == "wrong_product" and days_since_purchase <= 30:
        return {
            "eligible": True,
            "reason": "Wrong products can be refunded within 30 days."
        }

    if reason == "changed_mind" and days_since_purchase <= 7:
        return {
            "eligible": True,
            "reason": "Changed-mind refunds are allowed within 7 days."
        }

    return {
        "eligible": False,
        "reason": "The order does not satisfy the refund policy."
    }