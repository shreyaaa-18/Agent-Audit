# core/explain.py

"""
The Explanation layer.

Turns an AgentAudit trace and its analysis into a
plain-English explanation for a human reviewer.

Two cases are supported:

1. Normal run
   Explains how the agent reached its decision.

2. Anomalous run
   Explains:
       - what the agent decided
       - what tools it actually used
       - the typical tool sequence
       - which tools were missing
       - which tools were unexpected
       - the historical evidence
       - the agent's stated reason
"""


def _get_tool_events(trace):
    """
    Return only tool-call events from the trace.
    """

    return [
        event
        for event in trace.get("events", [])
        if event.get("event_type") == "tool_call"
    ]


def _describe_tool_event(event):
    """
    Convert a tool event into a short human-readable sentence.
    """

    tool_name = event.get("tool_name")
    output = event.get("output", {})

    if tool_name == "check_order":

        if output.get("exists") is True:
            return "The agent verified that the order exists."

        if output.get("exists") is False:
            return "The agent verified that the order does not exist."

    if tool_name == "check_refund_policy":

        if output.get("eligible") is True:
            return (
                "The agent verified that the refund satisfies "
                "the refund policy."
            )

        if output.get("eligible") is False:

            reason = output.get("reason")

            if reason:
                return (
                    "The agent checked the refund policy and found "
                    "that the request was not eligible "
                    f"({reason})."
                )

            return (
                "The agent checked the refund policy and found "
                "that the request was not eligible."
            )

    if tool_name == "check_customer_history":

        if output.get("flagged") is True:
            return (
                "The agent reviewed the customer's refund history "
                "and found a flag requiring further review."
            )

        return (
            "The agent reviewed the customer's refund history."
        )

    return (
        f"The agent called {tool_name} and received "
        "the recorded result."
    )


def _build_normal_explanation(trace):
    """
    Explain a normal run using the recorded tool calls.
    """

    decision = trace["final_decision"]["decision"]
    reason = trace["final_decision"]["reason"]

    tool_events = _get_tool_events(trace)

    explanation_parts = []

    for event in tool_events:

        explanation_parts.append(
            _describe_tool_event(event)
        )

    if explanation_parts:

        explanation = " ".join(
            explanation_parts
        )

        explanation += (
            f" Based on these checks, the agent reached "
            f"the decision '{decision}'."
        )

        return explanation

    return (
        f"The agent reached the decision '{decision}'. "
        f"The recorded reason was: {reason}"
    )


def _build_anomaly_explanation(trace, analysis):
    """
    Explain an anomalous run using structured anomaly evidence.
    """

    decision = trace["final_decision"]["decision"]

    observed_sequence = analysis.get(
        "observed_sequence",
        []
    )

    typical_sequence = analysis.get(
        "typical_sequence",
        []
    )

    missing_tools = analysis.get(
        "missing_tools",
        []
    )

    unexpected_tools = analysis.get(
        "unexpected_tools",
        []
    )

    tool_frequencies = analysis.get(
        "tool_frequencies",
        {}
    )

    # ---------------------------------------------------------
    # Observed sequence
    # ---------------------------------------------------------

    if observed_sequence:

        observed_path = " → ".join(
            observed_sequence
        )

        observed_path += f" → {decision}"

    else:
        observed_path = decision

    # ---------------------------------------------------------
    # Typical sequence
    # ---------------------------------------------------------

    if typical_sequence:

        typical_path = " → ".join(
            typical_sequence
        )

        typical_path += f" → {decision}"

    else:

        typical_path = (
            "No typical sequence established."
        )

    # ---------------------------------------------------------
    # Missing tools
    # ---------------------------------------------------------

    if missing_tools:

        missing_text = ", ".join(
            missing_tools
        )

    else:

        missing_text = "None"

    # ---------------------------------------------------------
    # Build explanation
    # ---------------------------------------------------------

    lines = [

        f"Decision: {decision}",

        "",

        "Audit finding:",
        "ANOMALY DETECTED",

        "",

        "Observed behavior:",
        observed_path,

        "",

        "Typical behavior for this decision:",
        typical_path,

        "",

        "Missing tool(s):",
        missing_text,

        "",

        "Why AgentAudit flagged this:"

    ]

    # ---------------------------------------------------------
    # Historical evidence for missing tools
    # ---------------------------------------------------------

    for tool in missing_tools:

        frequency = tool_frequencies.get(
            tool,
            0
        )

        lines.append(
            f"- {tool} appears in "
            f"{frequency:.0%} of historical "
            f"'{decision}' runs, but this run did not call it."
        )

    # ---------------------------------------------------------
    # Historical evidence for unexpected tools
    # ---------------------------------------------------------

    for tool in unexpected_tools:

        lines.append(
            f"- {tool} was called in this run, but it is not "
            f"typical of historical '{decision}' runs."
        )

    # ---------------------------------------------------------
    # Agent's own explanation
    # ---------------------------------------------------------

    lines.extend([

        "",

        "Agent's stated reason:",

        trace["final_decision"]["reason"]

    ])

    return "\n".join(lines)


def explain_run(trace, analysis=None):
    """
    Generate a human-readable explanation for a completed run.
    """

    if analysis is None:

        analysis = {
            "is_anomalous": False,
            "reasons": []
        }

    if analysis.get("is_anomalous"):

        return _build_anomaly_explanation(
            trace,
            analysis
        )

    return _build_normal_explanation(
        trace
    )