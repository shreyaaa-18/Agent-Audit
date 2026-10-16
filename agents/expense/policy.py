# policy.py


def check_expense_policy(category, days_since_expense, has_receipt):

    if not has_receipt:
        return {
            "eligible": False,
            "reason": "A receipt is required for reimbursement."
        }

    if category == "travel" and days_since_expense <= 60:
        return {
            "eligible": True,
            "reason": "Travel expenses can be claimed within 60 days."
        }

    if category == "meals" and days_since_expense <= 30:
        return {
            "eligible": True,
            "reason": "Meal expenses can be claimed within 30 days."
        }

    if category == "office_supplies" and days_since_expense <= 45:
        return {
            "eligible": True,
            "reason": "Office supply expenses can be claimed within 45 days."
        }

    if category == "client_entertainment" and days_since_expense <= 30:
        return {
            "eligible": True,
            "reason": "Client entertainment expenses can be claimed within 30 days."
        }

    return {
        "eligible": False,
        "reason": "The expense does not satisfy the reimbursement policy."
    }
