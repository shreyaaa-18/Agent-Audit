# core/audit.py

from core.storage import save_run, save_audit_result
from core.anomaly import analyze_run
from core.explain import explain_run


def audit_run(trace, use_llm=False):
    """
    Save a completed trace, analyze it for anomalies,
    persist the audit result, and generate a human-readable
    explanation.

    The core explanation is deterministic and does not require
    an external LLM API.
    """

    file_path = save_run(trace)

    analysis = analyze_run(trace)

    # Persist the audit result so future analysis can distinguish
    # normal historical runs from previously flagged anomalies.
    save_audit_result(
        trace["agent_name"],
        trace["run_id"],
        analysis
    )

    explanation = explain_run(
        trace,
        analysis
    )

    return {
        "run_id": trace["run_id"],
        "agent_name": trace["agent_name"],
        "file_path": file_path,
        "analysis": analysis,
        "explanation": explanation,
    }


def print_audit_report(report):
    """
    Display the audit result in a readable format.
    """

    analysis = report["analysis"]

    print("\n" + "=" * 60)
    print("AGENTAUDIT REPORT")
    print("=" * 60)

    print(f"Agent: {report['agent_name']}")
    print(f"Run ID: {report['run_id']}")
    print(f"Trace saved at: {report['file_path']}")

    print("\nANOMALY ANALYSIS")
    print("-" * 60)

    print(f"Anomalous: {analysis['is_anomalous']}")
    print(f"Note: {analysis['note']}")

    if analysis["reasons"]:

        print("Reasons:")

        for reason in analysis["reasons"]:
            print(f"- {reason}")

    else:

        print("No anomaly reasons detected.")

    print("\nEXPLANATION")
    print("-" * 60)
    print(report["explanation"])

    print("=" * 60)