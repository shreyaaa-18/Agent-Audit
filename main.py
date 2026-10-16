# main.py

"""
AgentAudit - unified entry point.

Lets you pick any of the four independently-built agents and run it
through a common interface. main.py only talks to core.agent_registry
and to the standardized result dict each agent returns - it has no
knowledge of any agent's tools, policies, or business rules.
"""

import sys

from core.agent_registry import get_agent, list_agents
from core.explain import explain_run
from core.storage import save_run
from core.anomaly import analyze_run


def print_banner():

    print()
    print("================================")
    print("       AGENTAUDIT SYSTEM")
    print("================================")
    print()
    print("Available Agents:")
    print()

    agents = list_agents()

    for i, (key, display_name) in enumerate(agents.items(), start=1):
        print(f"{i}. {display_name}")

    print()

    return agents


def choose_agent(agents):

    keys = list(agents.keys())

    while True:

        choice = input("Select an agent (number): ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(keys):
            return keys[int(choice) - 1]

        print("Invalid selection. Please enter a number from the list above.")
        print()


def print_trace(trace):

    print()
    print("================================")
    print("AGENTAUDIT TRACE")
    print("================================")

    print()
    print("Run ID:")
    print(trace["run_id"])

    print()
    print("Agent:")
    print(trace["agent_name"])

    print()
    print("Request:")
    print(trace["request"])

    print()
    print("Events:")

    for i, event in enumerate(trace["events"], start=1):

        print()
        print(f"Step {i}")
        print("------------------------------")

        if event["event_type"] == "tool_call":

            print("Type: Tool Call")

            print("Tool:")
            print(event["tool_name"])

            print("Input:")
            print(event["input"])

            print("Output:")
            print(event["output"])

            print("Duration:")
            print(f"{event['duration_seconds']} seconds")

        elif event["event_type"] == "llm_call":

            print("Type: LLM Call")

            print("Model:")
            print(event["model"])

            print("Content:")
            print(event["content"])

            print("Tools Requested:")
            print(event["tool_calls_requested"])

            print("Duration:")
            print(f"{event['duration_seconds']} seconds")

        else:

            print("Type: Unknown event")
            print(event)

    print()
    print("Final Decision:")
    print(trace["final_decision"]["decision"])

    print()
    print("Decision Reason:")
    print(trace["final_decision"]["reason"])


def run_once():

    agents = print_banner()

    agent_key = choose_agent(agents)

    print()
    print(f"Selected Agent: {agents[agent_key]}")
    print()

    request = input("Enter request: ").strip()

    if not request:
        print("No request entered. Exiting.")
        sys.exit(1)

    agent = get_agent(agent_key)

    result = agent.process_request(request)

    print()
    print("================================")
    print("FINAL AGENT RESULT")
    print("================================")

    print()
    print("Agent Name:")
    print(result["agent_name"])

    print()
    print("Decision:")
    print(result["decision"])

    print()
    print("Reason:")
    print(result["reason"])

    print()
    print("Status:")
    print(result["status"])

    print()
    print("Run ID:")
    print(result["run_id"])

    print_trace(result["trace"])

    saved_path = save_run(result["trace"])

    print()
    print(f"Run saved to: {saved_path}")

    print()
    print("================================")
    print("AGENTAUDIT ANALYSIS")
    print("================================")

    analysis = analyze_run(result["trace"])

    print()
    print(analysis["note"])

    if analysis["is_anomalous"]:

        print()
        print("FLAGGED AS ANOMALOUS:")

        for reason in analysis["reasons"]:
            print(f"- {reason}")

    else:

        print("No anomalies detected against this agent's history.")

    print()
    choice = input("Explain this decision in plain English? (y/n): ").strip().lower()

    if choice == "y":

        print()
        print("================================")
        print("AGENTAUDIT EXPLANATION")
        print("================================")
        print()

        explanation = explain_run(result["trace"])

        print(explanation)


if __name__ == "__main__":
    run_once()
