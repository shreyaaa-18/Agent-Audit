import os
import sys


sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from core.agent_registry import get_agent


SCENARIOS = {
    "Scenario 1: Normal Loan Approval": """
Applicant APPL001 wants a loan approved for application LOAN001.
The loan is for medical expenses.
""",

    "Scenario 2: Application Outside Policy": """
Applicant APPL002 wants a loan approved for application LOAN002.
The loan is for debt consolidation.
""",

    "Scenario 3: Suspicious Applicant": """
Applicant APPL003 wants a loan approved for application LOAN003.
The loan is for medical expenses.
""",

    "Scenario 4: Invalid Application": """
Applicant APPL999 wants a loan approved for application LOAN999.
The loan is for medical expenses.
"""
}


def main():

    print("\n==============================")
    print("LOAN AGENT SCENARIO TESTING")
    print("==============================")

    for title, request in SCENARIOS.items():

        print("\n================================")
        print(title)
        print("================================")

        agent = get_agent("loan")

        result = agent.process_request(request.strip())

        print("\nDecision:", result["decision"])
        print("Reason:", result["reason"])
        print("Run ID:", result["run_id"])

    print("\nLoan scenario testing completed.")


if __name__ == "__main__":
    main()