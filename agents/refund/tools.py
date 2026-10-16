# tools.py

from .data import orders, customer_history


def check_order(order_id):

    order = orders.get(order_id)

    if not order:
        return {
            "found": False,
            "message": f"Order {order_id} was not found."
        }

    return {
        "found": True,
        "order_id": order_id,
        "customer_id": order["customer_id"],
        "product": order["product"],
        "reason": order["reason"],
        "days_since_purchase": order["days_since_purchase"],
        "value": order["value"]
    }


def check_customer_history(customer_id):

    history = customer_history.get(customer_id)

    if not history:
        return {
            "found": False,
            "message": f"Customer {customer_id} was not found."
        }

    return {
        "found": True,
        "customer_id": customer_id,
        "previous_refunds": history["previous_refunds"],
        "suspicious": history["suspicious"]
    }


def check_order_value(value):

    HIGH_VALUE_THRESHOLD = 50000

    if value > HIGH_VALUE_THRESHOLD:
        return {
            "high_value": True,
            "threshold": HIGH_VALUE_THRESHOLD,
            "message": "Order is high-value and requires escalation."
        }

    return {
        "high_value": False,
        "threshold": HIGH_VALUE_THRESHOLD,
        "message": "Order is not considered high-value."
    }


def process_refund(order_id):

    return {
        "success": True,
        "order_id": order_id,
        "message": f"Refund processed successfully for {order_id}."
    }