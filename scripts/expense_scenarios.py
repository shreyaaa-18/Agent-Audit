# scripts/expense_scenarios.py

"""
Runs the Expense agent against the five demo scenarios that used to
live in separate main_scenarioN_*.py files in the original
ExpenseAudit project. Kept as one script for a quick regression check
after making changes to the expense agent, its tools, or its policy.

Run from the AgentAudit/ project root:

    python scripts/expense_scenarios.py
"""

import os
import sys

# Allow running this script directly (adds the project root to the
# import path so "core" and "agents" resolve the same way they do
# when main.py is run from the project root).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.agent_registry import get_agent


SCENARIOS = {
    "Scenario 1: Normal Reimbursement": """
Employee EMP001 submitted expense report EXP001.
It is a travel expense for a client onsite visit.
""",
    "Scenario 2: Expense Submitted Too Late": """
Employee EMP002 submitted expense report EXP002.
It is a meal expense from a team dinner.
""",
    "Scenario 3: Flagged Employee": """
Employee EMP003 submitted expense report EXP003.
It is a client entertainment expense.
""",
    "Scenario 4: High-Value Eligible Expense": """
Employee EMP002 submitted expense report EXP005.
It is a travel expense for a regional conference.
""",
    "Scenario 5: Missing Receipt": """
Employee EMP004 submitted expense report EXP004.
It is an office supplies purchase.
""",
}


def main():

    for title, request in SCENARIOS.items():

        print()
        print("================================")
        print(title)
        print("================================")

        agent = get_agent("expense")

        result = agent.process_request(request.strip())

        print()
        print("Decision:", result["decision"])
        print("Reason:", result["reason"])
        print("Run ID:", result["run_id"])


if __name__ == "__main__":
    main()
