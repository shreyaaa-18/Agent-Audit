# policy.py


def check_loan_policy(purpose, credit_score):

    if purpose == "medical_expenses" and credit_score >= 650:
        return {
            "eligible": True,
            "reason": "Medical-expense loans are approved for credit scores of 650 or higher."
        }

    if purpose == "education" and credit_score >= 650:
        return {
            "eligible": True,
            "reason": "Education loans are approved for credit scores of 650 or higher."
        }

    if purpose == "debt_consolidation" and credit_score >= 700:
        return {
            "eligible": True,
            "reason": "Debt-consolidation loans are approved for credit scores of 700 or higher."
        }

    return {
        "eligible": False,
        "reason": "The application does not satisfy the loan approval policy."
    }
