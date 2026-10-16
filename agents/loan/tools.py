# tools.py

from .data import loan_applications, applicant_history


def check_loan_application(loan_id):

    application = loan_applications.get(loan_id)

    if not application:
        return {
            "found": False,
            "message": f"Loan application {loan_id} was not found."
        }

    return {
        "found": True,
        "loan_id": loan_id,
        "applicant_id": application["applicant_id"],
        "loan_type": application["loan_type"],
        "purpose": application["purpose"],
        "credit_score": application["credit_score"],
        "amount": application["amount"]
    }


def check_applicant_history(applicant_id):

    history = applicant_history.get(applicant_id)

    if not history:
        return {
            "found": False,
            "message": f"Applicant {applicant_id} was not found."
        }

    return {
        "found": True,
        "applicant_id": applicant_id,
        "previous_loans": history["previous_loans"],
        "suspicious": history["suspicious"]
    }


def check_loan_amount(amount):

    HIGH_VALUE_THRESHOLD = 1000000

    if amount > HIGH_VALUE_THRESHOLD:
        return {
            "high_value": True,
            "threshold": HIGH_VALUE_THRESHOLD,
            "message": "Loan amount is high-value and requires escalation."
        }

    return {
        "high_value": False,
        "threshold": HIGH_VALUE_THRESHOLD,
        "message": "Loan amount is not considered high-value."
    }


def process_loan_approval(loan_id):

    return {
        "success": True,
        "loan_id": loan_id,
        "message": f"Loan approved and processed successfully for {loan_id}."
    }
