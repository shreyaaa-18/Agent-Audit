# tools.py

from .data import expense_reports, employee_history


def check_expense_report(report_id):

    report = expense_reports.get(report_id)

    if not report:
        return {
            "found": False,
            "message": f"Expense report {report_id} was not found."
        }

    return {
        "found": True,
        "report_id": report_id,
        "employee_id": report["employee_id"],
        "category": report["category"],
        "description": report["description"],
        "days_since_expense": report["days_since_expense"],
        "amount": report["amount"],
        "has_receipt": report["has_receipt"]
    }


def check_employee_history(employee_id):

    history = employee_history.get(employee_id)

    if not history:
        return {
            "found": False,
            "message": f"Employee {employee_id} was not found."
        }

    return {
        "found": True,
        "employee_id": employee_id,
        "previous_claims": history["previous_claims"],
        "flagged": history["flagged"]
    }


def check_expense_value(amount):

    HIGH_VALUE_THRESHOLD = 10000

    if amount > HIGH_VALUE_THRESHOLD:
        return {
            "high_value": True,
            "threshold": HIGH_VALUE_THRESHOLD,
            "message": "Expense is high-value and requires escalation."
        }

    return {
        "high_value": False,
        "threshold": HIGH_VALUE_THRESHOLD,
        "message": "Expense is not considered high-value."
    }


def reimburse_expense(report_id):

    return {
        "success": True,
        "report_id": report_id,
        "message": f"Reimbursement processed successfully for {report_id}."
    }
