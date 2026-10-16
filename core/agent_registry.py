# core/agent_registry.py

"""
Central registry for all AgentAudit agents.

Each agent lives in its own isolated package under agents/<name>/
and exposes a class with a process_request(request) method plus a
self.tracer (AgentTracer) attribute. This registry is the only place
that knows how to import and instantiate each one - main.py never
needs to import an agent class directly.

Adding a fifth agent later means adding one entry here, not touching
main.py at all.
"""

from importlib import import_module


# module path -> class name -> human-readable label shown in the menu
_AGENTS = {
    "refund": {
        "module": "agents.refund.agent",
        "class_name": "RefundAgent",
        "display_name": "Refund Agent",
    },
    "travel": {
        "module": "agents.travel.agent",
        "class_name": "TravelAgent",
        "display_name": "Travel Agent",
    },
    "loan": {
        "module": "agents.loan.agent",
        "class_name": "LoanApprovalAgent",
        "display_name": "Loan Approval Agent",
    },
    "expense": {
        "module": "agents.expense.agent",
        "class_name": "ExpenseAgent",
        "display_name": "Expense Agent",
    },
}


def list_agents():
    """
    Return {key: display_name} for every registered agent, in
    registration order. Used to build the main.py menu.
    """

    return {key: meta["display_name"] for key, meta in _AGENTS.items()}


def get_agent(key):
    """
    Instantiate and return the agent registered under `key`.

    Raises ValueError with the list of valid keys if `key` is not
    registered, instead of a bare KeyError/ImportError.
    """

    if key not in _AGENTS:
        valid = ", ".join(_AGENTS.keys())
        raise ValueError(
            f"Unknown agent '{key}'. Available agents: {valid}"
        )

    meta = _AGENTS[key]

    module = import_module(meta["module"])

    agent_class = getattr(module, meta["class_name"])

    return agent_class()
